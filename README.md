# 🔐 Sistema de Transferencia Segura de Archivos - ESICORP

Sistema robusto de transferencia segura de archivos entre máquinas usando cifrado simétrico AES-256-GCM, verificación de integridad SHA-256 y transmisión mediante sockets TCP/IP.

## 📋 Descripción

Este proyecto fue desarrollado para la financiera **ESICORP** con el objetivo de transportar de forma segura información digital de alta relevancia entre sus sedes en Latinoamérica. El sistema garantiza:

- ✅ **Confidencialidad**: Cifrado AES-256-GCM
- ✅ **Integridad**: Verificación mediante SHA-256
- ✅ **Autenticación**: Código de seguridad compartido
- ✅ **Compresión**: Archivos empaquetados en formato ZIP
- ✅ **Codificación**: Base64 antes del cifrado

## 🛠️ Tecnologías Utilizadas

- **Python 3.7+**
- **Criptografía**: `cryptography` (AES-256-GCM, PBKDF2HMAC)
- **Hashing**: SHA-256
- **Protocolo**: Sockets TCP/IP
- **Compresión**: ZIP
- **Interfaz**: CLI con argparse + Modo interactivo con tkinter

## 📁 Estructura del Proyecto

```
ScriptAutomatizacion/
├── main.py                 # Punto de entrada principal
├── requirements.txt        # Dependencias del proyecto
├── README.md              # Este archivo
├── .gitignore             # Archivos ignorados por Git
├── src/
│   ├── __init__.py
│   ├── config.py          # Configuración de seguridad y red
│   ├── cli_parser.py      # Parser de argumentos CLI
│   ├── crypto_manager.py  # Gestión de cifrado/descifrado
│   ├── file_manager.py    # Gestión de archivos y compresión
│   ├── network_manager.py # Gestión de conexiones de red
│   ├── sender.py          # Lógica de envío de archivos
│   ├── receiver.py        # Lógica de recepción de archivos
│   └── utils.py           # Utilidades y funciones de impresión
└── transfers/             # Directorio para sesiones de transferencia
    └── .gitkeep
```

## 🚀 Configuración Inicial

### 1. Requisitos Previos

- Python 3.7 o superior instalado
- Conexión de red entre máquinas emisora y receptora
- Puertos disponibles (por defecto: 5000)

### 2. Instalación de Dependencias

```powershell
# Crear entorno virtual (recomendado)
python -m venv venv

# Activar entorno virtual
# En Windows PowerShell:
.\venv\Scripts\Activate.ps1
# En Windows CMD:
.\venv\Scripts\activate.bat
# En Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 3. Configuración de Seguridad

Editar `src/config.py` para personalizar:

```python
# Contraseña compartida (cambiar en producción)
SHARED_PASSWORD = "EsicorpPasswordSegura2024!"

# Salt para derivación de clave (cambiar en producción)
SALT = b"\x15\xba\x81\xd7R\xd3\xf9(\xa3\xce@\x15\xf6\x92\xd7("

# Puerto por defecto
DEFAULT_PORT = 5000
```

⚠️ **IMPORTANTE**: Cambiar `SHARED_PASSWORD` y `SALT` en ambas máquinas (emisor y receptor).

## 📖 Modos de Uso

### Modo 1️⃣: Interactivo (Menú)

Ideal para usuarios que prefieren una interfaz guiada paso a paso.

```powershell
python main.py --interactivo
# O forma corta:
python main.py -i
```

**Características:**

- Menú visual intuitivo
- Selección de archivos mediante diálogo gráfico
- Validación interactiva de datos
- Opciones de reintento en caso de error

### Modo 2️⃣: Emisor Automático

Perfecto para scripts automatizados y tareas programadas.

```powershell
# Sintaxis completa
python main.py --emisor --archivo "C:\Datos\Compras-23-02-2023.santiago" --ip 192.168.1.10 --puerto 5000 --codigo 1234

# Sintaxis con opciones cortas
python main.py -e -a "Ventas-10-11-2023.lima" -d 10.0.0.5 -p 5001 -c 9876

# Puerto por defecto (5000)
python main.py -e -a "Finanzas-12-12-2023.buenosaires" -d 192.168.1.20 -c 5555
```

**Parámetros:**

- `--emisor` / `-e`: Activa modo emisor
- `--archivo` / `-a`: Ruta del archivo o carpeta (requerido)
- `--ip` / `-d`: IP del receptor (requerido)
- `--puerto` / `-p`: Puerto de conexión (opcional, default: 5000)
- `--codigo` / `-c`: Código de seguridad (requerido)

### Modo 3️⃣: Receptor Automático

Para máquinas que esperan recibir archivos de forma desatendida.

```powershell
# Recibir archivo (requiere desencriptado manual posterior)
python main.py --receptor --codigo 1234

# Recibir y desencriptar automáticamente
python main.py --receptor --codigo 1234 --desencriptar

# Con puerto específico
python main.py -r -c 5678 -p 5001 --desencriptar

# Puerto automático (recomendado)
python main.py -r -c 1234
```

**Parámetros:**

- `--receptor` / `-r`: Activa modo receptor
- `--codigo` / `-c`: Código de seguridad (requerido)
- `--puerto` / `-p`: Puerto de escucha (opcional, 0 = automático)
- `--desencriptar`: Desencripta automáticamente al recibir (opcional)

### Ayuda

```powershell
python main.py --help
python main.py -h
```

## 🔄 Flujo de Trabajo Típico

### Escenario: Enviar archivo desde Bogotá a Santiago

**Máquina Receptora (Santiago):**

```powershell
# Iniciar receptor en modo automático
python main.py -r -c 1234 --desencriptar
```

El sistema mostrará:

```
=== MODO RECEPTOR AUTOMÁTICO ===

Puerto: Asignación automática
Código: ****
Desencriptado automático: Sí

🔊 Servidor activo en: 192.168.1.10:52341
   Código de Seguridad: 1234
   
Esperando conexión...
```

**Máquina Emisora (Bogotá):**

```powershell
# Enviar archivo
python main.py -e -a "C:\Datos\Compras-23-02-2023.santiago" -d 192.168.1.10 -p 52341 -c 1234
```

El sistema procesará:

1. ✅ Compresión del archivo en ZIP
2. ✅ Cálculo de hash SHA-256
3. ✅ Cifrado con AES-256-GCM
4. ✅ Empaquetado seguro
5. ✅ Transmisión por red
6. ✅ Verificación de integridad
7. ✅ Desencriptado automático (en receptor)

## 🔒 Detalles de Seguridad

### Algoritmo de Cifrado

- **AES-256-GCM** (Galois/Counter Mode)
  - Cifrado simétrico de 256 bits
  - Modo autenticado (previene manipulación)
  - Nonce único de 12 bytes por operación
  - Tag de autenticación de 16 bytes

### Derivación de Clave

- **PBKDF2HMAC-SHA256**
  - 100,000 iteraciones (protección contra fuerza bruta)
  - Salt único (protección contra rainbow tables)
  - Genera clave maestra de 32 bytes

### Verificación de Integridad

- **SHA-256**
  - Hash de 256 bits del archivo comprimido
  - Verificación antes y después de la transmisión
  - Detecta cualquier modificación del archivo

### Codificación

- **Base64**
  - Codificación del ZIP antes del cifrado
  - Asegura compatibilidad en transmisión

## 📦 Estructura del Paquete Transmitido

Cada archivo enviado contiene:

```
[Nonce: 12 bytes] + [Hash SHA-256: 64 bytes] + [Datos Cifrados: N bytes]
```

El flujo completo es:

```
Archivo Original 
  → Compresión ZIP 
    → Codificación Base64 
      → Cifrado AES-256-GCM 
        → Empaquetado con Nonce y Hash 
          → Transmisión TCP/IP
```

## 🌐 Nomenclatura de Archivos ESICORP

El sistema soporta la nomenclatura definida por ESICORP:

```
[Área]-[DD]-[MM]-[AA].[Sede]

Ejemplos:
- Compras-23-02-2023.santiago
- Ventas-10-11-2023.buenosaires
- Finanzas-12-12-2023.lima
```

⚠️ El script acepta **cualquier nombre de archivo**, no está limitado a esta nomenclatura.

## 🛡️ Restricciones de Seguridad

De acuerdo con las políticas de ESICORP, **NO se permite**:

- ❌ Correo electrónico
- ❌ Servicios de almacenamiento en nube (Google Drive, Dropbox, etc.)
- ❌ Servicios web públicos

✅ **Solo se permite**: Transferencia directa punto a punto mediante sockets TCP/IP.

## 🧪 Ejemplo de Prueba Local

### Terminal 1 (Receptor):

```powershell
python main.py -r -c 1234 --desencriptar
```

### Terminal 2 (Emisor):

```powershell
python main.py -e -a "test.txt" -d 127.0.0.1 -p [PUERTO_MOSTRADO] -c 1234
```

## 📊 Sesiones y Logs

Cada transferencia crea una sesión con timestamp:

```
transfers/
└── 20251125_143022/          # Fecha y hora de la sesión
    ├── sender/               # Archivos del emisor
    │   └── payload.enc       # Paquete cifrado
    └── receiver/             # Archivos del receptor
        └── decrypted_files/  # Archivos desencriptados
```

## 🔧 Solución de Problemas

### Error: "El puerto debe estar entre 1024 y 65535"

- Usar puertos no privilegiados (>1024)
- Verificar que el puerto no esté en uso

### Error: "No se pudo establecer conexión"

- Verificar firewall en ambas máquinas
- Confirmar que la IP es correcta
- Asegurar que el receptor esté escuchando

### Error: "Código de seguridad incorrecto"

- El código debe ser idéntico en emisor y receptor
- Verificar que no haya espacios adicionales

### Error: "ERROR DE INTEGRIDAD - Hash no coincide"

- El archivo fue modificado durante la transmisión
- Posible interferencia en la red
- Reintentar la transferencia

## 👥 Créditos

Desarrollado para **ESICORP** - Financiera establecida en 1930

- Proyecto: Fase 2 - Solución de problemas para el manejo de integridad y confidencialidad
- Curso: Algoritmos y Modelos Criptográficos (219027)
- Programa: Especialización en Seguridad Informática
- Institución: Universidad Nacional Abierta y a Distancia (UNAD)
- Integrantes del grupo:
  - *MILLER ALEXANDER PARDO OVEJERO*
  - *OSCAR YESID BERNAL RODRÍGUEZ*
  - *YEFERSON CAMILO ZAQUE BAUTISTA*
  - *JOAQUIN JESUS VALLEJO*
  - *JHON JAIRO ESCORCIA RAMOS*

## 📝 Licencia

Este proyecto es de uso interno exclusivo de ESICORP.

---

## 🔐 Script SFTP Auto-Configurable (esicorp_final.py)

### Descripción

Script Python robusto y auto-configurable que automatiza el envío seguro de archivos desde Windows hacia servidores Linux usando SFTP. El script gestiona automáticamente sus propias llaves criptográficas RSA.

### Características Principales

- ✅ **Auto-configuración de Llaves**: Genera automáticamente llaves RSA de 4096 bits si no existen
- ✅ **Integridad**: Verificación mediante hash SHA-256
- ✅ **Codificación**: Conversión a Base64 antes del cifrado
- ✅ **Confidencialidad**: Cifrado AES-256-CBC con clave y IV únicos
- ✅ **Empaquetado**: Archivos comprimidos en formato ZIP
- ✅ **Transmisión Segura**: SFTP con autenticación por llave pública

### Flujo de Funcionamiento

#### 1. Módulo de Auto-Configuración (PRIORITARIO)

El script verifica automáticamente si existen las llaves RSA en `./keys`:

- **Si NO existen**:
  - Genera un nuevo par de llaves RSA de 4096 bits
  - Guarda `id_rsa` (llave privada) y `id_rsa.pub` (llave pública)
  - **IMPORTANTE**: El script se detiene y muestra un mensaje de advertencia visible
  - El usuario debe copiar el contenido de `./keys/id_rsa.pub` al archivo `~/.ssh/authorized_keys` en el servidor Linux
  - El usuario presiona ENTER para continuar después de configurar el servidor

#### 2. Módulo de Procesamiento de Archivos

Busca archivos en `./salida` que cumplan con el patrón regex: `Area-DD-MM-AAAA.Sede`

Ejemplos válidos:
- `Finanzas-12-12-2025.lima`
- `Compras-23-02-2023.santiago`
- `Ventas-10-11-2023.buenosaires`

Para cada archivo encontrado:

1. **Integridad**: Calcula hash SHA-256 → guarda como `.hash.txt`
2. **Codificación**: Convierte el archivo a Base64
3. **Confidencialidad**: Cifra el Base64 usando AES-256-CBC → guarda como `.enc`
4. **Empaquetado**: Crea archivo ZIP conteniendo:
   - Archivo cifrado (`.enc`)
   - Hash de integridad (`.hash.txt`)
   - Metadata del procesamiento

#### 3. Módulo de Transmisión SFTP

- Conecta al servidor Linux usando `paramiko`
- Autentica mediante la llave privada RSA generada/validada
- Sube el archivo ZIP al servidor
- Manejo robusto de errores con mensajes instructivos

### Configuración del Servidor SFTP

Editar las siguientes variables en `esicorp_final.py`:

```python
SFTP_CONFIG = {
    'hostname': '192.168.1.100',  # IP del servidor Linux
    'port': 22,                     # Puerto SSH/SFTP
    'username': 'esicorp',          # Usuario SFTP
    'remote_path': '/home/esicorp/uploads/'  # Ruta remota de destino
}
```

### Instalación de Dependencias

```powershell
pip install -r requirements.txt
```

Librerías requeridas:
- `cryptography` (generación de llaves RSA, cifrado AES-256)
- `paramiko` (cliente SFTP)
- Módulos estándar: `os`, `re`, `hashlib`, `base64`, `zipfile`

### Uso del Script

#### Paso 1: Preparar Archivos

Coloque los archivos a enviar en la carpeta `./salida`:

```powershell
mkdir salida
# Copiar archivos con formato: Area-DD-MM-AAAA.Sede
cp Finanzas-25-12-2025.lima ./salida/
```

#### Paso 2: Ejecutar el Script

```powershell
python esicorp_final.py
```

#### Paso 3: Primera Ejecución (Configuración de Llaves)

Si es la primera vez que ejecuta el script:

1. El script generará automáticamente las llaves RSA
2. Mostrará un mensaje de advertencia con instrucciones
3. **DEBE** copiar el contenido de `./keys/id_rsa.pub` al servidor Linux:

```bash
# En el servidor Linux, ejecutar:
mkdir -p ~/.ssh
echo 'ssh-rsa AAAA...[CONTENIDO_COMPLETO]...== esicorp' >> ~/.ssh/authorized_keys
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

4. Presionar ENTER en el script para continuar

#### Paso 4: Verificar Transferencia

El script mostrará el progreso:

```
═══════════════════════════════════════════════════════════════
           ESICORP - Sistema de Transferencia Segura
                  Auto-Configurable SFTP
═══════════════════════════════════════════════════════════════

PASO 1: VERIFICACIÓN DE LLAVES RSA (AUTENTICACIÓN)
✅ Llaves RSA encontradas

PASO 2: BÚSQUEDA Y PROCESAMIENTO DE ARCHIVOS
✅ Encontrados 1 archivo(s)
📄 Procesando: Finanzas-25-12-2025.lima
🔍 [INTEGRIDAD] Calculando hash SHA-256...
📝 [CODIFICACIÓN] Convirtiendo a Base64...
🔐 [CONFIDENCIALIDAD] Cifrando con AES-256-CBC...
📦 [EMPAQUETADO] Creando archivo ZIP...
✅ Procesamiento completado

PASO 3: CONEXIÓN SFTP AL SERVIDOR LINUX
✅ Conexión SFTP establecida exitosamente
📤 Enviando archivo al servidor...
✅ Enviado exitosamente

🎉 ¡PROCESO COMPLETADO EXITOSAMENTE! 🎉
```

### Estructura de Directorios

```
ScriptAutomatizacion/
├── esicorp_final.py      # Script principal SFTP
├── keys/                 # Llaves RSA (generadas automáticamente)
│   ├── id_rsa           # Llave privada (NO compartir)
│   └── id_rsa.pub       # Llave pública (copiar al servidor)
├── salida/              # Archivos a enviar (input)
│   └── Area-DD-MM-AAAA.Sede
└── procesados/          # Archivos procesados (output)
    └── Area-DD-MM-AAAA.zip
```

### Solución de Problemas

#### Error: "AuthenticationFailed"

**Síntoma**: El script no puede conectar al servidor SFTP

**Solución**:
1. Verificar que copió correctamente el contenido de `id_rsa.pub` al servidor
2. Verificar permisos del archivo `~/.ssh/authorized_keys` (debe ser 600)
3. Verificar que el directorio `~/.ssh` tiene permisos 700

```bash
# En el servidor Linux:
ls -la ~/.ssh/
# Debe mostrar:
# drwx------  .ssh/
# -rw-------  authorized_keys
```

#### Error: "No se encontraron archivos"

**Síntoma**: El script no encuentra archivos en `./salida`

**Solución**:
- Verificar que los archivos cumplan con el patrón: `Area-DD-MM-AAAA.Sede`
- Ejemplos válidos:
  - ✅ `Finanzas-12-12-2025.lima`
  - ✅ `Compras-23-02-2023.santiago`
  - ❌ `archivo.txt` (no cumple el patrón)
  - ❌ `Finanzas-12-2025.lima` (formato de fecha incorrecto)

#### Error: "Falta instalar dependencias"

**Solución**:
```powershell
pip install -r requirements.txt
```

### Seguridad

El script implementa múltiples capas de seguridad según los estándares de ESICORP:

| Aspecto | Implementación | Algoritmo |
|---------|----------------|-----------|
| **Autenticación** | Llave pública RSA | RSA 4096 bits |
| **Integridad** | Hash del archivo | SHA-256 |
| **Codificación** | Compatibilidad de transmisión | Base64 |
| **Confidencialidad** | Cifrado simétrico | AES-256-CBC |
| **Transmisión** | Protocolo seguro | SFTP sobre SSH |

### Comentarios en el Código

El código incluye comentarios explicativos que identifican qué parte cumple con cada requisito:

- `# AUTENTICACIÓN:` - Generación y uso de llaves RSA
- `# INTEGRIDAD:` - Cálculo y verificación de hashes SHA-256
- `# CODIFICACIÓN:` - Conversión a Base64
- `# CONFIDENCIALIDAD:` - Cifrado AES-256-CBC

---

**Última actualización**: Diciembre 2025
