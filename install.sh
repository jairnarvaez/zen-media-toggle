#!/bin/bash

# Script de instalación para Native Messaging

echo "=== Instalación de Native Messaging Host ==="

# Obtener la ruta actual
CURRENT_DIR=$(pwd)
HOST_PATH="$CURRENT_DIR/native_host.py"
MANIFEST_PATH="$CURRENT_DIR/media_tab_controller.json"

# Hacer ejecutable el host
chmod +x native_host.py
chmod +x controller.py

# Obtener el ID de la extensión
echo ""
echo "Por favor, ingresa el ID de tu extensión"
echo "(Lo puedes encontrar en about:debugging)"
read -p "ID de extensión: " EXTENSION_ID

# Crear el manifest con la ruta correcta
cat > media_tab_controller.json << EOF
{
  "name": "media_tab_controller",
  "description": "Controla pestañas con medios desde la terminal",
  "path": "$HOST_PATH",
  "type": "stdio",
  "allowed_extensions": ["$EXTENSION_ID"]
}
EOF

# Detectar el navegador y crear el directorio apropiado
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    MANIFEST_DIR="$HOME/.mozilla/native-messaging-hosts"
    
elif [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    MANIFEST_DIR="$HOME/Library/Application Support/Mozilla/NativeMessagingHosts"
    
else
    echo "Sistema operativo no soportado"
    exit 1
fi

# Crear directorio si no existe
mkdir -p "$MANIFEST_DIR"

# Copiar el manifest
cp media_tab_controller.json "$MANIFEST_DIR/"

echo ""
echo "✓ Instalación completa"
echo "✓ Manifest instalado en: $MANIFEST_DIR"
echo ""
echo "Comandos disponibles:"
echo "  ./controller.py switch       - Cambiar a pestaña con medios"
echo "  ./controller.py list         - Listar pestañas con medios"
echo "  ./controller.py goto <id>    - Cambiar a pestaña específica"
echo ""
echo "Para probar, ejecuta: ./controller.py switch"