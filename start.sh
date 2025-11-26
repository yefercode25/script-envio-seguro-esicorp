#!/bin/bash

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

VENV_DIR="venv"
REQUIREMENTS="requirements.txt"

echo -e "${GREEN}====================================================${NC}"
echo -e "${GREEN}     INICIANDO SISTEMA DE TRANSFERENCIA SEGURA      ${NC}"
echo -e "${GREEN}====================================================${NC}"
echo ""

# 1. Verificar si existe Python 3
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[ERROR] Python 3 no está instalado o no se encuentra en el PATH.${NC}"
    echo "Por favor instale python3 (ej: sudo apt install python3)"
    read -p "Presione Enter para salir..."
    exit 1
fi

# 2. Verificar/Crear Entorno Virtual
if [ ! -d "$VENV_DIR" ]; then
    echo "[INFO] Entorno virtual no detectado. Creando 'venv'..."
    python3 -m venv "$VENV_DIR"
    if [ $? -ne 0 ]; then
        echo -e "${RED}[ERROR] No se pudo crear el entorno virtual.${NC}"
        echo "Asegúrese de tener instalado python3-venv (ej: sudo apt install python3-venv)"
        read -p "Presione Enter para salir..."
        exit 1
    fi
    echo -e "${GREEN}[OK] Entorno virtual creado exitosamente.${NC}"
else
    echo "[INFO] Entorno virtual detectado."
fi

# 3. Activar Entorno
echo "[INFO] Activando entorno virtual..."
source "$VENV_DIR/bin/activate"

# 4. Instalar/Verificar Dependencias
echo "[INFO] Verificando dependencias..."
pip install -r "$REQUIREMENTS" > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo -e "${RED}[ERROR] Hubo un problema instalando las dependencias.${NC}"
    echo "Intentando instalar mostrando el error..."
    pip install -r "$REQUIREMENTS"
    read -p "Presione Enter para salir..."
    exit 1
fi
echo -e "${GREEN}[OK] Dependencias al día.${NC}"

# 5. Iniciar Aplicación
echo ""
echo "[INFO] Iniciando aplicación..."
echo "----------------------------------------------------"
python main.py

# Finalización
echo ""
echo "[INFO] Sesión finalizada."
read -p "Presione Enter para cerrar..."
