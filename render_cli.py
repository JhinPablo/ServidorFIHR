#!/usr/bin/env python3
# ===============================================
# RENDER MCP CLI - Control desde VS Code
# ===============================================

import sys
import argparse
from render_mcp import (
    get_service_info,
    redeploy_service,
    watch_deploy,
    get_env_vars,
    update_env_var,
    RenderMCP
)

def print_header(title):
    """Imprimir encabezado"""
    print(f"\n{'='*50}")
    print(f"  {title}")
    print(f"{'='*50}\n")

def cmd_status(args):
    """Mostrar estado del servicio"""
    print_header("📊 SERVICE STATUS")
    try:
        info = get_service_info()
        print(f"Servicio: {info['name']}")
        print(f"Status: {info['status']}")
        print(f"URL: {info['url']}")
        print(f"Creado: {info['createdAt']}")
        print(f"Actualizado: {info['updatedAt']}")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

def cmd_redeploy(args):
    """Triggear redeploy"""
    print_header("🚀 TRIGGERING REDEPLOY")
    try:
        result = redeploy_service()
        print(f"✅ {result['message']}")
        print(f"Deploy ID: {result['deployId']}")
        print(f"Status: {result['status']}")
        
        if args.watch:
            print_header("⏳ WATCHING DEPLOY")
            watch_result = watch_deploy()
            print(watch_result.get('message', watch_result))
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

def cmd_logs(args):
    """Mostrar logs"""
    print_header("📋 SERVICE LOGS")
    try:
        mcp = RenderMCP()
        service = mcp.get_service_by_name()
        logs = mcp.get_service_logs(service['id'], limit=args.lines)
        print(logs)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

def cmd_env(args):
    """Gestionar variables de entorno"""
    try:
        if args.action == "list":
            print_header("🔐 ENVIRONMENT VARIABLES")
            vars = get_env_vars()
            for var in vars:
                key = var.get('key')
                value = var.get('value')
                # Ocultar valores sensibles
                if key in ['API_KEY', 'DATABASE_URL', 'RENDER_API_KEY']:
                    value = '***REDACTED***'
                print(f"  {key}: {value}")
        
        elif args.action == "set":
            key = args.key
            value = args.value
            print_header(f"🔐 UPDATING {key}")
            result = update_env_var(key, value)
            print(f"✅ Variable '{key}' actualizada")
            print(f"Resultado: {result}")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

def cmd_databases(args):
    """Listar bases de datos"""
    print_header("🗄️  DATABASES")
    try:
        mcp = RenderMCP()
        databases = mcp.get_databases()
        if not databases:
            print("No hay bases de datos")
            return
        
        for db in databases:
            print(f"\nNombre: {db.get('name')}")
            print(f"ID: {db.get('id')}")
            print(f"Status: {db.get('status')}")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description="🎯 Render MCP CLI - Control tu servicio desde VS Code"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Comando a ejecutar')
    
    # Comando: status
    subparsers.add_parser('status', help='Ver estado del servicio')
    
    # Comando: redeploy
    redeploy_parser = subparsers.add_parser('redeploy', help='Triggear redeploy')
    redeploy_parser.add_argument('--watch', action='store_true', help='Monitorear el deploy')
    
    # Comando: logs
    logs_parser = subparsers.add_parser('logs', help='Ver logs')
    logs_parser.add_argument('--lines', type=int, default=100, help='Número de líneas')
    
    # Comando: env
    env_parser = subparsers.add_parser('env', help='Gestionar variables de entorno')
    env_subparsers = env_parser.add_subparsers(dest='action')
    
    env_subparsers.add_parser('list', help='Listar variables')
    
    set_parser = env_subparsers.add_parser('set', help='Establecer variable')
    set_parser.add_argument('key', help='Nombre de la variable')
    set_parser.add_argument('value', help='Valor de la variable')
    
    # Comando: databases
    subparsers.add_parser('databases', help='Listar bases de datos')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == 'status':
        cmd_status(args)
    elif args.command == 'redeploy':
        cmd_redeploy(args)
    elif args.command == 'logs':
        cmd_logs(args)
    elif args.command == 'env':
        cmd_env(args)
    elif args.command == 'databases':
        cmd_databases(args)

if __name__ == '__main__':
    main()
