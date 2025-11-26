import argparse
from . import config


def crear_parser():
    """Crea y configura el parser de argumentos de línea de comandos."""
    parser = argparse.ArgumentParser(
        description='Sistema de Transferencia Segura de Archivos - ESICORP',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
EJEMPLOS DE USO:

  Modo Interactivo (Menú):
    python main.py --interactivo
    python main.py -i

  Modo Emisor Automático:
    python main.py --emisor --archivo "C:\\Datos\\Compras-23-02-2023.santiago" --ip 192.168.1.10 --codigo 1234
    python main.py --emisor -a "Ventas-10-11-2023.lima" -d 10.0.0.5 -p 5001 -c 9876

  Modo Receptor Automático:
    python main.py --receptor --codigo 1234
    python main.py --receptor -c 5678 -p 5001

  Modo Receptor con Desencriptado Automático:
    python main.py --receptor --codigo 1234 --desencriptar

  Desencriptar Archivo Local:
    python main.py --desencriptar-archivo "transfers/20231126_140000/receiver/payload.enc"
    python main.py -da "ruta/al/archivo.enc"

NOTAS:
  - El código de seguridad debe coincidir entre emisor y receptor
  - Los archivos se cifran con AES-256-GCM antes de enviarse
  - Se incluye verificación de integridad mediante SHA-256
  - Para desencriptar archivos .enc existentes, usa --desencriptar-archivo
        '''
    )
    
    # Grupo de modos mutuamente excluyentes
    grupo_modo = parser.add_mutually_exclusive_group(required=True)
    grupo_modo.add_argument('--interactivo', '-i', action='store_true',
                           help='Iniciar en modo interactivo con menús')
    grupo_modo.add_argument('--emisor', '-e', action='store_true',
                           help='Modo emisor: enviar archivo')
    grupo_modo.add_argument('--receptor', '-r', action='store_true',
                           help='Modo receptor: recibir archivo')
    grupo_modo.add_argument('--desencriptar-archivo', '-da', type=str, metavar='ARCHIVO',
                           help='Desencriptar un archivo .enc existente')
    
    # Argumentos para modo emisor
    parser.add_argument('--archivo', '-a', type=str,
                       help='Ruta del archivo o carpeta a enviar (requerido en modo emisor)')
    parser.add_argument('--ip', '-d', type=str, dest='destino_ip',
                       help='IP del receptor (requerido en modo emisor)')
    parser.add_argument('--puerto', '-p', type=int, default=config.DEFAULT_PORT,
                       help=f'Puerto de conexión (por defecto: {config.DEFAULT_PORT})')
    
    # Argumentos comunes
    parser.add_argument('--codigo', '-c', type=str,
                       help='Código de seguridad compartido (requerido en modos emisor y receptor)')
    
    # Argumentos para modo receptor
    parser.add_argument('--desencriptar', action='store_true',
                       help='Desencriptar automáticamente el archivo recibido (solo modo receptor)')
    
    return parser
