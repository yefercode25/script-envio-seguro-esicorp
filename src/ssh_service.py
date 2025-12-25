"""
SSH Service Manager - Verificación y configuración de SSH

Este módulo verifica si el servicio SSH está disponible para recibir
conexiones y ofrece ayuda para configurarlo en Windows y Linux.
"""

import platform
import subprocess
import socket


def verificar_puerto_abierto(host="localhost", port=22, timeout=2):
    """
    Verifica si un puerto está abierto y escuchando.

    Args:
        host (str): Host a verificar
        port (int): Puerto a verificar
        timeout (int): Tiempo de espera en segundos

    Returns:
        bool: True si el puerto está abierto
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            return result == 0
    except Exception:
        return False


def obtener_sistema():
    """
    Obtiene el sistema operativo actual.

    Returns:
        str: 'windows', 'linux', o 'other'
    """
    sistema = platform.system().lower()
    if "windows" in sistema:
        return "windows"
    elif "linux" in sistema:
        return "linux"
    else:
        return "other"


def verificar_ssh_windows():
    """
    Verifica el estado del servicio SSH en Windows.

    Returns:
        tuple: (instalado, corriendo, mensaje)
    """
    try:
        # PRIMERO: Verificar si el servicio sshd existe (no requiere admin)
        result = subprocess.run(
            [
                "powershell",
                "-Command",
                "Get-Service -Name sshd -ErrorAction SilentlyContinue",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )

        servicio_existe = result.returncode == 0 and "sshd" in result.stdout

        if servicio_existe:
            # El servicio existe, verificar si está corriendo
            corriendo = "Running" in result.stdout

            if corriendo:
                return True, True, "SSH Server está instalado y corriendo"
            else:
                return True, False, "SSH Server está instalado pero no está corriendo"

        # SEGUNDO: Si no existe el servicio, asumir no instalado
        # (WindowsCapability requiere admin, así que lo omitimos)
        return (
            False,
            False,
            "OpenSSH Server no está instalado (servicio sshd no encontrado)",
        )

    except Exception as e:
        return False, False, f"Error al verificar SSH: {e}"


def verificar_ssh_linux():
    """
    Verifica el estado del servicio SSH en Linux.

    Returns:
        tuple: (instalado, corriendo, mensaje)
    """
    try:
        # Verificar si sshd está instalado
        result = subprocess.run(["which", "sshd"], capture_output=True, timeout=5)

        instalado = result.returncode == 0

        if not instalado:
            return False, False, "OpenSSH Server no está instalado"

        # Verificar si el servicio está corriendo
        result = subprocess.run(
            ["systemctl", "is-active", "sshd"],
            capture_output=True,
            text=True,
            timeout=5,
        )

        corriendo = result.stdout.strip() == "active"

        if not corriendo:
            # Intentar con ssh en lugar de sshd
            result = subprocess.run(
                ["systemctl", "is-active", "ssh"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            corriendo = result.stdout.strip() == "active"

        if corriendo:
            return True, True, "SSH Server está instalado y corriendo"
        else:
            return True, False, "SSH Server está instalado pero no está corriendo"

    except Exception as e:
        return False, False, f"Error al verificar SSH: {e}"


def configurar_ssh_windows():
    """
    Intenta configurar SSH en Windows.

    Returns:
        tuple: (exito, mensaje)
    """
    print("\n🔧 Intentando configurar SSH en Windows...")
    print("   Esto requiere permisos de administrador.\n")

    try:
        # Paso 1: Instalar OpenSSH Server
        print("📦 Instalando OpenSSH Server...")
        result = subprocess.run(
            [
                "powershell",
                "-Command",
                "Start-Process",
                "powershell",
                "-ArgumentList",
                '"Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0"',
                "-Verb",
                "RunAs",
                "-Wait",
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )

        if result.returncode != 0:
            return (
                False,
                "No se pudo instalar OpenSSH Server. Ejecute PowerShell como Administrador.",
            )

        print("   ✅ OpenSSH Server instalado")

        # Paso 2: Iniciar el servicio (requiere admin)
        print("🚀 Iniciando servicio SSH...")
        print("   ℹ️  Se solicitarán permisos de administrador...")

        result = subprocess.run(
            [
                "powershell",
                "-Command",
                "Start-Process",
                "powershell",
                "-ArgumentList",
                '"-Command Start-Service sshd"',
                "-Verb",
                "RunAs",
                "-Wait",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode == 0:
            print("   ✅ Servicio SSH iniciado")
        else:
            print(
                "   ⚠️  Error al iniciar servicio (puede requerir intervención manual)"
            )

        # Paso 3: Configurar inicio automático (requiere admin)
        print("⚙️  Configurando inicio automático...")

        result = subprocess.run(
            [
                "powershell",
                "-Command",
                "Start-Process",
                "powershell",
                "-ArgumentList",
                '"-Command Set-Service -Name sshd -StartupType Automatic"',
                "-Verb",
                "RunAs",
                "-Wait",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode == 0:
            print("   ✅ Inicio automático configurado")
        else:
            print("   ⚠️  Advertencia al configurar inicio automático")

        # Paso 4: Configurar firewall
        print("🔥 Configurando regla de firewall...")
        result = subprocess.run(
            [
                "powershell",
                "-Command",
                'New-NetFirewallRule -Name sshd -DisplayName "OpenSSH Server (sshd)" -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22',
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )

        # Verificar si hubo error de permisos
        if (
            "Acceso denegado" in result.stderr
            or "Access is denied" in result.stderr
            or "PermissionDenied" in result.stderr
        ):
            print(
                "   ⚠️  Regla de firewall NO creada (requiere permisos de administrador)"
            )
            return (
                True,
                "SSH instalado pero la regla de firewall requiere ejecutar como Administrador.\n💡 Ejecute: PowerShell como Administrador y ejecute:\nNew-NetFirewallRule -Name sshd -DisplayName 'OpenSSH Server' -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22",
            )
        elif "ya existe" in result.stderr or "already exists" in result.stderr:
            print("   ℹ️  Regla de firewall ya existe")
        elif result.returncode == 0:
            print("   ✅ Regla de firewall agregada")
        else:
            print(
                f"   ⚠️  Advertencia al configurar firewall (código: {result.returncode})"
            )

        return True, "SSH configurado exitosamente en Windows"

    except subprocess.TimeoutExpired:
        return False, "Timeout al configurar SSH"
    except Exception as e:
        return False, f"Error al configurar SSH: {e}"


def configurar_ssh_linux():
    """
    Muestra instrucciones para configurar SSH en Linux.

    Returns:
        tuple: (exito, mensaje)
    """
    print("\n📋 INSTRUCCIONES PARA CONFIGURAR SSH EN LINUX")
    print("=" * 60)
    print("\nEjecute los siguientes comandos con privilegios de administrador:\n")
    print("# Ubuntu/Debian:")
    print("sudo apt update")
    print("sudo apt install openssh-server -y")
    print("sudo systemctl start sshd")
    print("sudo systemctl enable sshd")
    print("sudo ufw allow 22/tcp")
    print("\n# CentOS/RHEL:")
    print("sudo yum install openssh-server -y")
    print("sudo systemctl start sshd")
    print("sudo systemctl enable sshd")
    print("sudo firewall-cmd --permanent --add-service=ssh")
    print("sudo firewall-cmd --reload")
    print("\n" + "=" * 60)

    return False, "Configuración manual requerida en Linux"


def verificar_y_configurar_ssh():
    """
    Verifica el estado de SSH y ofrece configurarlo si es necesario.

    Returns:
        bool: True si SSH está disponible
    """
    print("\n" + "=" * 60)
    print("VERIFICACIÓN DE SERVICIO SSH")
    print("=" * 60)

    sistema = obtener_sistema()
    print(f"\n🖥️  Sistema operativo: {sistema.upper()}")

    # Verificar puerto 22
    print("🔍 Verificando puerto 22...")
    puerto_abierto = verificar_puerto_abierto()

    if puerto_abierto:
        print("   ✅ Puerto 22 está abierto y escuchando")
        return True
    else:
        print("   ⚠️  Puerto 22 no está accesible")

    # Verificar servicio según el sistema
    if sistema == "windows":
        instalado, corriendo, mensaje = verificar_ssh_windows()
        print(f"\n📊 Estado: {mensaje}")

        if corriendo:
            print("   ✅ SSH está disponible para recibir conexiones")
            return True
        elif instalado and not corriendo:
            print("\n💡 El servicio está instalado pero no está corriendo.")
            configurar = input("¿Desea iniciar el servicio SSH? (s/n): ").lower()

            if configurar == "s":
                try:
                    subprocess.run(
                        ["powershell", "-Command", "Start-Service sshd"], timeout=10
                    )
                    print("✅ Servicio SSH iniciado")
                    return True
                except Exception as e:
                    print(f"❌ Error al iniciar servicio: {e}")
                    return False
        else:
            print("\n💡 SSH no está instalado.")
            configurar = input("¿Desea instalar y configurar SSH? (s/n): ").lower()

            if configurar == "s":
                exito, mensaje = configurar_ssh_windows()
                print(f"\n{mensaje}")
                return exito

    elif sistema == "linux":
        instalado, corriendo, mensaje = verificar_ssh_linux()
        print(f"\n📊 Estado: {mensaje}")

        if corriendo:
            print("   ✅ SSH está disponible para recibir conexiones")
            return True
        else:
            configurar_ssh_linux()
            input("\nPresione ENTER después de configurar SSH...")

            # Verificar nuevamente
            _, corriendo, _ = verificar_ssh_linux()
            if corriendo:
                print("✅ SSH configurado exitosamente")
                return True
    else:
        print(f"⚠️  Sistema '{sistema}' no soportado para configuración automática")

    return False


def mostrar_estado_ssh():
    """
    Muestra el estado actual del servicio SSH.
    """
    print("=" * 60)
    print("ESTADO DEL SERVICIO SSH")
    print("=" * 60)

    sistema = obtener_sistema()
    print(f"\n🖥️  Sistema: {sistema.upper()}")

    # Verificar puerto
    puerto_abierto = verificar_puerto_abierto()
    print(f"🔌 Puerto 22: {'✅ ABIERTO' if puerto_abierto else '❌ CERRADO'}")

    # Estado del servicio
    if sistema == "windows":
        instalado, corriendo, mensaje = verificar_ssh_windows()
    elif sistema == "linux":
        instalado, corriendo, mensaje = verificar_ssh_linux()
    else:
        print("\n⚠️  Sistema no soportado")
        return

    print(f"📊 Estado: {mensaje}")

    if instalado and corriendo:
        print("\n✅ SSH está listo para recibir conexiones")
    elif instalado and not corriendo:
        print("\n⚠️  SSH está instalado pero no está corriendo")
    else:
        print("\n❌ SSH no está configurado en este sistema")

    print("=" * 60)
