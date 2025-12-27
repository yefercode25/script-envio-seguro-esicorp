import argparse
from . import config


def crear_parser():
    """Crea y configura el parser de argumentos de línea de comandos."""
    parser = argparse.ArgumentParser(
        description="Sistema de Transferencia Segura ESICORP - SFTP/SSH",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EJEMPLOS DE USO:

  Modo Interactivo (Menú):
    python main.py --interactivo
    python main.py -i

  Modo ESICORP SFTP (Envío automático):
    python main.py --esicorp --sftp-host 192.168.1.100 --sftp-user grupo1
    python main.py --esicorp --sftp-host 10.0.0.5 --sftp-user admin --sftp-port 2222

  Verificar/Configurar SSH:
    python main.py --check-ssh

  Intercambio de llaves RSA:
    python main.py --key-exchange --mode server --port 5000
    python main.py --key-exchange --mode client --target 192.168.1.100

  Gestión de llaves RSA:
    python main.py --manage-keys --action view
    python main.py --manage-keys --action generate

  Mostrar información del servidor:
    python main.py --info

  Limpiar configuraciones:
    python main.py --cleanup --local
    python main.py --cleanup --remote --sftp-host 192.168.1.100 --sftp-user grupo1
    python main.py --cleanup --all --sftp-host 192.168.1.100 --sftp-user grupo1

NOTAS:
  - Los archivos deben estar en ./salida con formato: Area-DD-MM-AAAA.Sede
  - Las llaves RSA se generan automáticamente en ./keys
  - Los archivos procesados se guardan en ./procesados
  - Se requiere configurar la llave pública en el servidor Linux
        """,
    )

    # Grupo de modos mutuamente excluyentes
    grupo_modo = parser.add_mutually_exclusive_group(required=True)

    grupo_modo.add_argument(
        "--interactivo",
        "-i",
        action="store_true",
        help="Iniciar en modo interactivo con menús",
    )

    grupo_modo.add_argument(
        "--esicorp",
        action="store_true",
        help="Modo ESICORP: procesar y enviar archivos vía SFTP",
    )

    grupo_modo.add_argument(
        "--info",
        action="store_true",
        help="Mostrar información del servidor para conexiones",
    )

    grupo_modo.add_argument(
        "--check-ssh",
        action="store_true",
        help="Verificar y configurar servicio SSH",
    )

    grupo_modo.add_argument(
        "--key-exchange",
        action="store_true",
        help="Intercambio automático de llaves RSA",
    )

    grupo_modo.add_argument(
        "--manage-keys",
        action="store_true",
        help="Gestión de llaves RSA (ver/generar)",
    )

    grupo_modo.add_argument(
        "--cleanup",
        action="store_true",
        help="Limpiar configuraciones y archivos",
    )

    # Argumentos para modo ESICORP SFTP
    parser.add_argument("--sftp-host", type=str, help="Hostname/IP del servidor SFTP")
    parser.add_argument("--sftp-user", type=str, help="Usuario SFTP")
    parser.add_argument(
        "--sftp-port",
        type=int,
        default=22,
        help="Puerto SFTP (default: 22)",
    )
    parser.add_argument("--sftp-path", type=str, help="Ruta remota en servidor SFTP")

    # Argumentos para intercambio de llaves
    parser.add_argument(
        "--mode",
        type=str,
        choices=["server", "client"],
        help="Modo para intercambio de llaves: server o client",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=5000,
        help="Puerto para intercambio de llaves (default: 5000)",
    )
    parser.add_argument(
        "--target",
        type=str,
        help="IP objetivo para modo cliente en intercambio de llaves",
    )

    # Argumentos para gestión de llaves
    parser.add_argument(
        "--action",
        type=str,
        choices=["view", "generate"],
        help="Acción para gestión de llaves: view o generate",
    )

    # Argumentos para limpieza
    parser.add_argument(
        "--local",
        action="store_true",
        help="Limpiar solo archivos locales (modo --cleanup)",
    )
    parser.add_argument(
        "--remote",
        action="store_true",
        help="Limpiar solo servidor remoto (modo --cleanup)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Limpiar todo: local + remoto (modo --cleanup)",
    )

    return parser
