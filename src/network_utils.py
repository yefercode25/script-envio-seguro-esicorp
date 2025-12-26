"""
Utilidades de red - Obtener información del sistema

Este módulo proporciona funciones para obtener información
de red del sistema actual.
"""

import socket
import getpass


def obtener_ip_local():
    """
    Obtiene la dirección IP local de la máquina.

    Returns:
        str: Dirección IP local
    """
    try:
        # Crear socket temporal para obtener IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        try:
            # Método alternativo
            hostname = socket.gethostname()
            return socket.gethostbyname(hostname)
        except Exception:
            return "127.0.0.1"


def obtener_nombre_host():
    """
    Obtiene el nombre del host de la máquina.

    Returns:
        str: Nombre del host
    """
    try:
        return socket.gethostname()
    except Exception:
        return "localhost"


def obtener_usuario_actual():
    """
    Obtiene el nombre del usuario actual del sistema.

    Returns:
        str: Nombre de usuario
    """
    try:
        return getpass.getuser()
    except Exception:
        return "usuario"


def mostrar_info_servidor():
    """
    Muestra la información del servidor para que otros se conecten.
    """
    ip_local = obtener_ip_local()
    hostname = obtener_nombre_host()
    username = obtener_usuario_actual()

    print("\n" + "=" * 60)
    print("INFORMACIÓN DEL SERVIDOR PARA CONEXIÓN SFTP")
    print("=" * 60)
    print("\n📍 Información de Red:")
    print(f"   • Nombre del Host: {hostname}")
    print(f"   • Dirección IP Local: {ip_local}")
    print(f"   • Usuario del Sistema: {username}")
    print("\n[SEC] Configuración SFTP:")
    print("   • Puerto SSH: 22 (estándar)")
    print("   • Autenticación: Llave pública RSA")
    print("\n[EDIT] Instrucciones para el Cliente:")
    print("   1. Obtener la llave pública del emisor (id_rsa.pub)")
    print(f"   2. Conectarse a este servidor como: {username}@{ip_local}")
    print("   3. Agregar llave pública a ~/.ssh/authorized_keys")
    print("   4. Configurar permisos: chmod 600 ~/.ssh/authorized_keys")
    print("\n[TIP] Ejemplo de conexión desde el cliente:")
    print(f"   python main.py --esicorp --sftp-host {ip_local} --sftp-user {username}")
    print("\n[KEY] Comando de prueba SSH:")
    print(f"   ssh {username}@{ip_local}")
    print("\n" + "=" * 60)
