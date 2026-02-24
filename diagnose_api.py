#!/usr/bin/env python3
import os
import json
import requests

api_key = os.getenv("RENDER_API_KEY")
if not api_key:
    print("❌ RENDER_API_KEY no configurada")
    exit(1)

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

print("🔍 Diagnosticando API de Render...\n")

# Test 1: Conectar a la API
print("1️⃣ Conectando a API de Render...")
try:
    response = requests.get(
        "https://api.render.com/v1/services",
        headers=headers
    )
    print(f"Status: {response.status_code}")
    print(f"Response type: {type(response.json())}\n")
    
    data = response.json()
    
    # Mostrar estructura
    if isinstance(data, list):
        print(f"📋 Lista de {len(data)} servicios:")
        for i, service in enumerate(data[:3]):  # Primeros 3
            print(f"\n  Servicio {i+1}:")
            print(f"    Keys: {list(service.keys())[:5]}...")
            if 'id' in service:
                print(f"    ID: {service['id']}")
            if 'name' in service:
                print(f"    Name: {service['name']}")
            if 'service' in service:
                print(f"    Service: {service['service']}")
    
    elif isinstance(data, dict):
        print(f"📦 Respuesta envuelta:")
        print(f"    Keys: {list(data.keys())}")
        if 'services' in data:
            services = data['services']
            print(f"    Servicios: {len(services)}")
            if services:
                print(f"\n  Servicio 1:")
                print(f"    Keys: {list(services[0].keys())[:5]}...")
                print(json.dumps(services[0], indent=2)[:500])
    
    print("\n✅ Conexión exitosa a Render API")
    
except requests.exceptions.RequestException as e:
    print(f"❌ Error de conexión: {e}")
    if hasattr(e, 'response') and e.response is not None:
        print(f"Response: {e.response.text}")
