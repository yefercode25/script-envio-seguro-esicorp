import os
import base64
import traceback
from .utils import (
    print_banner,
    print_phase,
    print_action,
    print_success,
    print_error,
    print_info,
)


class Receiver:
    """Maneja el flujo de recepción de archivos."""
    
    def __init__(self, crypto_manager, file_manager, network_manager):
        self.crypto = crypto_manager
        self.file_manager = file_manager
        self.network = network_manager

    def receive_auto(self, puerto, codigo, auto_desencriptar=False):
        """Modo receptor automático."""
        print_banner()
        print("=== MODO RECEPTOR AUTOMÁTICO ===\n")
        print_info(f"Puerto: {puerto if puerto != 0 else 'Asignación automática'}")
        print_info(f"Código: {'*' * len(codigo)}")
        print_info(f"Desencriptado automático: {'Sí' if auto_desencriptar else 'No'}\n")
        
        print("Esperando conexión...\n")
        
        received_file, session_id, original_filename = self.network.start_server(
            puerto, codigo
        )
        
        if not received_file or not session_id:
            print_error("No se recibió ningún archivo")
            return False
        
        self.file_manager.setup_session(session_id)
        print_success(f"\n✅ ARCHIVO RECIBIDO: {original_filename}")
        print_info(f"Ubicación: {received_file}")
        
        if auto_desencriptar:
            print("\n" + "="*60)
            return self.decrypt_auto(received_file)
        
        return True

    def decrypt_auto(self, file_path):
        """Desencripta automáticamente un archivo recibido."""
        try:
            print_phase("DESENCRIPTADO AUTOMÁTICO")
            
            print_action("1. Leyendo paquete...")
            nonce, original_hash, ciphertext = self.file_manager.read_package(file_path)
            
            print_action("2. Descifrando (AES-GCM)...")
            decrypted_data = self.crypto.decrypt_data(nonce, ciphertext)
            zip_content = base64.b64decode(decrypted_data)
            
            print_action("3. Verificando integridad (SHA-256)...")
            current_hash = self.crypto.generate_hash(zip_content)
            
            if current_hash != original_hash:
                print_error("❌ ERROR DE INTEGRIDAD - Hash no coincide")
                return False
            
            print_success("✅ Integridad verificada")
            
            print_action("4. Descomprimiendo...")
            temp_zip = os.path.join(self.file_manager.receiver_dir, "temp_decrypted.zip")
            self.file_manager.write_binary(temp_zip, zip_content)
            final_path = self.file_manager.decompress_file(temp_zip)
            self.file_manager.cleanup(temp_zip)
            
            print_success(f"\n✅ DESENCRIPTADO COMPLETADO")
            print_info(f"Archivos extraídos en: {final_path}")
            return True
            
        except Exception as e:
            print_error(f"Error en desencriptado: {e}")
            traceback.print_exc()
            return False

    def decrypt_local_file(self, enc_file_path):
        """Desencripta un archivo .enc local sin necesidad de transmisión de red."""
        print_banner()
        print("=== DESENCRIPTADO DE ARCHIVO LOCAL ===\n")
        
        # Validar que el archivo existe
        if not os.path.exists(enc_file_path):
            print_error(f"El archivo no existe: {enc_file_path}")
            return False
        
        # Validar extensión
        if not enc_file_path.endswith('.enc'):
            print_error("El archivo debe tener extensión .enc")
            return False
        
        print_info(f"Archivo: {enc_file_path}\n")
        
        try:
            # Crear una sesión temporal para el desencriptado
            from datetime import datetime
            session_id = datetime.now().strftime("%Y%m%d_%H%M%S") + "_local"
            self.file_manager.setup_session(session_id)
            
            print_phase("PROCESO DE DESENCRIPTADO")
            
            print_action("1. Leyendo paquete cifrado...")
            nonce, original_hash, ciphertext = self.file_manager.read_package(enc_file_path)
            print_info(f"   - Nonce: {nonce.hex()[:20]}...")
            print_info(f"   - Hash original: {original_hash[:32]}...")
            print_info(f"   - Tamaño cifrado: {len(ciphertext)} bytes")
            
            print_action("2. Descifrando con AES-256-GCM...")
            decrypted_data = self.crypto.decrypt_data(nonce, ciphertext)
            print_success("   ✓ Descifrado exitoso")
            
            print_action("3. Decodificando Base64...")
            zip_content = base64.b64decode(decrypted_data)
            print_info(f"   - Tamaño descomprimido: {len(zip_content)} bytes")
            
            print_action("4. Verificando integridad (SHA-256)...")
            current_hash = self.crypto.generate_hash(zip_content)
            print_info(f"   - Hash calculado: {current_hash[:32]}...")
            print_info(f"   - Hash esperado:  {original_hash[:32]}...")
            
            if current_hash != original_hash:
                print_error("❌ ERROR DE INTEGRIDAD - Los hashes no coinciden")
                print_info("El archivo puede estar corrupto o haber sido modificado")
                return False
            
            print_success("   ✓ Integridad verificada correctamente")
            
            print_action("5. Descomprimiendo archivos...")
            temp_zip = os.path.join(self.file_manager.receiver_dir, "temp_local_decrypt.zip")
            self.file_manager.write_binary(temp_zip, zip_content)
            final_path = self.file_manager.decompress_file(temp_zip)
            self.file_manager.cleanup(temp_zip)
            
            print_success(f"\n✅ DESENCRIPTADO COMPLETADO EXITOSAMENTE")
            print_info(f"\nArchivos extraídos en:")
            print_info(f"  {final_path}")
            
            # Listar archivos extraídos
            if os.path.exists(final_path):
                print_info("\nContenido:")
                for root, dirs, files in os.walk(final_path):
                    for file in files:
                        rel_path = os.path.relpath(os.path.join(root, file), final_path)
                        print_info(f"  - {rel_path}")
            
            return True
            
        except Exception as e:
            print_error(f"Error durante el desencriptado: {e}")
            traceback.print_exc()
            return False

    def decrypt_interactive(self, file_path):
        """Desencripta interactivamente un archivo (usado por el menú)."""
        try:
            print("\n[DESENCRIPTANDO...]")
            print_phase("1. LECTURA DEL PAQUETE")
            print_action("Extrayendo componentes del archivo cifrado...")
            nonce, original_hash, ciphertext = self.file_manager.read_package(file_path)

            print_phase("2. DESCIFRADO (AES-GCM)")
            print_action("Verificando autenticidad y descifrando...")
            decrypted_data = self.crypto.decrypt_data(nonce, ciphertext)
            print_success("Descifrado exitoso. La clave es correcta y el Tag GCM es válido.")

            zip_content = base64.b64decode(decrypted_data)

            print_phase("3. VERIFICACIÓN DE INTEGRIDAD")
            print_action("Recalculando hash SHA-256...")
            current_hash = self.crypto.generate_hash(zip_content)
            print_info(f"Hash calculado: {current_hash}")
            print_info(f"Hash original : {original_hash}")

            if current_hash != original_hash:
                print_error("¡ERROR DE INTEGRIDAD! Hash no coincide.")
                print_info("Esto indica que el archivo fue modificado después de ser generado por el emisor.")
                return False

            print_success("Integridad verificada. El archivo es auténtico.")

            print_phase("4. DESCOMPRESIÓN")
            print_action("Restaurando archivos originales...")
            temp_zip = os.path.join(self.file_manager.receiver_dir, "temp_decrypted.zip")
            self.file_manager.write_binary(temp_zip, zip_content)
            final_path = self.file_manager.decompress_file(temp_zip)
            self.file_manager.cleanup(temp_zip)

            print_success(f"Archivos extraídos en: {final_path}")
            return True

        except Exception as e:
            print_error(f"Error: {e}")
            return False

    def validate_integrity(self, file_path):
        """Valida la integridad de un archivo recibido."""
        try:
            print("\n[VALIDANDO...]")
            print_phase("VALIDACIÓN DE INTEGRIDAD")
            print_action("Leyendo paquete...")
            nonce, original_hash, ciphertext = self.file_manager.read_package(file_path)

            print_action("Descifrando para obtener contenido original...")
            decrypted_data = self.crypto.decrypt_data(nonce, ciphertext)
            zip_content = base64.b64decode(decrypted_data)

            print_action("Recalculando Hash...")
            current_hash = self.crypto.generate_hash(zip_content)

            if current_hash == original_hash:
                print_success("✅ INTEGRIDAD OK.")
                print_info("El archivo no ha sufrido alteraciones.")
                return True
            else:
                print_error("❌ INTEGRIDAD FALLIDA.")
                print_info("El archivo está corrupto o ha sido manipulado.")
                return False
        except Exception as e:
            print_error(f"Error: {e}")
            return False
