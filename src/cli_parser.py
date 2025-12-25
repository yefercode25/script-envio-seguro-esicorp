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
    python main.py --esicorp --sftp-host 192.168.1.100 --sftp-user esicorp
    python main.py --esicorp --sftp-host 10.0.0.5 --sftp-user admin --sftp-port 2222

  Mostrar información del servidor:
    python main.py --info

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

    # Argumentos para modo ESICORP SFTP
    parser.add_argument(
        "--sftp-host", type=str, help="Hostname/IP del servidor SFTP (modo ESICORP)"
    )
    parser.add_argument("--sftp-user", type=str, help="Usuario SFTP (modo ESICORP)")
    parser.add_argument(
        "--sftp-port",
        type=int,
        default=22,
        help="Puerto SFTP (default: 22, modo ESICORP)",
    )
    parser.add_argument(
        "--sftp-path", type=str, help="Ruta remota en servidor SFTP (modo ESICORP)"
    )

    return parser
