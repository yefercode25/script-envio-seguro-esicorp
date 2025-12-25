"""
Función combinada para mostrar info de servidor y SSH sin limpieza de pantalla
"""


def mostrar_info_completa():
    """
    Muestra toda la información del servidor y SSH en una sola salida
    para evitar que se borre la pantalla entre llamadas.
    """
    from src.network_utils import (
        obtener_ip_local,
        obtener_nombre_host,
        obtener_usuario_actual,
    )
    from src.ssh_service import (
        verificar_puerto_abierto,
        verificar_ssh_windows,
        obtener_sistema,
    )

    # Recolectar toda la información primero
    ip_local = obtener_ip_local()
    hostname = obtener_nombre_host()
    username = obtener_usuario_actual()
    sistema = obtener_sistema()
    puerto_abierto = verificar_puerto_abierto()

    if sistema == "windows":
        instalado, corriendo, mensaje_ssh = verificar_ssh_windows()
    else:
        instalado, corriendo, mensaje_ssh = False, False, "Sistema no Windows"

    # Mostrar TODO junto
    print("\n" + "=" * 60)
    print("INFORMACIÓN DEL SERVIDOR PARA CONEXIÓN SFTP")
    print("=" * 60)
    print("\n📍 Información de Red:")
    print(f"   • Nombre del Host: {hostname}")
    print(f"   • Dirección IP Local: {ip_local}")
    print(f"   • Usuario del Sistema: {username}")
    print("\n🔐 Configuración SFTP:")
    print("   • Puerto SSH: 22 (estándar)")
    print("   • Autenticación: Llave pública RSA")
    print("\n📝 Instrucciones para el Cliente:")
    print("   1. Obtener la llave pública del emisor (id_rsa.pub)")
    print(f"   2. Conectarse a este servidor como: {username}@{ip_local}")
    print("   3. Agregar llave pública a ~/.ssh/authorized_keys")
    print("   4. Configurar permisos: chmod 600 ~/.ssh/authorized_keys")
    print("\n💡 Ejemplo de conexión desde el cliente:")
    print(f"   python main.py --esicorp --sftp-host {ip_local} --sftp-user {username}")
    print("\n🔑 Comando de prueba SSH:")
    print(f"   ssh {username}@{ip_local}")

    # Estado de SSH
    print("\n" + "=" * 60)
    print("ESTADO DEL SERVICIO SSH")
    print("=" * 60)
    print(f"\n🖥️  Sistema: {sistema.upper()}")
    print(f"🔌 Puerto 22: {'✅ ABIERTO' if puerto_abierto else '❌ CERRADO'}")
    print(f"📊 Estado: {mensaje_ssh}")

    if instalado and corriendo:
        print("\n✅ SSH está listo para recibir conexiones")
    elif instalado and not corriendo:
        print("\n⚠️  SSH está instalado pero no está corriendo")
    else:
        print("\n❌ SSH no está configurado en este sistema")

    print("=" * 60)

    return instalado, corriendo
