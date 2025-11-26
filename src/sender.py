import os
import base64
import traceback
from datetime import datetime
from .utils import (
    print_banner,
    print_phase,
    print_action,
    print_success,
    print_error,
    print_info,
)


class Sender:
    """Maneja el flujo de envío de archivos."""
    
    def __init__(self, crypto_manager, file_manager, network_manager):
        self.crypto = crypto_manager
        self.file_manager = file_manager
        self.network = network_manager

    def send_auto(self, archivo, destino_ip, puerto, codigo):
        """Modo emisor automático sin interacción del usuario."""
        print_banner()
        print("=== MODO EMISOR AUTOMÁTICO ===\n")
        
        # Validar que el archivo existe
        if not os.path.exists(archivo):
            print_error(f"El archivo no existe: {archivo}")
            return False
        
        # Configurar sesión
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.file_manager.setup_session(session_id)
        print_info(f"ID de Sesión: {session_id}")
        print_info(f"Archivo: {archivo}")
        print_info(f"Destino: {destino_ip}:{puerto}")
        print_info(f"Código: {'*' * len(codigo)}\n")
        
        try:
            # Procesamiento
            print_phase("1. PREPARACIÓN Y COMPRESIÓN")
            zip_path = self.file_manager.compress_path(archivo)
            
            print_phase("2. INTEGRIDAD (HASHING)")
            zip_content = self.file_manager.read_binary(zip_path)
            file_hash = self.crypto.generate_hash(zip_content)
            print_info(f"Hash SHA-256: {file_hash}")
            
            print_phase("3. CONFIDENCIALIDAD (CIFRADO)")
            encoded_content = base64.b64encode(zip_content)
            nonce, ciphertext = self.crypto.encrypt_data(encoded_content)
            
            print_phase("4. EMPAQUETADO")
            pkg_path = self.file_manager.save_package(archivo, nonce, file_hash, ciphertext)
            self.file_manager.cleanup(zip_path)
            
            print_phase("5. TRANSMISIÓN POR RED")
            original_filename = os.path.basename(archivo)
            success = self.network.send_file(
                destino_ip, puerto, pkg_path, codigo, session_id, original_filename
            )
            
            if success:
                print_success("\n✅ ENVÍO COMPLETADO EXITOSAMENTE")
                return True
            else:
                print_error("\n❌ ERROR EN EL ENVÍO")
                return False
                
        except ConnectionError as e:
            print_error(f"Error de conexión: {e}")
            return False
        except PermissionError:
            print_error("Código de seguridad incorrecto")
            return False
        except Exception as e:
            print_error(f"Error crítico: {e}")
            traceback.print_exc()
            return False

    def send_interactive(self, get_input_path_func, dest_ip, dest_port, security_code, session_id):
        """Modo emisor interactivo (usado por el menú)."""
        path = get_input_path_func()
        if not path:
            return False

        try:
            print("\n[PROCESANDO ARCHIVO...]")
            print_phase("1. PREPARACIÓN Y COMPRESIÓN")
            print_action("Iniciando compresión y sanitización...")
            zip_path = self.file_manager.compress_path(path)

            print_phase("2. INTEGRIDAD (HASHING)")
            print_action("Calculando hash SHA-256 del archivo comprimido...")
            zip_content = self.file_manager.read_binary(zip_path)
            file_hash = self.crypto.generate_hash(zip_content)
            print_info(f"Hash SHA-256 original: {file_hash}")

            print_phase("3. CONFIDENCIALIDAD (CIFRADO)")
            print_action("Cifrando datos con AES-256-GCM...")
            encoded_content = base64.b64encode(zip_content)
            nonce, ciphertext = self.crypto.encrypt_data(encoded_content)

            print_phase("4. EMPAQUETADO")
            print_action("Generando estructura de transporte (.enc)...")
            pkg_path = self.file_manager.save_package(path, nonce, file_hash, ciphertext)
            self.file_manager.cleanup(zip_path)
            print_success(f"Paquete seguro listo en: {pkg_path}")

            print("\n[TRANSMITIENDO...]")
            print_phase("5. TRANSMISIÓN POR RED")
            print_action("Iniciando protocolo de transferencia segura...")
            original_filename = os.path.basename(path)

            success = self.network.send_file(
                dest_ip, dest_port, pkg_path, security_code, session_id, original_filename
            )

            return success

        except Exception as e:
            print_error(f"Error: {e}")
            traceback.print_exc()
            return False
