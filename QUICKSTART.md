# 🚀 ESICORP - Guía Rápida de Inicio

## ▶️ Iniciar el Sistema

```bash
python main.py -i
```

## 📋 Opciones del Menú Principal

### 1️⃣ ENVIAR ARCHIVOS (SFTP)

**Flujo completo de envío:**

1. **Verificación de llaves** - Si no existen, las genera automáticamente
2. **Selección de archivos:**
   - Opción 1: Buscar en `./salida` (patrón Area-DD-MM-AAAA.Sede)
   - Opción 2: Seleccionar manualmente
     - Ingresar ruta
     - Diálogo de archivo
     - Diálogo de carpeta
3. **Procesamiento automático:**
   - Calcula hash SHA-256
   - Codifica en Base64
   - Cifra con AES-256-CBC
   - Crea archivo ZIP
4. **Configuración SFTP:**
   - IP del servidor
   - Usuario
   - Puerto (default: 22)
   - Ruta remota
5. **Transferencia segura** vía SFTP

### 2️⃣ INFORMACIÓN DEL SERVIDOR

Muestra:
- 🖥️ Nombre del host
- 🌐 Dirección IP local
- 🔌 Estado del puerto 22
- 📊 Estado del servicio SSH
- 📝 Instrucciones para clientes

**Opcional:** Configurar SSH si no está disponible

### 3️⃣ GESTIÓN DE LLAVES RSA

- 👁️ Ver llave pública (para copiar al servidor)
- 🔄 Regenerar llaves (invalidará la actual)
- 🔑 Generar primera vez

### 4️⃣ VERIFICAR/CONFIGURAR SSH

**En Windows:**
- Detecta si OpenSSH Server está instalado
- Ofrece instalarlo automáticamente
- Inicia el servicio
- Configura inicio automático
- Agrega regla de firewall

**En Linux:**
- Muestra comandos para Ubuntu/Debian
- Muestra comandos para CentOS/RHEL
- Guía de configuración completa

### 5️⃣ SALIR

Cierra el programa

---

## 💡 Ejemplo de Uso Completo

### Preparación (Primera Vez)

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Iniciar el sistema
python main.py -i

# 3. Generar llaves (Opción 3)
# Seleccionar: 1. Generar llaves nuevas

# 4. Ver llave pública (Opción 3)
# Seleccionar: 1. Ver llave pública
# → COPIAR el contenido completo
```

### En el Servidor Linux

```bash
# Configurar SSH (si no está instalado)
sudo apt update
sudo apt install openssh-server -y
sudo systemctl start sshd
sudo systemctl enable sshd

# Crear usuario
sudo useradd -m -s /bin/bash esicorp
sudo mkdir -p /home/esicorp/uploads
sudo chown esicorp:esicorp /home/esicorp/uploads

# Agregar llave pública
su - esicorp
mkdir -p ~/.ssh
echo 'ssh-rsa AAAAB...[LLAVE_COPIADA]' >> ~/.ssh/authorized_keys
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys

# Permitir SSH en firewall
sudo ufw allow 22/tcp
```

### Enviar Archivos

```bash
# 1. Colocar archivos en ./salida
# Ejemplo: Finanzas-25-12-2025.lima

# 2. Ejecutar main.py
python main.py -i

# 3. Opción 1: ENVIAR ARCHIVOS

# 4. Opción 1: Usar archivos de ./salida

# 5. Configurar conexión:
# IP: 192.168.1.100
# Usuario: esicorp
# Puerto: 22
# Ruta: /home/esicorp/uploads/

# 6. ¡Archivo enviado!
```

### Verificar en Servidor

```bash
ls -lh /home/esicorp/uploads/
# Debería mostrar: Finanzas-25-12-2025.zip

# Ver contenido del ZIP
unzip -l /home/esicorp/uploads/Finanzas-25-12-2025.zip
# Contendrá:
# - Finanzas-25-12-2025.enc (archivo cifrado)
# - Finanzas-25-12-2025.hash.txt (hash SHA-256)
# - metadata.txt (información del procesamiento)
```

---

## 🎯 Modo CLI (Automático)

### Envío Automático

```bash
# Básico
python main.py --esicorp --sftp-host 192.168.1.100 --sftp-user esicorp

# Completo
python main.py --esicorp \
    --sftp-host 192.168.1.100 \
    --sftp-user esicorp \
    --sftp-port 22 \
    --sftp-path /home/esicorp/uploads/
```

### Mostrar Info del Servidor

```bash
python main.py --info
```

---

## 🔒 Patrón de Archivos ESICORP

**Formato requerido:** `Area-DD-MM-AAAA.Sede`

**Ejemplos válidos:**
- ✅ `Finanzas-25-12-2025.lima`
- ✅ `Compras-23-02-2023.santiago`
- ✅ `Ventas-10-11-2023.buenosaires`
- ✅ `RH-01-01-2024.bogota`

**Ejemplos inválidos:**
- ❌ `reporte.txt` (no sigue patrón)
- ❌ `Ventas-2025.lima` (fecha incompleta)
- ❌ `Finanzas_25_12_2025.lima` (usa _ en lugar de -)

**Nota:** Si no hay archivos con el patrón, el sistema ofrece procesar cualquier archivo con una advertencia.

---

## 🛠️ Solución de Problemas

### Error: "No se pudieron generar las llaves"
- Verificar permisos de escritura en `./keys`
- Ejecutar como administrador en Windows

### Error: "AuthenticationFailed"
- Verificar que la llave pública esté en `~/.ssh/authorized_keys` del servidor
- Verificar permisos: `chmod 600 ~/.ssh/authorized_keys`
- Verificar que el usuario sea correcto

### Error: "Connection refused"
- Verificar que SSH esté corriendo: `sudo systemctl status sshd`
- Verificar firewall: `sudo ufw status`
- Verificar que el puerto sea 22 o el configurado

### Error: "No se encontraron archivos"
- Verificar que haya archivos en `./salida`
- Verificar que sigan el patrón correcto
- O usar opción 2 para seleccionar manualmente

### SSH no está configurado
- En Windows: Usar opción 4 del menú para instalarlo automáticamente
- En Linux: Seguir las instrucciones mostradas

---

## 📞 Información Adicional

**Estructura de seguridad:**
1. **RSA 4096 bits** - Autenticación SFTP
2. **SHA-256** - Verificación de integridad
3. **Base64** - Codificación
4. **AES-256-CBC** - Cifrado de contenido
5. **ZIP** - Empaquetado final

**Archivos generados:**
- `keys/id_rsa` - Llave privada (NO compartir)
- `keys/id_rsa.pub` - Llave pública (compartir con servidor)
- `procesados/*.zip` - Archivos procesados listos para enviar

**Documentación completa:**
- `README.md` - Documentación técnica
- `EXAMPLES.md` - Ejemplos detallados
- `walkthrough.md` - Registro completo del proyecto

---

**¡Listo para usar! 🎉**
