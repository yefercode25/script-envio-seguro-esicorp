# 📚 Ejemplos de Uso - ESICORP SFTP

Guía completa paso a paso para transferir archivos de forma segura entre dos equipos usando SFTP/SSH.

---

## 📋 Escenario

- **Equipo A (Cliente)**: Windows o Linux - Envía archivos
- **Equipo B (Servidor)**: Linux - Recibe archivos vía SFTP

---

## 🔧 PASO 1: Configuración Inicial en Ambos Equipos

### En el Equipo Cliente (A)

**Instalar dependencias:**

```powershell
# En Windows PowerShell
pip install -r requirements.txt
```

```bash
# En Linux
pip3 install -r requirements.txt
```

**Crear estructura de carpetas:**

```powershell
# Windows
New-Item -Path "salida" -ItemType Directory -Force
New-Item -Path "keys" -ItemType Directory -Force
```

```bash
# Linux
mkdir -p salida keys procesados
```

---

## 🖥️ PASO 2: Configurar el Servidor Receptor (Equipo B - Linux)

### 2.1 Instalar SSH Server (si no está instalado)

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install openssh-server

# CentOS/RHEL
sudo yum install openssh-server

# Iniciar servicio SSH
sudo systemctl start sshd
sudo systemctl enable sshd
```

### 2.2 Crear usuario ESICORP

```bash
# Crear usuario con directorio home
sudo useradd -m -s /bin/bash esicorp
sudo passwd esicorp

# Crear directorio de uploads
sudo mkdir -p /home/grupo1/upload
sudo chown esicorp:esicorp /home/grupo1/upload
sudo chmod 755 /home/grupo1/upload
```

### 2.3 Obtener información del servidor

**Modo Interactivo:**

```bash
# En el equipo servidor (Linux)
python3 main.py -i

# Seleccionar opción: 2. 📋 INFORMACIÓN DEL SERVIDOR

# Salida esperada:
============================================================
INFORMACIÓN DEL SERVIDOR PARA CONEXIÓN SFTP
============================================================

📍 Información de Red:
   • Nombre del Host: servidor-esicorp
   • Dirección IP Local: 192.168.1.100

🔐 Configuración SFTP:
   • Puerto SSH: 22 (estándar)
   • Autenticación: Llave pública RSA

📝 Instrucciones para el Cliente:
   1. Obtener la llave pública del emisor (id_rsa.pub)
   2. Agregar al archivo ~/.ssh/authorized_keys en este servidor
   3. Configurar permisos: chmod 600 ~/.ssh/authorized_keys

💡 Ejemplo de conexión desde el cliente:
   python main.py --esicorp --sftp-host 192.168.1.100 --sftp-user esicorp
============================================================
```

**Modo CLI:**

```bash
python3 main.py --info
```

**📝 Anotar esta información:**
- IP del servidor: `192.168.1.100`
- Usuario: `esicorp`
- Puerto: `22`

---

## 📤 PASO 3: Generar Llaves en el Cliente (Equipo A)

### Modo Interactivo

```powershell
# Windows
python main.py -i

# Menú:
# 1. 📤 ENVIAR ARCHIVOS (SFTP)
# 2. 📋 INFORMACIÓN DEL SERVIDOR
# 3. 🔑 GESTIÓN DE LLAVES RSA
# 4. [EXIT] SALIR

# Seleccionar: 3

# Menú de gestión:
# ⚠️  No hay llaves RSA generadas.
# 
# 1. 🔑 Generar llaves nuevas
# 2. 🔙 Volver

# Seleccionar: 1

# Salida:
🔑 Generando llaves RSA de 4096 bits...
   (Esto puede tomar unos segundos)
✅ Llaves generadas exitosamente:
   Privada: c:\...\keys\id_rsa
   Pública: c:\...\keys\id_rsa.pub

# Volver al menú y seleccionar opción 3 nuevamente
# Ahora seleccionar: 1. 👁️  Ver llave pública

============================================================
LLAVE PÚBLICA RSA:
============================================================
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQC... (muy larga)
============================================================

# COPIAR esta llave completa
```

### Modo CLI

```powershell
# Las llaves se generan automáticamente al ejecutar --esicorp
# por primera vez, o puedes forzar la generación en modo interactivo
```

---

## 🔑 PASO 4: Configurar Llave Pública en el Servidor (Equipo B)

### En el Servidor Linux

```bash
# Cambiar al usuario esicorp
su - esicorp

# Crear directorio .ssh si no existe
mkdir -p ~/.ssh
chmod 700 ~/.ssh

# Agregar la llave pública (reemplazar con la llave copiada del cliente)
echo 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQC...' >> ~/.ssh/authorized_keys

# Configurar permisos
chmod 600 ~/.ssh/authorized_keys

# Verificar
cat ~/.ssh/authorized_keys
```

---

## 📁 PASO 5: Preparar Archivos para Enviar (Equipo A)

Los archivos deben seguir el patrón: `Area-DD-MM-AAAA.Sede`

**Ejemplos válidos:**
- `Finanzas-25-12-2025.lima`
- `Compras-23-02-2023.santiago`
- `Ventas-10-11-2023.buenosaires`

```powershell
# Windows - Crear archivo de prueba
"Datos confidenciales de ESICORP" | Out-File -FilePath "salida\Finanzas-25-12-2025.lima"
```

```bash
# Linux
echo "Datos confidenciales de ESICORP" > salida/Finanzas-25-12-2025.lima
```

---

## 🚀 PASO 6: Enviar Archivos

### Opción A: Modo Interactivo

```powershell
# En el equipo cliente
python main.py -i

# Seleccionar: 1. 📤 ENVIAR ARCHIVOS (SFTP)

# El script mostrará:
============================================================
PASO 1: VERIFICACIÓN DE LLAVES RSA
============================================================
✅ Llaves RSA encontradas

============================================================
PASO 2: BÚSQUEDA Y PROCESAMIENTO DE ARCHIVOS
============================================================
✅ Encontrados 1 archivo(s):
   • Finanzas-25-12-2025.lima

📄 Procesando: Finanzas-25-12-2025.lima
------------------------------------------------------------
🔍 [INTEGRIDAD] Calculando hash SHA-256...
   ✅ Hash: e3b0c44298fc1c149afbf4c8996f...
📝 [CODIFICACIÓN] Convirtiendo a Base64...
   ✅ Archivo codificado (568 bytes)
🔐 [CONFIDENCIALIDAD] Cifrando con AES-256-CBC...
   ✅ Cifrado (576 bytes)
📦 [EMPAQUETADO] Creando archivo ZIP...
   ✅ ZIP creado: Finanzas-25-12-2025.zip
   Tamaño: 1338 bytes
✅ Procesamiento completado
============================================================

============================================================
PASO 3: CONFIGURACIÓN Y ENVÍO SFTP
============================================================

>> IP del servidor SFTP: 192.168.1.100
>> Usuario SFTP: esicorp
>> Puerto SFTP [22]: 
>> Ruta remota [/home/grupo1/upload/]: 

🔌 Conectando a esicorp@192.168.1.100:22...
✅ Conexión SFTP establecida exitosamente

📤 Subiendo: Finanzas-25-12-2025.zip
   Destino: /home/grupo1/upload/Finanzas-25-12-2025.zip
   ✅ Subido exitosamente (1338 bytes)

============================================================
✅ Resultado: 1/1 archivos enviados
============================================================

🎉 ¡PROCESO COMPLETADO EXITOSAMENTE!
```

### Opción B: Modo CLI

```powershell
# Windows - Envío automático
python main.py --esicorp --sftp-host 192.168.1.100 --sftp-user esicorp

# Con puerto y ruta personalizados
python main.py --esicorp `
    --sftp-host 192.168.1.100 `
    --sftp-user esicorp `
    --sftp-port 22 `
    --sftp-path /home/grupo1/upload/
```

```bash
# Linux - Envío automático
python3 main.py --esicorp --sftp-host 192.168.1.100 --sftp-user esicorp

# Con configuración completa
python3 main.py --esicorp \
    --sftp-host 192.168.1.100 \
    --sftp-user esicorp \
    --sftp-port 22 \
    --sftp-path /home/grupo1/upload/
```

---

## ✅ PASO 7: Verificar Recepción en el Servidor (Equipo B)

```bash
# En el servidor Linux
ls -lh /home/grupo1/upload/

# Salida esperada:
-rw-r--r-- 1 esicorp esicorp 1.3K Dec 25 13:00 Finanzas-25-12-2025.zip

# Verificar contenido del ZIP
unzip -l /home/grupo1/upload/Finanzas-25-12-2025.zip

# Salida:
Archive:  Finanzas-25-12-2025.zip
  Length      Date    Time    Name
---------  ---------- -----   ----
      592  12-25-2025 13:00   Finanzas-25-12-2025.enc
       89  12-25-2025 13:00   Finanzas-25-12-2025.hash.txt
      194  12-25-2025 13:00   metadata.txt
---------                     -------
      875                     3 files
```

---

## 🔓 PASO 8 (Opcional): Desencriptar en el Servidor

> **NOTA**: Actualmente, el script NO incluye funcionalidad de desencriptado. Los archivos `.enc` contienen:
> - Primeros 16 bytes: IV (Vector de inicialización)
> - Siguientes 32 bytes: Clave AES-256
> - Resto: Datos cifrados con AES-256-CBC

Para uso en producción, se recomienda:
1. Transmitir la clave AES por un canal separado
2. Implementar un script de desencriptado en el servidor
3. O usar cifrado asimétrico (RSA) para la clave AES

---

## 🔄 Ejemplo Completo: Transferencia entre Dos Oficinas

### Escenario Real

**Oficina Lima (Cliente)** → **Oficina Santiago (Servidor)**

#### En Santiago (Servidor - 192.168.10.50)

```bash
# 1. Verificar servicio SSH
sudo systemctl status sshd

# 2. Obtener IP del servidor
python3 main.py --info

# 3. Crear directorio para recibir
mkdir -p /home/grupo1/upload
chmod 755 /home/grupo1/upload
```

#### En Lima (Cliente)

```powershell
# 1. Colocar archivos en ./salida
Copy-Item "C:\Documentos\Finanzas-25-12-2025.lima" -Destination ".\salida\"

# 2. Generar llaves (modo interactivo)
python main.py -i
# Opción 3 → Opción 1 (Generar llaves)
# Opción 3 → Opción 1 (Ver llave pública) → COPIAR

# 3. Enviar llave pública a Santiago (por email seguro o USB)
# Copiar contenido de: keys\id_rsa.pub

# 4. Esperar confirmación de Santiago que agregaron la llave
```

#### En Santiago (configurar llave)

```bash
# Recibir llave pública de Lima y agregarla
echo 'ssh-rsa AAAAB...[llave de Lima]' >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

#### En Lima (enviar archivos)

**Modo Interactivo:**
```powershell
python main.py -i
# Opción 1: ENVIAR ARCHIVOS
# IP: 192.168.10.50
# Usuario: esicorp
# Puerto: 22
# Ruta: /home/grupo1/upload/
```

**Modo CLI:**
```powershell
python main.py --esicorp `
    --sftp-host 192.168.10.50 `
    --sftp-user esicorp
```

#### En Santiago (verificar)

```bash
ls -lh /home/grupo1/upload/
# Debe aparecer: Finanzas-25-12-2025.zip
```

---

## 🛠️ Solución de Problemas

### Error: "AuthenticationFailed"

**Causa**: La llave pública no está configurada correctamente.

**Solución**:
```bash
# En el servidor, verificar
cat ~/.ssh/authorized_keys
# Debe contener la llave pública del cliente

# Verificar permisos
ls -la ~/.ssh/
# Debe mostrar:
# drwx------ 2 esicorp esicorp 4096 ... .ssh
# -rw------- 1 esicorp esicorp  xxx ... authorized_keys
```

### Error: "Connection refused"

**Causa**: SSH no está ejecutándose o firewall bloqueando.

**Solución**:
```bash
# Verificar SSH
sudo systemctl status sshd

# Verificar puerto
sudo netstat -tlnp | grep :22

# Permitir en firewall (Ubuntu)
sudo ufw allow 22/tcp
```

### Error: "No se encontraron archivos"

**Causa**: Archivos no cumplen el patrón `Area-DD-MM-AAAA.Sede`.

**Ejemplos correctos**:
- ✅ `Finanzas-25-12-2025.lima`
- ✅ `Ventas-01-01-2024.santiago`
- ❌ `reporte.txt` (no cumple patrón)
- ❌ `Ventas-2025.lima` (fecha incompleta)

---

## 📊 Resumen de Comandos Rápidos

### Ver información del servidor
```bash
python main.py --info
```

### Enviar archivos (CLI)
```bash
python main.py --esicorp --sftp-host <IP> --sftp-user <usuario>
```

### Modo interactivo completo
```bash
python main.py -i
```

### Verificar recepción
```bash
ls -lh /home/grupo1/upload/
```

---

## 🔐 Checklist de Seguridad

Antes de usar en producción, verificar:

- [ ] Llaves RSA de 4096 bits generadas
- [ ] Llave pública agregada a `authorized_keys` en servidor
- [ ] Permisos correctos en `.ssh` (700) y `authorized_keys` (600)
- [ ] Firewall configurado para permitir SSH (puerto 22)
- [ ] Usuario ESICORP tiene permisos en directorio de uploads
- [ ] Red entre cliente y servidor es segura (VPN recomendada)
- [ ] Archivos originales se respaldan antes de enviar
- [ ] Implementar sistema de desencriptado en servidor

---

**Última actualización**: Diciembre 2025
**Versión**: 3.0 (SFTP-Only)
