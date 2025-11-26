import os

# Configuración de Seguridad
SHARED_PASSWORD = "EsicorpPasswordSegura2024!"
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
