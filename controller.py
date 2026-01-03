#!/usr/bin/env python3
"""
Script para controlar la extensión desde la terminal
Uso:
  ./controller.py switch      # Cambia a pestaña con medios
  ./controller.py list        # Lista pestañas con medios
  ./controller.py goto <id>   # Cambia a pestaña específica
"""
import sys
import json
import socket
import os

SOCKET_PATH = "/tmp/zen_media_control.sock"

def send_command(command_data):
    try:
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client.connect(SOCKET_PATH)
        
        message = json.dumps(command_data)
        client.send(message.encode('utf-8'))
        
        response = client.recv(4096).decode('utf-8')
        result = json.loads(response)
        
        if result.get('status') == 'sent':
            print(f" Comando enviado: {command_data['command']}")
            print("  Revisa el log para ver la respuesta: tail -f ~/native_host.log")
        else:
            print(f" Error: {result.get('message', 'Unknown error')}")
        
        client.close()
        return True
        
    except FileNotFoundError:
        print(f" Error: Socket no encontrado en {SOCKET_PATH}")
        print("  ¿Está la extensión activa y conectada?")
        print("  Verifica: tail -f ~/native_host.log")
        return False
        
    except ConnectionRefusedError:
        print("✗ Error: No se pudo conectar al socket")
        print("  El native host no está escuchando")
        return False
        
    except Exception as e:
        print(f" Error: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Uso: controller.py [switch|list|goto <id>|toggle|status]")
        print()
        print("Comandos:")
        print("  switch       - Cambiar a pestaña con medios")
        print("  toggle       - Alternar entre pestaña actual y pestaña con medios")
        print("  list         - Listar pestañas con medios")
        print("  goto <id>    - Cambiar a pestaña específica por ID")
        print("  status       - Verificar estado de la conexión")
        sys.exit(1)
    
    command = sys.argv[1]
    command_data = {}
    
    if command == "switch":
        command_data = {"command": "switch_to_media"}
    
    elif command == "toggle":
        command_data = {"command": "toggle"}
    
    elif command == "list":
        command_data = {"command": "get_media_tabs"}
    
    elif command == "goto" and len(sys.argv) > 2:
        try:
            tab_id = int(sys.argv[2])
            command_data = {"command": "switch_to_tab", "tabId": tab_id}
        except ValueError:
            print("✗ Error: El ID de pestaña debe ser un número")
            sys.exit(1)
    
    elif command == "status":
        if os.path.exists(SOCKET_PATH):
            print(f" Socket encontrado: {SOCKET_PATH}")
            try:
                client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                client.settimeout(1)
                client.connect(SOCKET_PATH)
                client.close()
                print(" Native host está escuchando")
                print(" La extensión debería estar conectada")
            except:
                print(" Socket existe pero no responde")
        else:
            print(f" Socket no encontrado: {SOCKET_PATH}")
            print("  La extensión no está conectada al native host")
        
        log_file = os.path.expanduser("~/native_host.log")
        if os.path.exists(log_file):
            print(f"\nÚltimas líneas del log:")
            os.system(f"tail -n 5 {log_file}")
        return
    
    else:
        print(f" Comando desconocido: {command}")
        sys.exit(1)
    
    send_command(command_data)

if __name__ == '__main__':
    main()
