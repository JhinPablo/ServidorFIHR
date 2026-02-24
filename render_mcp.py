# ===============================================
# RENDER MCP - Interacción con Render API
# ===============================================

import requests
import os
from typing import Dict, List, Optional
from datetime import datetime

class RenderMCP:
    """Cliente para Render API - MCP Server Integration"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("RENDER_API_KEY")
        self.base_url = "https://api.render.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        if not self.api_key:
            raise ValueError("RENDER_API_KEY no configurada")
    
    def get_services(self) -> List[Dict]:
        """Obtener lista de servicios"""
        response = requests.get(
            f"{self.base_url}/services",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def get_service_by_name(self, service_name: str) -> Dict:
        """Obtener un servicio por nombre"""
        services = self.get_services()
        for service in services:
            if service.get("name") == service_name:
                return service
        raise ValueError(f"Servicio '{service_name}' no encontrado")
    
    def get_service_status(self, service_id: str) -> Dict:
        """Obtener estado del servicio"""
        response = requests.get(
            f"{self.base_url}/services/{service_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def get_service_logs(self, service_id: str, limit: int = 100) -> str:
        """Obtener logs del servicio"""
        response = requests.get(
            f"{self.base_url}/services/{service_id}/logs?limit={limit}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.text
    
    def get_environment_variables(self, service_id: str) -> List[Dict]:
        """Obtener variables de entorno del servicio"""
        response = requests.get(
            f"{self.base_url}/services/{service_id}/env-vars",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def update_environment_variable(
        self, 
        service_id: str, 
        key: str, 
        value: str
    ) -> Dict:
        """Actualizar variable de entorno"""
        data = {"key": key, "value": value}
        response = requests.put(
            f"{self.base_url}/services/{service_id}/env-vars/{key}",
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    def trigger_deploy(self, service_id: str) -> Dict:
        """Triggear un nuevo deploy"""
        response = requests.post(
            f"{self.base_url}/services/{service_id}/deploys",
            headers=self.headers,
            json={"cleaBuildCache": False}
        )
        response.raise_for_status()
        return response.json()
    
    def get_deploy_status(self, service_id: str, deploy_id: str) -> Dict:
        """Obtener estado de un deploy"""
        response = requests.get(
            f"{self.base_url}/services/{service_id}/deploys/{deploy_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def get_databases(self) -> List[Dict]:
        """Obtener lista de bases de datos"""
        response = requests.get(
            f"{self.base_url}/postgres",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def get_database_status(self, db_id: str) -> Dict:
        """Obtener estado de la base de datos"""
        response = requests.get(
            f"{self.base_url}/postgres/{db_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()


# ===============================================
# HELPER FUNCTIONS
# ===============================================

def get_service_info(service_name: str = "ServidorFIHR") -> Dict:
    """Obtener información completa del servicio"""
    mcp = RenderMCP()
    service = mcp.get_service_by_name(service_name)
    status = mcp.get_service_status(service["id"])
    
    return {
        "name": service["name"],
        "id": service["id"],
        "status": status.get("status"),
        "url": status.get("serviceDetails", {}).get("url"),
        "createdAt": status.get("createdAt"),
        "updatedAt": status.get("updatedAt"),
        "buildStatus": status.get("status")
    }

def redeploy_service(service_name: str = "ServidorFIHR") -> Dict:
    """Triggear redeploy del servicio"""
    mcp = RenderMCP()
    service = mcp.get_service_by_name(service_name)
    deploy = mcp.trigger_deploy(service["id"])
    
    return {
        "message": f"Deploy iniciado para {service_name}",
        "deployId": deploy.get("id"),
        "status": deploy.get("status"),
        "createdAt": deploy.get("createdAt")
    }

def watch_deploy(service_name: str = "ServidorFIHR", max_attempts: int = 60) -> Dict:
    """Monitorear un deploy en tiempo real"""
    import time
    
    mcp = RenderMCP()
    service = mcp.get_service_by_name(service_name)
    service_status = mcp.get_service_status(service["id"])
    
    current_deploy = service_status.get("currentDeploy")
    if not current_deploy:
        return {"error": "No hay despliegue en progreso"}
    
    deploy_id = current_deploy.get("id")
    
    print(f"🚀 Monitoreando deploy de {service_name}...")
    print(f"Deploy ID: {deploy_id}\n")
    
    for attempt in range(max_attempts):
        deploy_status = mcp.get_deploy_status(service["id"], deploy_id)
        status = deploy_status.get("status")
        
        print(f"[{attempt+1}/{max_attempts}] Status: {status}")
        
        if status in ["LIVE", "SUCCESS"]:
            return {
                "message": "✅ Deploy completado exitosamente",
                "status": status,
                "finishedAt": deploy_status.get("finishedAt")
            }
        elif status in ["BUILD_FAILED", "DEPLOY_FAILED"]:
            return {
                "error": f"❌ Error en deploy: {status}",
                "logs": mcp.get_service_logs(service["id"])
            }
        
        time.sleep(5)
    
    return {"message": "⏱️ Timeout esperando deploy"}

def get_env_vars(service_name: str = "ServidorFIHR") -> List[Dict]:
    """Obtener variables de entorno del servicio"""
    mcp = RenderMCP()
    service = mcp.get_service_by_name(service_name)
    return mcp.get_environment_variables(service["id"])

def update_env_var(key: str, value: str, service_name: str = "ServidorFIHR") -> Dict:
    """Actualizar variable de entorno"""
    mcp = RenderMCP()
    service = mcp.get_service_by_name(service_name)
    return mcp.update_environment_variable(service["id"], key, value)


if __name__ == "__main__":
    # Test
    info = get_service_info()
    print("📊 Service Info:")
    print(info)
