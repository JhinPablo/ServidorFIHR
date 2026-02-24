#!/usr/bin/env python3
import os
from render_mcp import RenderMCP

# Configurar API key
api_key = os.getenv("RENDER_API_KEY")
if not api_key:
    print("❌ RENDER_API_KEY no configurada")
    exit(1)

try:
    mcp = RenderMCP(api_key=api_key)
    
    # Listar servicios
    print("📋 Obteniendo lista de servicios...\n")
    services = mcp.get_services()
    
    if not services:
        print("❌ No hay servicios disponibles")
        exit(1)
    
    print(f"✅ Se encontraron {len(services)} servicio(s):\n")
    for i, s in enumerate(services, 1):
        print(f"{i}. {s.get('name')}")
        print(f"   ID: {s.get('id')}")
        print(f"   Tipo: {s.get('service', {}).get('type', 'N/A')}")
        print()
    
    # Si hay solo un servicio, usarlo
    if len(services) == 1:
        service = services[0]
    else:
        # Buscar ServidorFIHR
        service = None
        for s in services:
            if "fhir" in s.get('name', '').lower() or "servidor" in s.get('name', '').lower():
                service = s
                break
        
        if not service:
            service = services[0]
    
    print(f"🎯 Usando servicio: {service.get('name')}\n")
    
    # Obtener status
    print(f"📊 Obteniendo estado del servicio...")
    status = mcp.get_service_status(service['id'])
    print(f"Status: {status.get('status')}")
    print(f"URL: {status.get('serviceDetails', {}).get('url')}\n")
    
    # Triggear deploy
    print(f"🚀 Triggereando deploy...")
    deploy_result = mcp.trigger_deploy(service['id'])
    deploy_id = deploy_result.get('id')
    print(f"Deploy ID: {deploy_id}")
    print(f"Status: {deploy_result.get('status')}\n")
    
    print("⏳ Monitoreando deploy en tiempo real...\n")
    
    import time
    for attempt in range(120):  # 10 minutos máximo
        deploy_status = mcp.get_deploy_status(service['id'], deploy_id)
        status = deploy_status.get('status')
        
        print(f"[{attempt+1}/120] Status: {status}")
        
        if status in ["LIVE", "SUCCESS"]:
            print("\n✅ ¡Deploy completado exitosamente!")
            break
        elif status in ["BUILD_FAILED", "DEPLOY_FAILED"]:
            print(f"\n❌ Error en deploy: {status}")
            print("\n📋 Obtiendo logs de error...\n")
            logs = mcp.get_service_logs(service['id'], limit=200)
            print(logs)
            exit(1)
        elif status == "CANCELED":
            print("\n⚠️ Deploy cancelado")
            exit(1)
        
        time.sleep(5)
    
    print("\n✅ Deploy completado!")
    print(f"URL: {status.get('serviceDetails', {}).get('url')}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
