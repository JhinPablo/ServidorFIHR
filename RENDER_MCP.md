# 🎯 Render MCP - Control desde VS Code

Control total de tu servicio Render directamente desde Visual Studio Code.

## ⚙️ Configuración

### 1. Agregar API Key de Render

Establece tu API key de Render en las variables de entorno:

**En Render Dashboard:**
1. Ve a tu servicio **ServidorFIHR**
2. Environment Variables
3. Agrega:
   ```
   RENDER_API_KEY=rnd_UdMTfMyHhjomesjaPEDrJDV5MeIQ
   ```

**En tu máquina local (para testing):**
```powershell
$env:RENDER_API_KEY="rnd_UdMTfMyHhjomesjaPEDrJDV5MeIQ"
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

## 📋 Comandos CLI

### Ver estado del servicio
```bash
python render_cli.py status
```

Salida:
```
==================================================
  📊 SERVICE STATUS
==================================================

Servicio: ServidorFIHR
Status: live
URL: https://servidorfhir.onrender.com
Creado: 2026-02-24T10:30:00Z
Actualizado: 2026-02-24T14:45:00Z
```

### Triggear redeploy
```bash
python render_cli.py redeploy
```

Con monitoreo en tiempo real:
```bash
python render_cli.py redeploy --watch
```

### Ver logs
```bash
python render_cli.py logs
```

Con más líneas:
```bash
python render_cli.py logs --lines 200
```

### Gestionar variables de entorno

**Listar todas:**
```bash
python render_cli.py env list
```

**Establecer una variable:**
```bash
python render_cli.py env set DATABASE_URL "postgresql://..."
```

### Listar bases de datos
```bash
python render_cli.py databases
```

## 🌐 Endpoints HTTP

Tu servidor tiene endpoints para MCP. Úsalos con curl o Postman:

### Ver estado del servicio
```bash
curl -H "Authorization: Bearer tu-api-key" \
  https://servidorfhir.onrender.com/render/status
```

### Triggear redeploy
```bash
curl -X POST -H "Authorization: Bearer tu-api-key" \
  https://servidorfhir.onrender.com/render/redeploy
```

### Ver variables de entorno
```bash
curl -H "Authorization: Bearer tu-api-key" \
  https://servidorfhir.onrender.com/render/env-vars
```

### Actualizar variable
```bash
curl -X POST -H "Authorization: Bearer tu-api-key" \
  "https://servidorfhir.onrender.com/render/env-var/MY_VAR?value=new_value"
```

### Verificar conexión con Render API
```bash
curl -H "Authorization: Bearer tu-api-key" \
  https://servidorfhir.onrender.com/render/health
```

## 🚀 Integración en VS Code

### Terminal integrada

Abre la terminal en VS Code (`Ctrl+Shift+`` ) y ejecuta:

```bash
# Ver estado
python render_cli.py status

# Redeploy con monitoreo
python render_cli.py redeploy --watch

# Ver logs
python render_cli.py logs --lines 50
```

### Tareas automatizadas

Edita `.vscode/tasks.json`:

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Render: Status",
      "type": "shell",
      "command": "python",
      "args": ["render_cli.py", "status"],
      "problemMatcher": [],
      "group": {
        "kind": "test",
        "isDefault": true
      }
    },
    {
      "label": "Render: Redeploy",
      "type": "shell",
      "command": "python",
      "args": ["render_cli.py", "redeploy", "--watch"],
      "problemMatcher": [],
      "group": "test"
    }
  ]
}
```

Luego ejecuta con `Ctrl+Shift+B` o desde Command Palette.

## 📊 Casos de uso

### 1. Redeploy después de cambios

```bash
git add .
git commit -m "Fix: ajuste importante"
git push
python render_cli.py redeploy --watch
```

### 2. Monitorear problema en producción

```bash
python render_cli.py status
python render_cli.py logs --lines 200
```

### 3. Actualizar configuración

```bash
python render_cli.py env set API_KEY "new-key"
python render_cli.py redeploy
```

## 🔐 Seguridad

⚠️ **Nunca commits tu RENDER_API_KEY al repositorio**

- Variables sensibles se muestran como `***REDACTED***`
- Solo exponga endpoints HTTP con autenticación
- Rota las API keys regularmente

## 📚 Módulos Python

### `render_mcp.py`

Cliente OOP para Render API:

```python
from render_mcp import RenderMCP

mcp = RenderMCP(api_key="tu-api-key")

# Ver servicios
services = mcp.get_services()

# Triggear deploy
deploy = mcp.trigger_deploy("service-id")

# Obtener logs
logs = mcp.get_service_logs("service-id")
```

### `render_cli.py`

Interfaz CLI para Render API:

```bash
python render_cli.py --help
```

## 🆘 Troubleshooting

### Error: "RENDER_API_KEY no configurada"

Establesce la variable de entorno:
```bash
export RENDER_API_KEY=rnd_...  # Linux/Mac
$env:RENDER_API_KEY="rnd_..."  # PowerShell
```

### Error: "Servicio no encontrado"

Verifica el nombre exacto en Render Dashboard (por defecto: `ServidorFIHR`)

Edita `render_mcp.py` para cambiar el nombre por defecto.

### Deploy se queda atascado

Cancela con `Ctrl+C` y verifica los logs:
```bash
python render_cli.py logs --lines 300
```

## 📖 Referencias

- [Render API Docs](https://render.com/docs/api)
- [FastAPI API](https://fastapi.tiangolo.com/)
- [Pydantic](https://docs.pydantic.dev/)
