# 🔐 ESICORP - Sistema de Transferencia Segura de Archivos

Sistema automatizado de procesamiento, cifrado y transferencia segura de archivos vía SFTP con autenticación RSA 4096 bits y cifrado AES-256-CBC.

## 📋 Características

- ✅ **Cifrado de extremo a extremo**: AES-256-CBC + Base64
- ✅ **Autenticación sin contraseñas**: RSA 4096 bits
- ✅ **Integridad verificada**: Hash SHA-256
- ✅ **Desencriptación automática**: Restaura archivos originales en servidor
- ✅ **Intercambio de llaves automático**: Via sockets TCP
- ✅ **Modo CLI completo**: Todas las funciones disponibles por línea de comandos
- ✅ **Modo interactivo**: Menú intuitivo con descripciones
- ✅ **Limpieza automatizada**: Local y remota

---

## 🚀 Instalación Rápida

### Requisitos
- **Python 3.8+**
- **pip** (gestor de paquetes Python)
- **OpenSSH** (cliente y servidor)

### Linux/macOS
```bash
# Instalar dependencias
sudo apt-get update
sudo apt-get install python3 python3-pip openssh-client openssh-server unzip

# Clonar repositorio
git clone <repo-url>
cd ScriptAutomatizacionFase3

# Instalar paquetes Python
pip3 install -r requirements.txt
```

### Windows
```powershell
# Instalar OpenSSH (PowerShell como Administrador)
Add-WindowsCapability -Online -Name OpenSSH.Client~~~~0.0.1.0
Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0

# Clonar repositorio
git clone <repo-url>
cd ScriptAutomatizacionFase3

# Instalar paquetes Python
pip install -r requirements.txt
```

---

## 🎯 Uso Rápido

### Modo Interactivo (Recomendado)
```bash
python main.py -i
```

Menú con 7 opciones:
1. Verificar/Configurar SSH
2. Intercambio automático de llaves
3. Gestión de llaves RSA
4. Información del servidor
5. Enviar archivos (SFTP)
6. Limpiar configuraciones
7. Salir

### Modo CLI - Envío Automático
```bash
# Enviar archivos automáticamente
python main.py --esicorp --sftp-host 192.168.1.100 --sftp-user grupo1
```

---

## 📖 Referencia CLI Completa

### Modos Principales

| Comando | Descripción | Ejemplo |
|---------|-------------|---------|
| `-i`, `--interactivo` | Menú interactivo | `python main.py -i` |
| `--esicorp` | Envío automático SFTP | `python main.py --esicorp` |
| `--info` | Info del servidor | `python main.py --info` |
| `--check-ssh` | Verificar SSH | `python main.py --check-ssh` |
| `--key-exchange` | Intercambio de llaves | `python main.py --key-exchange --mode server` |
| `--manage-keys` | Gestión de llaves | `python main.py --manage-keys --action view` |
| `--cleanup` | Limpieza | `python main.py --cleanup --local` |

### Parámetros SFTP

| Parámetro | Default | Descripción |
|-----------|---------|-------------|
| `--sftp-host` | `192.168.1.100` | IP del servidor |
| `--sftp-user` | `grupo1` | Usuario SFTP |
| `--sftp-port` | `22` | Puerto SSH |
| `--sftp-path` | `/home/grupo1/upload/` | Ruta remota |

### Ejemplos Completos

**Intercambio de llaves:**
```bash
# Servidor (escuchar)
python main.py --key-exchange --mode server --port 5000

# Cliente (conectar)
python main.py --key-exchange --mode client --target 192.168.1.100
```

**Gestión de llaves:**
```bash
# Ver llaves actuales
python main.py --manage-keys --action view

# Generar nuevas
python main.py --manage-keys --action generate
```

**Limpieza:**
```bash
# Solo local
python main.py --cleanup --local

# Solo remoto
python main.py --cleanup --remote --sftp-host 192.168.1.100 --sftp-user grupo1

# Todo
python main.py --cleanup --all --sftp-host 192.168.1.100 --sftp-user grupo1
```

---

## 🔄 Flujo del Sistema

### Cliente (Origen)
1. **Selección**: Archivos en `./salida/` (formato: `Area-DD-MM-AAAA.Sede`)
2. **Procesamiento Seguro**:
   - Calcula hash SHA-256
   - Codifica en Base64
   - Cifra con AES-256-CBC
   - Empaqueta en ZIP
3. **Envío SFTP**: Conexión cifrada con RSA
4. **Verificación**: Integridad del archivo

### Servidor (Destino) - Automático
5. **Extracción**: Descomprime ZIP
6. **Desencriptación**:
   - Descifra AES-256-CBC
   - Decodifica Base64
   - Verifica hash SHA-256
   - Restaura archivo original con extensión

**Resultado**: Archivo original restaurado en `/home/grupo1/upload/`

---

## 📁 Estructura del Proyecto

```
ScriptAutomatizacionFase3/
├── main.py                      # Aplicación principal
├── decrypt_esicorp.py          # Script de desencriptación (se copia al servidor)
├── requirements.txt            # Dependencias Python
├── README.md                   # Este archivo
├── EXAMPLES.md                 # Ejemplos detallados
├── keys/                       # Llaves RSA (generadas automáticamente)
│   ├── id_rsa                  # Llave privada
│   └── id_rsa.pub             # Llave pública
├── salida/                     # Archivos de entrada
├── procesados/                 # Archivos procesados (ZIP)
└── src/                        # Código fuente
    ├── cli_parser.py          # Parser de argumentos CLI
    ├── config.py              # Configuración
    ├── cleanup_utils.py       # Utilidades de limpieza
    ├── esicorp_processor.py   # Procesamiento de archivos
    ├── key_exchange.py        # Intercambio de llaves
    ├── network_utils.py       # Utilidades de red
    ├── sftp_manager.py        # Gestión SFTP
    ├── ssh_service.py         # Servicio SSH
    └── utils.py               # Utilidades generales
```

---

## 🔐 Seguridad

### Capas de Protección
1. **Integridad**: SHA-256 (verifica archivos no modificados)
2. **Codificación**: Base64 (formato de transporte)
3. **Confidencialidad**: AES-256-CBC (cifrado militar)
4. **Transporte**: SSH/SFTP (canal cifrado)
5. **Autenticación**: RSA 4096 bits (sin contraseñas)

### Formato de Archivo Cifrado
```
[IV 16 bytes][Clave AES 32 bytes][Datos cifrados]
```

---

## 🛠️ Configuración del Servidor

### 1. Preparar Usuario
```bash
# Crear usuario (si no existe)
sudo useradd -m -s /bin/bash grupo1
sudo passwd grupo1

# Crear directorio de uploads
sudo mkdir -p /home/grupo1/upload
sudo chown grupo1:grupo1 /home/grupo1/upload
sudo chmod 755 /home/grupo1/upload
```

### 2. Configurar SSH
```bash
# Instalar OpenSSH
sudo apt-get install openssh-server

# Habilitar autenticación por llave
sudo nano /etc/ssh/sshd_config
# Verificar: PubkeyAuthentication yes

# Reiniciar SSH
sudo systemctl restart sshd
```

### 3. Copiar Llave Pública
```bash
# En el cliente, ver llave pública
python main.py --manage-keys --action view

# En el servidor
mkdir -p ~/.ssh
echo "<contenido_llave_publica>" >> ~/.ssh/authorized_keys
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

### 4. Instalar Dependencias Python
```bash
sudo apt-get install python3 python3-pip unzip
pip3 install cryptography
```

---

## 📊 Estados de Ejecución

### Exitoso
```
[OK] Verificacion exitosa
[OK] Archivo transferido exitosamente
[OK] Extraccion completada exitosamente
[OK] Desencriptacion completada exitosamente
[***] ¡PROCESO COMPLETADO EXITOSAMENTE!
```

### Errores Comunes

**Error de permisos:**
```
[X] ERROR: Permiso denegado
[TIP] sudo chown grupo1:grupo1 /home/grupo1/upload/
[TIP] sudo chmod 755 /home/grupo1/upload/
```

**Falta unzip:**
```
[!] Verifica que 'unzip' este instalado
[TIP] sudo apt-get install unzip
```

**Falta cryptography:**
```
[!] Verifica que Python 3 y cryptography esten instalados
[TIP] sudo apt-get install python3-pip && pip3 install cryptography
```

---

## 🔍 Solución de Problemas

### No encuentra llaves RSA
```bash
python main.py --manage-keys --action generate
```

### SSH no funciona
```bash
python main.py --check-ssh
```

### Limpiar todo y empezar de nuevo
```bash
python main.py --cleanup --all --sftp-host <IP> --sftp-user <usuario>
```

---

## 📚 Documentación Adicional

- **[EXAMPLES.md](EXAMPLES.md)**: Casos de uso detallados y ejemplos paso a paso

---

## 👥 Soporte

Para problemas o preguntas:
1. Revisar `EXAMPLES.md` para ejemplos detallados
2. Ejecutar con `--help` para ver ayuda CLI
3. Verificar logs de SSH: `/var/log/auth.log` (Linux)

---

## 📝 Licencia

Este proyecto es parte del sistema ESICORP para transferencia segura de archivos.

---

**Versión**: 3.0  
**Última actualización**: 2025-12-26
