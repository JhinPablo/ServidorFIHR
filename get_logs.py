#!/usr/bin/env python3
import os
import requests
import json

api_key = os.getenv("RENDER_API_KEY")
if not api_key:
    print("ERROR: RENDER_API_KEY no configurada")
    exit(1)

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

try:
    # Get service
    response = requests.get(
        "https://api.render.com/v1/services",
        headers=headers
    )
    response.raise_for_status()
    
    service_data = response.json()[0].get('service', {})
    service_id = service_data.get('id')
    
    print(f"[*] Obteniendo logs del servicio {service_id}...\n")
    
    # Get logs
    logs_response = requests.get(
        f"https://api.render.com/v1/services/{service_id}/logs",
        headers=headers
    )
    
    if logs_response.status_code == 200:
        logs = logs_response.text
        print(logs)
    else:
        print(f"Error: {logs_response.status_code}")
        print(logs_response.text)
        
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
