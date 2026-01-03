#!/usr/bin/env python3
import sys
import json
import struct
import os
import socket
import threading

# Log file para debug
LOG_FILE = os.path.expanduser("~/native_host.log")
SOCKET_PATH = "/tmp/zen_media_control.sock"

# Variable global para el puerto de la extensión
extension_port = None

def log(message):
    """Escribe en el archivo de log para debug"""
    with open(LOG_FILE, 'a') as f:
        f.write(f"{message}\n")

def send_to_extension(message):
    """Envía un mensaje a la extensión"""
    global extension_port
    if not extension_port:
        log("ERROR: No hay conexión con la extensión")
        return False
    
    try:
        encoded = json.dumps(message).encode('utf-8')
        sys.stdout.buffer.write(struct.pack('I', len(encoded)))
        sys.stdout.buffer.write(encoded)
        sys.stdout.buffer.flush()
        log(f"SENT to extension: {message}")
        return True
    except Exception as e:
        log(f"ERROR sending to extension: {e}")
        return False

def read_from_extension():
    """Lee un mensaje de la extensión"""
    try:
        raw_length = sys.stdin.buffer.read(4)
        if len(raw_length) == 0:
            log("Connection closed by extension")
            return None
        
        message_length = struct.unpack('I', raw_length)[0]
        message = sys.stdin.buffer.read(message_length).decode('utf-8')
        parsed = json.loads(message)
        log(f"RECEIVED from extension: {parsed}")
        return parsed
    except Exception as e:
        log(f"ERROR reading from extension: {e}")
        return None

def handle_socket_client(client_socket):
    """Maneja conexiones desde el socket Unix (comandos de terminal)"""
    try:
        # Lee el comando del socket
        data = client_socket.recv(4096).decode('utf-8')
        if not data:
            return
        
        command = json.loads(data)
        log(f"RECEIVED from socket: {command}")
        
        # Envía el comando a la extensión
        if send_to_extension(command):
            client_socket.send(b'{"status":"sent"}\n')
        else:
            client_socket.send(b'{"status":"error","message":"No connection to extension"}\n')
            
    except Exception as e:
        log(f"ERROR handling socket client: {e}")
        try:
            client_socket.send(f'{{"status":"error","message":"{str(e)}"}}\n'.encode())
        except:
            pass
    finally:
        client_socket.close()

def socket_server():
    """Servidor de socket Unix para recibir comandos de terminal"""
    # Elimina el socket si ya existe
    if os.path.exists(SOCKET_PATH):
        os.remove(SOCKET_PATH)
    
    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(SOCKET_PATH)
    server.listen(5)
    
    log(f"Socket server listening on {SOCKET_PATH}")
    
    while True:
        try:
            client, _ = server.accept()
            # Maneja cada conexión en un thread separado
            thread = threading.Thread(target=handle_socket_client, args=(client,))
            thread.daemon = True
            thread.start()
        except Exception as e:
            log(f"ERROR in socket server: {e}")
            break

def main():
    global extension_port
    
    log("=== Native Host Started ===")
    
    # Inicia el servidor de socket en un thread separado
    socket_thread = threading.Thread(target=socket_server)
    socket_thread.daemon = True
    socket_thread.start()
    
    log("Socket server started, waiting for extension messages...")
    
    extension_port = True  # Marca que estamos conectados
    
    # Lee mensajes de la extensión
    while True:
        try:
            message = read_from_extension()
            if message is None:
                break
            
            # Procesa respuestas de la extensión
            if 'success' in message:
                if message['success']:
                    action = message.get('action', 'switched')
                    if action == 'toggled_back':
                        log(f" Volviendo a: {message.get('title', 'Pestaña anterior')}")
                    else:
                        log(f" Cambiado a: {message.get('title', 'Pestaña')}")
                        if message.get('previousTabId'):
                            log(f"  (Pestaña anterior guardada: {message['previousTabId']})")
                else:
                    log(f" {message.get('message', 'Error')}")
            
            elif 'command' in message and message['command'] == 'media_tabs_list':
                log(f"Pestañas con medios:")
                for tab in message.get('tabs', []):
                    log(f"  - [{tab['id']}] {tab['title']}")
            
            elif 'event' in message and message['event'] == 'media_started':
                log(f" Media iniciado en: {message['title']}")
                
        except Exception as e:
            log(f"Error in main loop: {e}")
            break
    
    log("=== Native Host Stopped ===")

if __name__ == '__main__':
    main()