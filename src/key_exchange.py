"""
Módulo de Intercambio Automático de Llaves RSA
===============================================

Este módulo permite el intercambio automático de llaves públicas RSA
entre dos máquinas usando sockets TCP.

Autor: ESICORP - UNAD
Fecha: 2025-12-26
"""

import socket
import json
import os
import platform
import hashlib
import subprocess
from pathlib import Path
from datetime import datetime

# Directorio del proyecto (donde está main.py)
PROJECT_ROOT = Path(__file__).parent.parent
KEYS_DIR = PROJECT_ROOT / "keys"


# ============================================================================
# CONFIGURACIÓN
# ============================================================================

PUERTO_DEFAULT = 5555
TIMEOUT_CONEXION = 30  # segundos
TIMEOUT_INTERCAMBIO = 60  # segundos
BUFFER_SIZE = 4096


# ============================================================================
# UTILIDADES MULTIPLATAFORMA
# ============================================================================


def obtener_ruta_ssh():
    """
    Obtiene la ruta del directorio .ssh según el sistema operativo.

    Returns:
        Path: Ruta al directorio .ssh
    """
    sistema = platform.system().lower()

    if sistema == "windows":
        ssh_dir = Path.home() / ".ssh"
    else:  # Linux/Mac
        ssh_dir = Path.home() / ".ssh"

    return ssh_dir


def crear_directorio_ssh():
    """
    Crea el directorio .ssh si no existe y configura permisos apropiados.

    Returns:
        tuple: (exito, mensaje)
    """
    ssh_dir = obtener_ruta_ssh()

    try:
        if not ssh_dir.exists():
            print(f"📁 Creando directorio: {ssh_dir}")
            ssh_dir.mkdir(mode=0o700, parents=True)

        # Configurar permisos según el sistema
        sistema = platform.system().lower()

        if sistema == "windows":
            # En Windows usar icacls
            try:
                subprocess.run(
                    ["icacls", str(ssh_dir), "/inheritance:r"],
                    capture_output=True,
                    check=True,
                )
                subprocess.run(
                    [
                        "icacls",
                        str(ssh_dir),
                        f"/grant:r {os.getenv('USERNAME')}:(OI)(CI)F",
                    ],
                    capture_output=True,
                    check=True,
                )
                print(f"🔒 Permisos configurados en Windows")
            except Exception as e:
                print(f"⚠️  Advertencia al configurar permisos: {e}")
        else:
            # En Linux/Mac usar chmod
            os.chmod(ssh_dir, 0o700)
            print(f"🔒 Permisos configurados (chmod 700)")

        return True, f"Directorio .ssh verificado: {ssh_dir}"

    except Exception as e:
        return False, f"Error al crear directorio .ssh: {e}"


def configurar_permisos_archivo(archivo_path):
    """
    Configura permisos apropiados para un archivo en .ssh

    Args:
        archivo_path (Path): Ruta al archivo
    """
    sistema = platform.system().lower()

    try:
        if sistema == "windows":
            # Windows: solo el usuario actual
            subprocess.run(
                ["icacls", str(archivo_path), "/inheritance:r"],
                capture_output=True,
                check=True,
            )
            subprocess.run(
                ["icacls", str(archivo_path), f"/grant:r {os.getenv('USERNAME')}:F"],
                capture_output=True,
                check=True,
            )
        else:
            # Linux/Mac: chmod 600
            os.chmod(archivo_path, 0o600)

    except Exception as e:
        print(f"⚠️  Advertencia al configurar permisos de {archivo_path.name}: {e}")


# ============================================================================
# VALIDACIÓN DE LLAVES
# ============================================================================


def validar_llave_publica(llave_contenido):
    """
    Valida que una llave pública tenga formato correcto.

    Args:
        llave_contenido (str): Contenido de la llave pública

    Returns:
        tuple: (es_valida, tipo_llave, bits)
    """
    try:
        partes = llave_contenido.strip().split()

        if len(partes) < 2:
            return False, None, None

        tipo_llave = partes[0]

        # Validar tipo de llave
        tipos_validos = ["ssh-rsa", "ssh-ed25519", "ecdsa-sha2-nistp256"]
        if tipo_llave not in tipos_validos:
            return False, tipo_llave, None

        # Para RSA, intentar determinar bits (aproximación)
        if tipo_llave == "ssh-rsa":
            # La longitud del contenido base64 da una idea del tamaño
            contenido_b64 = partes[1]
            bits_aprox = len(contenido_b64) * 6 // 8  # Aproximación
            return True, tipo_llave, bits_aprox

        return True, tipo_llave, None

    except Exception as e:
        return False, None, None


def calcular_fingerprint(llave_contenido):
    """
    Calcula el fingerprint SHA256 de una llave pública.

    Args:
        llave_contenido (str): Contenido de la llave pública

    Returns:
        str: Fingerprint en formato SHA256:xxxxx...
    """
    try:
        # Extraer la parte base64 de la llave
        partes = llave_contenido.strip().split()
        if len(partes) < 2:
            return "INVALID"

        import base64

        llave_bytes = base64.b64decode(partes[1])
        hash_obj = hashlib.sha256(llave_bytes)
        fingerprint = hash_obj.hexdigest()

        # Formato: SHA256:primeros16caracteres...
        return f"SHA256:{fingerprint[:16]}...{fingerprint[-8:]}"

    except Exception as e:
        return "ERROR"


# ============================================================================
# PROTOCOLO DE COMUNICACIÓN
# ============================================================================


def crear_mensaje(tipo, datos):
    """
    Crea un mensaje JSON para el protocolo de intercambio.

    Args:
        tipo (str): Tipo de mensaje (HANDSHAKE, PUBLIC_KEY, ACK, ERROR)
        datos (dict): Datos del mensaje

    Returns:
        bytes: Mensaje JSON codificado
    """
    mensaje = {"tipo": tipo, "timestamp": datetime.now().isoformat(), "datos": datos}
    return json.dumps(mensaje).encode("utf-8")


def recibir_mensaje(conexion, timeout=TIMEOUT_INTERCAMBIO):
    """
    Recibe un mensaje JSON de la conexión.

    Args:
        conexion: Socket de conexión
        timeout (int): Timeout en segundos

    Returns:
        dict: Mensaje decodificado o None si error
    """
    try:
        conexion.settimeout(timeout)
        datos = conexion.recv(BUFFER_SIZE)

        if not datos:
            return None

        mensaje = json.loads(datos.decode("utf-8"))
        return mensaje

    except socket.timeout:
        print("⏱️  Timeout al recibir mensaje")
        return None
    except json.JSONDecodeError:
        print("❌ Error al decodificar mensaje JSON")
        return None
    except Exception as e:
        print(f"❌ Error al recibir mensaje: {e}")
        return None


# ============================================================================
# CONFIGURACIÓN DE LLAVES EN EL SISTEMA
# ============================================================================


def agregar_a_authorized_keys(llave_publica, info_remota):
    """
    Agrega una llave pública a authorized_keys.

    Args:
        llave_publica (str): Contenido de la llave pública
        info_remota (dict): Información del host remoto

    Returns:
        tuple: (exito, mensaje)
    """
    try:
        # Crear directorio .ssh si no existe
        exito, msg = crear_directorio_ssh()
        if not exito:
            return False, msg

        ssh_dir = obtener_ruta_ssh()
        authorized_keys = ssh_dir / "authorized_keys"

        print(f"\n📝 Configurando authorized_keys...")
        print(f"   Archivo: {authorized_keys}")

        # Leer archivo existente
        llaves_existentes = []
        if authorized_keys.exists():
            with open(authorized_keys, "r") as f:
                llaves_existentes = f.readlines()

        # Verificar si la llave ya existe
        llave_limpia = llave_publica.strip()
        for llave_existente in llaves_existentes:
            if llave_limpia in llave_existente:
                print(f"   ℹ️  Llave ya existe en authorized_keys")
                return True, "Llave ya configurada previamente"

        # Agregar nueva llave con comentario
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        comentario = f"# Agregada vía intercambio automático: {info_remota.get('hostname', 'unknown')} ({timestamp})\n"

        with open(authorized_keys, "a") as f:
            f.write(comentario)
            f.write(llave_publica.strip() + "\n")

        print(f"   ✅ Llave agregada a authorized_keys")

        # Configurar permisos
        print(f"   🔒 Configurando permisos...")
        configurar_permisos_archivo(authorized_keys)
        print(f"   ✅ Permisos configurados")

        return True, f"Llave agregada exitosamente a {authorized_keys}"

    except Exception as e:
        return False, f"Error al agregar llave: {e}"


def agregar_a_known_hosts(ip_servidor, llave_publica, info_remota):
    """
    Agrega una llave pública a known_hosts (para el cliente).

    Args:
        ip_servidor (str): IP del servidor
        llave_publica (str): Contenido de la llave pública del servidor
        info_remota (dict): Información del servidor

    Returns:
        tuple: (exito, mensaje)
    """
    try:
        # Crear directorio .ssh si no existe
        exito, msg = crear_directorio_ssh()
        if not exito:
            return False, msg

        ssh_dir = obtener_ruta_ssh()
        known_hosts = ssh_dir / "known_hosts"

        print(f"\n📝 Configurando known_hosts...")
        print(f"   Archivo: {known_hosts}")

        # Formato: ip tipo_llave contenido_base64
        partes = llave_publica.strip().split()
        if len(partes) >= 2:
            entrada = f"{ip_servidor} {partes[0]} {partes[1]}\n"
        else:
            return False, "Formato de llave inválido"

        # Leer archivo existente
        entradas_existentes = []
        if known_hosts.exists():
            with open(known_hosts, "r") as f:
                entradas_existentes = f.readlines()

        # Remover entradas antiguas de esta IP
        entradas_filtradas = [
            e for e in entradas_existentes if not e.startswith(ip_servidor + " ")
        ]

        # Agregar nueva entrada
        with open(known_hosts, "w") as f:
            f.writelines(entradas_filtradas)
            f.write(
                f"# {info_remota.get('hostname', 'unknown')} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            )
            f.write(entrada)

        print(f"   ✅ Servidor agregado a known_hosts")

        # Configurar permisos
        configurar_permisos_archivo(known_hosts)

        return True, f"Servidor {ip_servidor} agregado a known_hosts"

    except Exception as e:
        return False, f"Error al configurar known_hosts: {e}"


# Continuación de src/key_exchange.py

# ============================================================================
# MODO SERVIDOR - Intercambio de Llaves
# ============================================================================


def intercambiar_llaves_servidor(conexion, usuario_local):
    """
    Realiza el intercambio de llaves desde el lado del servidor.

    Args:
        conexion: Socket de conexión con el cliente
        usuario_local (str): Usuario local del sistema

    Returns:
        bool: True si el intercambio fue exitoso
    """
    try:
        from src.network_utils import obtener_ip_local, obtener_nombre_host

        print(f"\n{'═' * 60}")
        print("INICIANDO INTERCAMBIO DE LLAVES")
        print(f"{'═' * 60}")

        # ========== FASE 1: HANDSHAKE ==========
        print(f"\n🔄 FASE 1: Intercambio de información")
        print(f"   📡 Enviando información del servidor...")

        hostname = obtener_nombre_host()
        sistema = platform.system().lower()

        info_servidor = {
            "hostname": hostname,
            "usuario": usuario_local,
            "sistema": sistema,
        }

        mensaje_handshake = crear_mensaje("HANDSHAKE", info_servidor)
        conexion.send(mensaje_handshake)
        print(f"   ✅ Información enviada")

        # Recibir handshake del cliente
        print(f"   📥 Recibiendo información del cliente...")
        mensaje_cliente = recibir_mensaje(conexion)

        if not mensaje_cliente or mensaje_cliente.get("tipo") != "HANDSHAKE":
            print(f"   ❌ Error: Handshake inválido")
            return False

        info_cliente = mensaje_cliente.get("datos", {})
        print(f"   ✅ Información recibida:")
        print(f"      • Hostname: {info_cliente.get('hostname', 'unknown')}")
        print(f"      • Usuario: {info_cliente.get('usuario', 'unknown')}")
        print(f"      • Sistema: {info_cliente.get('sistema', 'unknown').upper()}")

        # ========== FASE 2: INTERCAMBIO DE LLAVES PÚBLICAS ==========
        print(f"\n🔄 FASE 2: Intercambio de llaves públicas")

        # Leer nuestra llave pública desde ./keys/
        print("   📖 Leyendo llave pública del servidor...")
        llave_pub_path = KEYS_DIR / "id_rsa.pub"

        if not llave_pub_path.exists():
            print("   ❌ Error: No se encontró la llave pública")
            print(f"      Buscada en: {llave_pub_path}")
            print(f"      💡 Genera las llaves primero con Opción 3")
            return False

        with open(llave_pub_path, "r") as f:
            llave_publica_servidor = f.read().strip()

        print(f"   ✅ Llave pública leída ({len(llave_publica_servidor)} bytes)")

        # Enviar nuestra llave pública
        print(f"   📤 Enviando llave pública del servidor...")
        mensaje_llave = crear_mensaje(
            "PUBLIC_KEY",
            {
                "llave_publica": llave_publica_servidor,
                "hostname": hostname,
                "usuario": usuario_local,
            },
        )
        conexion.send(mensaje_llave)
        print(f"   ✅ Llave enviada")

        # Recibir llave pública del cliente
        print(f"   📥 Recibiendo llave pública del cliente...")
        mensaje_llave_cliente = recibir_mensaje(conexion)

        if (
            not mensaje_llave_cliente
            or mensaje_llave_cliente.get("tipo") != "PUBLIC_KEY"
        ):
            print(f"   ❌ Error: Mensaje de llave inválido")
            return False

        llave_publica_cliente = mensaje_llave_cliente.get("datos", {}).get(
            "llave_publica", ""
        )

        if not llave_publica_cliente:
            print(f"   ❌ Error: Llave pública vacía")
            return False

        print(f"   ✅ Llave recibida ({len(llave_publica_cliente)} bytes)")

        # Validar llave del cliente
        print(f"\n   🔍 Validando llave del cliente...")
        es_valida, tipo_llave, bits = validar_llave_publica(llave_publica_cliente)

        if not es_valida:
            print(f"   ❌ Llave inválida")
            return False

        print(f"   ✅ Llave válida:")
        print(f"      • Tipo: {tipo_llave}")
        if bits:
            print(f"      • Tamaño aprox: {bits} bits")

        # Mostrar fingerprint
        fingerprint = calcular_fingerprint(llave_publica_cliente)
        print(f"\n   🔎 Fingerprint de la llave del cliente:")
        print(f"      {fingerprint}")

        # ========== FASE 3: CONFIRMACIÓN DEL USUARIO ==========
        print(f"\n{'═' * 60}")
        print(f"CONFIRMACIÓN REQUERIDA")
        print(f"{'═' * 60}")
        print(f"\nEst a punto de agregar la llave del cliente a authorized_keys.")
        print(f"Esto permitirá que el cliente se conecte vía SSH sin contraseña.")
        print(f"\nDetalles del cliente:")
        print(f"  • Usuario: {info_cliente.get('usuario', 'unknown')}")
        print(f"  • Hostname: {info_cliente.get('hostname', 'unknown')}")
        print(f"  • Sistema: {info_cliente.get('sistema', 'unknown').upper()}")
        print(f"  • Fingerprint: {fingerprint}")

        respuesta = input(
            f"\n¿Desea agregar esta llave a authorized_keys? (s/n): "
        ).lower()

        if respuesta != "s":
            print(f"\n❌ Intercambio cancelado por el usuario")
            mensaje_error = crear_mensaje("ERROR", {"razon": "Cancelado por usuario"})
            conexion.send(mensaje_error)
            return False

        # ========== FASE 4: CONFIGURACIÓN DE LLAVES ==========
        print(f"\n🔄 FASE 3: Configuración de llaves")

        # Agregar llave del cliente a authorized_keys
        exito, mensaje = agregar_a_authorized_keys(llave_publica_cliente, info_cliente)

        if not exito:
            print(f"   ❌ {mensaje}")
            mensaje_error = crear_mensaje("ERROR", {"razon": mensaje})
            conexion.send(mensaje_error)
            return False

        print(f"   ✅ {mensaje}")

        # ========== FASE 5: CONFIRMACIÓN FINAL ==========
        print(f"\n🔄 FASE 4: Confirmación")
        print(f"   📡 Enviando confirmación al cliente...")

        mensaje_ack = crear_mensaje(
            "ACK",
            {
                "estado": "exito",
                "mensaje": "Llave configurada correctamente en el servidor",
            },
        )
        conexion.send(mensaje_ack)
        print(f"   ✅ Confirmación enviada")

        # Esperar confirmación del cliente
        print(f"   📥 Esperando confirmación del cliente...")
        mensaje_ack_cliente = recibir_mensaje(conexion, timeout=30)

        if mensaje_ack_cliente and mensaje_ack_cliente.get("tipo") == "ACK":
            print(f"   ✅ Cliente confirmó configuración exitosa")
        else:
            print(f"   ⚠️  No se recibió confirmación del cliente")

        return True

    except Exception as e:
        print(f"\n❌ Error durante el intercambio: {e}")
        return False


def modo_servidor_intercambio(puerto=PUERTO_DEFAULT):
    """
    Inicia el modo servidor para recibir conexiones de intercambio de llaves.

    Args:
        puerto (int): Puerto en el que escuchar

    Returns:
        bool: True si el intercambio fue exitoso
    """
    from src.network_utils import (
        obtener_ip_local,
        obtener_nombre_host,
        obtener_usuario_actual,
    )
    from src.sftp_manager import SFTPManager

    print(f"\n{'═' * 60}")
    print("MODO SERVIDOR - INTERCAMBIO AUTOMÁTICO DE LLAVES RSA")
    print(f"{'═' * 60}")

    # Verificar/generar llaves
    print(f"\n🔍 Verificando llaves RSA locales...")
    sftp_mgr = SFTPManager()

    if not sftp_mgr.verificar_llaves():
        print(f"⚠️  Generando nuevas llaves...")
        sftp_mgr.generar_llaves()

    print(f"✅ Llaves RSA disponibles")

    # Mostrar información del servidor
    ip_local = obtener_ip_local()
    hostname = obtener_nombre_host()
    usuario = obtener_usuario_actual()
    sistema = platform.system()

    print(f"\n📍 Información del servidor:")
    print(f"   • IP Local: {ip_local}")
    print(f"   • Hostname: {hostname}")
    print(f"   • Usuario: {usuario}")
    print(f"   • Sistema: {sistema}")

    # Iniciar servidor socket
    print(f"\n🔌 Iniciando servidor en puerto {puerto}...")

    try:
        servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        servidor.bind(("0.0.0.0", puerto))
        servidor.listen(1)
        servidor.settimeout(300)  # 5 minutos

        print(f"✅ Servidor escuchando en {ip_local}:{puerto}")
        print(f"\n💡 Comparta esta información con el cliente:")
        print(f"{'─' * 60}")
        print(f"  IP del Servidor: {ip_local}")
        print(f"  Puerto: {puerto}")
        print(f"{'─' * 60}")
        print(f"\n⏳ Esperando conexión del cliente...")
        print(f"   (Timeout en 5 minutos)")

        # Aceptar conexión
        conexion, direccion_cliente = servidor.accept()
        ip_cliente = direccion_cliente[0]

        print(f"\n✅ Cliente conectado desde: {ip_cliente}")

        # Realizar intercambio
        exito = intercambiar_llaves_servidor(conexion, usuario)

        conexion.close()
        servidor.close()

        if exito:
            print(f"\n{'═' * 60}")
            print(f"🎉 ¡INTERCAMBIO COMPLETADO EXITOSAMENTE!")
            print(f"{'═' * 60}")
            print(f"\n📊 Resumen:")
            print(f"   ✅ Llave del cliente agregada a authorized_keys")
            print(f"   ✅ Cliente puede conectarse desde: {ip_cliente}")
            print(f"   ✅ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"\n💡 El cliente ahora puede conectarse con:")
            print(f"   ssh {usuario}@{ip_local}")
        else:
            print(f"\n{'═' * 60}")
            print(f"❌ INTERCAMBIO FALLIDO")
            print(f"{'═' * 60}")

        return exito

    except socket.timeout:
        print(f"\n⏱️  Timeout: No se recibió conexión en 5 minutos")
        servidor.close()
        return False
    except KeyboardInterrupt:
        print(f"\n\n⚠️  Interrumpido por el usuario")
        servidor.close()
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        try:
            servidor.close()
        except:
            pass
        return False


# Modo Cliente - Intercambio de Llaves
# Continuación para src/key_exchange.py

# ============================================================================
# MODO CLIENTE - Intercambio de Llaves
# ============================================================================


def intercambiar_llaves_cliente(conexion, ip_servidor):
    """
    Realiza el intercambio de llaves desde el lado del cliente.

    Args:
        conexion: Socket de conexión con el servidor
        ip_servidor (str): IP del servidor

    Returns:
        bool: True si el intercambio fue exitoso
    """
    try:
        from src.network_utils import obtener_nombre_host, obtener_usuario_actual

        print(f"\n{'═' * 60}")
        print("INICIANDO INTERCAMBIO DE LLAVES")
        print(f"{'═' * 60}")

        hostname = obtener_nombre_host()
        usuario_local = obtener_usuario_actual()
        sistema = platform.system().lower()

        # ========== FASE 1: HANDSHAKE ==========
        print(f"\n🔄 FASE 1: Intercambio de información")
        print(f"   📡 Enviando información del cliente...")

        info_cliente = {
            "hostname": hostname,
            "usuario": usuario_local,
            "sistema": sistema,
        }

        mensaje_handshake = crear_mensaje("HANDSHAKE", info_cliente)
        conexion.send(mensaje_handshake)
        print(f"   ✅ Información enviada")

        # Recibir handshake del servidor
        print(f"   📥 Recibiendo información del servidor...")
        mensaje_servidor = recibir_mensaje(conexion)

        if not mensaje_servidor or mensaje_servidor.get("tipo") != "HANDSHAKE":
            print(f"   ❌ Error: Handshake inválido")
            return False

        info_servidor = mensaje_servidor.get("datos", {})
        print(f"   ✅ Información recibida:")
        print(f"      • Hostname: {info_servidor.get('hostname', 'unknown')}")
        print(f"      • Usuario: {info_servidor.get('usuario', 'unknown')}")
        print(f"      • Sistema: {info_servidor.get('sistema', 'unknown').upper()}")

        # ========== FASE 2: INTERCAMBIO DE LLAVES PÚBLICAS ==========
        print(f"\n🔄 FASE 2: Intercambio de llaves públicas")

        # Recibir llave pública del servidor primero
        print(f"   📥 Recibiendo llave pública del servidor...")
        mensaje_llave_servidor = recibir_mensaje(conexion)

        if (
            not mensaje_llave_servidor
            or mensaje_llave_servidor.get("tipo") != "PUBLIC_KEY"
        ):
            print(f"   ❌ Error: Mensaje de llave inválido")
            return False

        llave_publica_servidor = mensaje_llave_servidor.get("datos", {}).get(
            "llave_publica", ""
        )

        if not llave_publica_servidor:
            print(f"   ❌ Error: Llave pública vacía")
            return False

        print(f"   ✅ Llave recibida ({len(llave_publica_servidor)} bytes)")

        # Validar llave del servidor
        print(f"\n   🔍 Validando llave del servidor...")
        es_valida, tipo_llave, bits = validar_llave_publica(llave_publica_servidor)

        if not es_valida:
            print(f"   ❌ Llave inválida")
            return False

        print(f"   ✅ Llave válida:")
        print(f"      • Tipo: {tipo_llave}")
        if bits:
            print(f"      • Tamaño aprox: {bits} bits")

        # Mostrar fingerprint
        fingerprint = calcular_fingerprint(llave_publica_servidor)
        print(f"\n   🔎 Fingerprint de la llave del servidor:")
        print(f"      {fingerprint}")

        # Leer nuestra llave pública desde ./keys/
        print("   📖 Leyendo llave pública del cliente...")
        llave_pub_path = KEYS_DIR / "id_rsa.pub"

        if not llave_pub_path.exists():
            print("   ❌ Error: No se encontró la llave pública")
            print(f"      Buscada en: {llave_pub_path}")
            print(f"      💡 Genera las llaves primero con Opción 3")
            return False

        with open(llave_pub_path, "r") as f:
            llave_publica_cliente = f.read().strip()

        print(f"   ✅ Llave pública leída ({len(llave_publica_cliente)} bytes)")

        # Enviar nuestra llave pública
        print(f"   📤 Enviando llave pública del cliente...")
        mensaje_llave = crear_mensaje(
            "PUBLIC_KEY",
            {
                "llave_publica": llave_publica_cliente,
                "hostname": hostname,
                "usuario": usuario_local,
            },
        )
        conexion.send(mensaje_llave)
        print(f"   ✅ Llave enviada")

        # ========== FASE 3: CONFIRMACIÓN DEL USUARIO ==========
        print(f"\n{'═' * 60}")
        print(f"CONFIRMACIÓN REQUERIDA")
        print(f"{'═' * 60}")
        print(f"\nEstá a punto de agregar la llave del servidor a known_hosts.")
        print(f"Esto permitirá conectarse al servidor sin verificación manual.")
        print(f"\nDetalles del servidor:")
        print(f"  • IP: {ip_servidor}")
        print(f"  • Usuario: {info_servidor.get('usuario', 'unknown')}")
        print(f"  • Hostname: {info_servidor.get('hostname', 'unknown')}")
        print(f"  • Sistema: {info_servidor.get('sistema', 'unknown').upper()}")
        print(f"  • Fingerprint: {fingerprint}")

        respuesta = input(f"\n¿Desea agregar esta llave a known_hosts? (s/n): ").lower()

        if respuesta != "s":
            print(f"\n❌ Intercambio cancelado por el usuario")
            mensaje_error = crear_mensaje("ERROR", {"razon": "Cancelado por usuario"})
            conexion.send(mensaje_error)
            return False

        # ========== FASE 4: CONFIGURACIÓN DE LLAVES ==========
        print(f"\n🔄 FASE 3: Configuración de llaves")

        # Agregar llave del servidor a known_hosts
        exito, mensaje = agregar_a_known_hosts(
            ip_servidor, llave_publica_servidor, info_servidor
        )

        if not exito:
            print(f"   ❌ {mensaje}")
            mensaje_error = crear_mensaje("ERROR", {"razon": mensaje})
            conexion.send(mensaje_error)
            return False

        print(f"   ✅ {mensaje}")

        # ========== FASE 5: CONFIRMACIÓN FINAL ==========
        print(f"\n🔄 FASE 4: Confirmación")
        print(f"   📥 Esperando confirmación del servidor...")

        mensaje_ack_servidor = recibir_mensaje(conexion, timeout=30)

        if not mensaje_ack_servidor or mensaje_ack_servidor.get("tipo") != "ACK":
            print(f"   ❌ No se recibió confirmación del servidor")
            return False

        print(f"   ✅ Servidor confirmó configuración exitosa")

        # Enviar nuestra confirmación
        print(f"   📡 Enviando confirmación al servidor...")
        mensaje_ack = crear_mensaje(
            "ACK",
            {
                "estado": "exito",
                "mensaje": "Llave configurada correctamente en el cliente",
            },
        )
        conexion.send(mensaje_ack)
        print(f"   ✅ Confirmación enviada")

        return True

    except Exception as e:
        print(f"\n❌ Error durante el intercambio: {e}")
        import traceback

        traceback.print_exc()
        return False


def modo_cliente_intercambio(ip_servidor=None, puerto=PUERTO_DEFAULT):
    """
    Inicia el modo cliente para conectarse a un servidor y realizar intercambio.

    Args:
        ip_servidor (str): IP del servidor (se solicita si es None)
        puerto (int): Puerto del servidor

    Returns:
        bool: True si el intercambio fue exitoso
    """
    from src.network_utils import obtener_usuario_actual
    from src.sftp_manager import SFTPManager

    print(f"\n{'═' * 60}")
    print("MODO CLIENTE - INTERCAMBIO AUTOMÁTICO DE LLAVES RSA")
    print(f"{'═' * 60}")

    # Verificar/generar llaves
    print(f"\n🔍 Verificando llaves RSA locales...")
    sftp_mgr = SFTPManager()

    if not sftp_mgr.verificar_llaves():
        print(f"⚠️  Generando nuevas llaves...")
        sftp_mgr.generar_llaves()

    print(f"✅ Llaves RSA disponibles")

    # Solicitar IP del servidor si no se proporcionó
    if not ip_servidor:
        print(f"\n📍 Configuración de conexión")
        ip_servidor = input("Ingrese la IP del servidor: ").strip()

        if not ip_servidor:
            print(f"❌ IP del servidor requerida")
            return False

    print(f"\n🔌 Conectando a {ip_servidor}:{puerto}...")

    try:
        # Conectar al servidor
        cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cliente.settimeout(TIMEOUT_CONEXION)
        cliente.connect((ip_servidor, puerto))

        print(f"✅ Conectado al servidor {ip_servidor}")

        # Realizar intercambio
        exito = intercambiar_llaves_cliente(cliente, ip_servidor)

        cliente.close()

        if exito:
            usuario_servidor = input(
                f"\n💡 Ingrese el usuario del servidor (para SSH): "
            ).strip()
            if not usuario_servidor:
                usuario_servidor = "usuario"

            print(f"\n{'═' * 60}")
            print(f"🎉 ¡INTERCAMBIO COMPLETADO EXITOSAMENTE!")
            print(f"{'═' * 60}")
            print(f"\n📊 Resumen:")
            print(f"   ✅ Llave del servidor agregada a known_hosts")
            print(f"   ✅ Su llave fue enviada al servidor")
            print(f"   ✅ Servidor: {ip_servidor}")
            print(f"   ✅ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"\n💡 Ahora puede conectarse con:")
            print(f"   ssh {usuario_servidor}@{ip_servidor}")
            print(f"\n💡 O usar en el script:")
            print(
                f"   python main.py --esicorp --sftp-host {ip_servidor} --sftp-user {usuario_servidor}"
            )
        else:
            print(f"\n{'═' * 60}")
            print(f"❌ INTERCAMBIO FALLIDO")
            print(f"{'═' * 60}")

        return exito

    except socket.timeout:
        print(f"\n⏱️  Timeout: No se pudo conectar al servidor")
        print(f"   Verifique que el servidor esté escuchando en {ip_servidor}:{puerto}")
        return False
    except ConnectionRefusedError:
        print(f"\n❌ Error: Conexión rechazada")
        print(f"   Verifique que:")
        print(f"   1. El servidor esté escuchando en el puerto {puerto}")
        print(f"   2. El firewall permita conexiones en ese puerto")
        print(f"   3. La IP {ip_servidor} sea correcta")
        return False
    except KeyboardInterrupt:
        print(f"\n\n⚠️  Interrumpido por el usuario")
        try:
            cliente.close()
        except:
            pass
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
        try:
            cliente.close()
        except:
            pass
        return False
