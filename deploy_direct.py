#!/usr/bin/env python3
import os
import json
import requests
import time

api_key = os.getenv("RENDER_API_KEY")
if not api_key:
    print("ERROR: RENDER_API_KEY no configurada")
    exit(1)

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

print("[*] Inicilizando deploy...\n")

try:
    # Obtener servicios
    print("[*] Obteniendo servicios...")
    response = requests.get(
        "https://api.render.com/v1/services",
        headers=headers
    )
    response.raise_for_status()
    
    data = response.json()
    if not isinstance(data, list) or not data:
        print("[!] No hay servicios disponibles")
        exit(1)
    
    # Extraer primer servicio
    service_data = data[0].get('service', {})
    service_id = service_data.get('id')
    service_name = service_data.get('name')
    
    if not service_id:
        print("[!] No se encontro ID de servicio")
        exit(1)
    
    print(f"[+] Servicio: {service_name}")
    print(f"    ID: {service_id}")
    print(f"    URL: {service_data.get('serviceDetails', {}).get('url')}\n")
    
    # Triggear deploy
    print("[*] Triggereando deploy...")
    deploy_response = requests.post(
        f"https://api.render.com/v1/services/{service_id}/deploys",
        headers=headers,
        json={"cleaBuildCache": False}
    )
    
    if deploy_response.status_code != 201:
        print(f"[!] Error al triggear deploy: {deploy_response.status_code}")
        print(f"Response: {deploy_response.text}")
        exit(1)
    
    deploy_data = deploy_response.json()
    deploy_id = deploy_data.get('id')
    
    print(f"[+] Deploy triggereado")
    print(f"    ID: {deploy_id}\n")
    
    # Monitorear deploy
    print("[*] Monitoreando deploy (timeout: 10 minutos)...\n")
    
    for attempt in range(120):
        status_response = requests.get(
            f"https://api.render.com/v1/services/{service_id}/deploys/{deploy_id}",
            headers=headers
        )
        status_response.raise_for_status()
        
        deploy_status = status_response.json()
        status = deploy_status.get('status')
        
        print(f"[{attempt+1:03}/120] Status: {status:<20} | CreatedAt: {deploy_status.get('createdAt', '')[:19]}")
        
        if status in ["LIVE", "SUCCESS"]:
            print(f"\n[+] Deploy completado exitosamente!")
            print(f"    URL: {service_data.get('serviceDetails', {}).get('url')}")
            break
        elif status in ["BUILD_FAILED", "DEPLOY_FAILED"]:
            print(f"\n[!] Error en deploy: {status}\n")
            print("[*] Obteniendo logs de error...\n")
            
            # Obtener logs
            logs_response = requests.get(
                f"https://api.render.com/v1/services/{service_id}/logs",
                headers=headers
            )
            if logs_response.status_code == 200:
                print(logs_response.text[-2000:])  # Ultimas 2000 caracteres
            exit(1)
        elif status == "CANCELED":
            print(f"\n[!] Deploy cancelado")
            exit(1)
        
        time.sleep(5)
    
    print(f"\n[+] Deploy finalizado!")
    
except requests.exceptions.RequestException as e:
    print(f"[!] Error de conexion: {e}")
    if hasattr(e, 'response') and e.response is not None:
        print(f"Response: {e.response.text}")
    exit(1)
except Exception as e:
    print(f"[!] Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
