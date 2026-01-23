"""
Configuración ESICORP - Anexo 6 Compatible
Configuración de rutas, seguridad y parámetros del sistema
"""

import os
from pathlib import Path

# ============================================================================
# CONFIGURACIÓN DE SEGURIDAD
# ============================================================================

# Configuración de Seguridad (preferiblemente desde variables de entorno)
SHARED_PASSWORD = os.getenv("ESICORP_PASSWORD", "EsicorpPasswordSegura2024!")
SALT = b"\x15\xba\x81\xd7R\xd3\xf9(\xa3\xce@\x15\xf6\x92\xd7("

# Directorio Base para todas las transferencias
BASE_DIR = "transfers"

# Configuraciones de PBKDF2
KDF_ITERATIONS = 100000
KEY_LENGTH = 32

# Configuración de Red
DEFAULT_PORT = 5000
BUFFER_SIZE = 4096
SEPARATOR = "<SEPARATOR>"

# ============================================================================
# CONFIGURACIÓN SFTP (ESICORP)
# ============================================================================

# Configuración del servidor SFTP Linux
SFTP_CONFIG = {
    "hostname": os.getenv(
        "ESICORP_SFTP_HOST", "192.168.1.100"
    ),  # IP del servidor Linux
    "port": int(os.getenv("ESICORP_SFTP_PORT", "22")),  # Puerto SSH/SFTP
    "username": os.getenv("ESICORP_SFTP_USER", "esicorp"),  # Usuario SFTP
    "remote_path": "/home/grupo1/upload/",  # Ruta remota
}

# ============================================================================
# DIRECTORIOS ESICORP - ANEXO 6
# ============================================================================

# RUTA DIAN (según Anexo 6)
# El Anexo 6 requiere que los archivos se procesen desde /Dian/XXX
# donde XXX representa la sede.

# Configuración de sede desde variable de entorno
SEDE = os.getenv("ESICORP_SEDE", "Sede001")

# Ruta base DIAN
DIAN_BASE_DIR = os.getenv("ESICORP_DIAN_PATH", "/Dian")

# Ruta completa según Anexo 6: /Dian/XXX
SALIDA_DIR_ANEXO6 = f"{DIAN_BASE_DIR}/{SEDE}"

# Validar si existe la ruta DIAN, si no, usar fallback para desarrollo
if Path(SALIDA_DIR_ANEXO6).exists():
    SALIDA_DIR = SALIDA_DIR_ANEXO6
    print(f"[CONFIG] [OK] Usando ruta DIAN (Anexo 6): {SALIDA_DIR}")
else:
    # Fallback para desarrollo/testing
    SALIDA_DIR = "./salida"
    print(f"[CONFIG] [!] Ruta DIAN no encontrada: {SALIDA_DIR_ANEXO6}")
    print(f"[CONFIG] [INFO] Usando fallback para desarrollo: {SALIDA_DIR}")
    print("[CONFIG] [TIP] Para producción, configure la variable ESICORP_DIAN_PATH")

# Directorios locales
KEYS_DIR = "./keys"
PROCESADOS_DIR = "./procesados"
