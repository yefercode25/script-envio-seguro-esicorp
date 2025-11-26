import sys
import os
import time
import base64
import tkinter as tk
import traceback
import random
from datetime import datetime
from tkinter import filedialog
from src import config
from src.crypto_manager import CryptoManager
from src.file_manager import FileManager
from src.network_manager import NetworkManager
from src.utils import (
    print_banner,
    print_phase,
    print_action,
    print_success,
    print_error,
    print_info,
    print_crypto,
    print_file,
    print_network,
)


class SecureTransferApp:
    def __init__(self):
        self.crypto = CryptoManager()
        self.file_manager = FileManager()
        self.network = NetworkManager()

    def select_path_dialog(self, select_folder=False):
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        if select_folder:
            path = filedialog.askdirectory(title="Seleccione la carpeta")
        else:
            path = filedialog.askopenfilename(title="Seleccione el archivo")
        root.destroy()
        return path

    def get_input_path(self):
        print("\n--- SELECCIÓN DE ORIGEN ---")
        print("1. 📄 Seleccionar Archivo (Diálogo)")
        print("2. 📁 Seleccionar Carpeta (Diálogo)")

        choice = input("\nOpción [1-2]: ").strip()
        path = ""
        if choice == "1":
            path = self.select_path_dialog(select_folder=False)
        elif choice == "2":
            path = self.select_path_dialog(select_folder=True)

        if not path:
            print_error("No se seleccionó ninguna ruta.")
            return None
        return path

    # ==========================================
    # FLUJO DE ENVÍO (SENDER)
    # ==========================================
    def sender_flow(self):
        print_banner()
        print("=== MODO EMISOR ===")

        # 1. Configurar Sesión (Timestamp)
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.file_manager.setup_session(session_id)
        print_info(f"ID de Sesión generado: {session_id}")

        # 2. Seleccionar Archivo
        path = self.get_input_path()
        if not path:
            return

        # 3. Datos de Conexión y Autenticación con Reintentos
        while True:  # Bucle de Conexión
            dest_ip = input(">> IP del Receptor: ").strip()

            # Validación de Puerto Emisor
            while True:
                port_input = input(f">> Puerto [{config.DEFAULT_PORT}]: ").strip()
                if not port_input:
                    dest_port = config.DEFAULT_PORT
                    break
                if port_input.isdigit() and 1024 <= int(port_input) <= 65535:
                    dest_port = port_input
                    break
                print_error("Puerto inválido.")

            auth_attempts = 0
            max_auth_attempts = 5

            while auth_attempts < max_auth_attempts:  # Bucle de Autenticación
                security_code = input(
                    f">> Código de Seguridad (Intento {auth_attempts + 1}/{max_auth_attempts}): "
                ).strip()

                try:
                    print("\n[PROCESANDO ARCHIVO...]")
                    if (
                        auth_attempts == 0
                    ):  # Solo procesar el archivo la primera vez para ahorrar tiempo
                        print_phase("1. PREPARACIÓN Y COMPRESIÓN")
                        print_action("Iniciando compresión y sanitización...")
                        # Compresión
                        zip_path = self.file_manager.compress_path(path)

                        print_phase("2. INTEGRIDAD (HASHING)")
                        print_action(
                            "Calculando hash SHA-256 del archivo comprimido..."
                        )
                        # Hashing
                        zip_content = self.file_manager.read_binary(zip_path)
                        file_hash = self.crypto.generate_hash(zip_content)
                        print_info(f"Hash SHA-256 original: {file_hash}")

                        print_phase("3. CONFIDENCIALIDAD (CIFRADO)")
                        print_action("Cifrando datos con AES-256-GCM...")
                        # Cifrado
                        encoded_content = base64.b64encode(zip_content)
                        nonce, ciphertext = self.crypto.encrypt_data(encoded_content)

                        print_phase("4. EMPAQUETADO")
                        print_action("Generando estructura de transporte (.enc)...")
                        # Empaquetado
                        pkg_path = self.file_manager.save_package(
                            path, nonce, file_hash, ciphertext
                        )
                        self.file_manager.cleanup(
                            zip_path
                        )  # Limpiar zip temporal del sender
                        print_success(f"Paquete seguro listo en: {pkg_path}")
                    else:
                        # Recuperar ruta del paquete ya generado
                        pkg_path = self.file_manager.get_sender_path("payload.enc")

                    # --- ENVÍO POR RED ---
                    print("\n[TRANSMITIENDO...]")
                    print_phase("5. TRANSMISIÓN POR RED")
                    print_action("Iniciando protocolo de transferencia segura...")
                    original_filename = os.path.basename(path)

                    # Intentar envío
                    success = self.network.send_file(
                        dest_ip,
                        dest_port,
                        pkg_path,
                        security_code,
                        session_id,
                        original_filename,
                    )

                    if success:
                        print("\n✅ ENVÍO COMPLETADO.")
                        print_info("El archivo ha sido entregado al receptor.")
                        input("\nPresione Enter para volver...")
                        return  # Salir de la función sender_flow exitosamente

                except ConnectionError as e:
                    print_error(f"Error de conexión: {e}")
                    retry = input(
                        "¿Desea reintentar ingresando nueva IP/Puerto? (s/n): "
                    ).lower()
                    if retry == "s":
                        break  # Romper bucle de autenticación para volver a pedir IP/Puerto
                    else:
                        return  # Salir si no quiere reintentar

                except PermissionError:
                    auth_attempts += 1
                    print_error(f"Código de seguridad incorrecto.")
                    if auth_attempts >= max_auth_attempts:
                        print_error(
                            "❌ Se ha excedido el número máximo de intentos de autenticación."
                        )
                        input("\nPresione Enter para volver...")
                        return

                except Exception as e:
                    print_error(f"Error crítico: {e}")
                    traceback.print_exc()
                    return

    # ==========================================
    # FLUJO DE RECEPCIÓN (RECEIVER)
    # ==========================================
    def receiver_flow(self):
        print_banner()
        print("=== MODO RECEPTOR ===")

        # Generar código aleatorio de 4 dígitos
        security_code = str(random.randint(1000, 9999))

        # Usar puerto 0 para asignación automática
        port = 0

        print("\nIniciando servidor seguro...")
        received_file, session_id, original_filename = self.network.start_server(
            port, security_code
        )

        if received_file and session_id:
            # Sincronizar sesión en el receptor
            self.file_manager.setup_session(session_id)
            print_info(f"Sesión sincronizada: {session_id}")
            self.receiver_menu(received_file, original_filename)
        else:
            # Si retorna None es porque el usuario canceló con Ctrl+C o hubo error crítico
            pass
            input("\nPresione Enter para volver...")

    def receiver_menu(self, file_path, original_filename):
        while True:
            print_banner()
            print(f"ARCHIVO RECIBIDO: {original_filename}")
            print(f"UBICACIÓN TEMPORAL: {file_path}")
            print("-" * 40)
            print("1. 🔓 Desencriptar y Descomprimir")
            print("2. 🔍 Validar Integridad (Hash)")
            print("3. 🔙 Volver al Menú Principal")

            choice = input("\nOpción: ").strip()

            if choice == "1":
                self.decrypt_process(file_path)
            elif choice == "2":
                self.validate_integrity(file_path)
            elif choice == "3":
                break

    def decrypt_process(self, file_path):
        try:
            print("\n[DESENCRIPTANDO...]")
            print_phase("1. LECTURA DEL PAQUETE")
            print_action("Extrayendo componentes del archivo cifrado...")
            nonce, original_hash, ciphertext = self.file_manager.read_package(file_path)

            print_phase("2. DESCIFRADO (AES-GCM)")
            print_action("Verificando autenticidad y descifrando...")
            decrypted_data = self.crypto.decrypt_data(nonce, ciphertext)
            print_success(
                "Descifrado exitoso. La clave es correcta y el Tag GCM es válido."
            )

            zip_content = base64.b64decode(decrypted_data)

            print_phase("3. VERIFICACIÓN DE INTEGRIDAD")
            print_action("Recalculando hash SHA-256...")
            current_hash = self.crypto.generate_hash(zip_content)
            print_info(f"Hash calculado: {current_hash}")
            print_info(f"Hash original : {original_hash}")

            if current_hash != original_hash:
                print_error("¡ERROR DE INTEGRIDAD! Hash no coincide.")
                print_info(
                    "Esto indica que el archivo fue modificado después de ser generado por el emisor."
                )
                return

            print_success("Integridad verificada. El archivo es auténtico.")

            print_phase("4. DESCOMPRESIÓN")
            print_action("Restaurando archivos originales...")
            # Guardar zip temporal en receiver dir
            temp_zip = os.path.join(
                self.file_manager.receiver_dir, "temp_decrypted.zip"
            )
            self.file_manager.write_binary(temp_zip, zip_content)

            final_path = self.file_manager.decompress_file(temp_zip)
            self.file_manager.cleanup(temp_zip)

            print_success(f"Archivos extraídos en: {final_path}")

        except Exception as e:
            print_error(f"Error: {e}")

        input("\nPresione Enter para continuar...")

    def validate_integrity(self, file_path):
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
            else:
                print_error("❌ INTEGRIDAD FALLIDA.")
                print_info("El archivo está corrupto o ha sido manipulado.")
        except Exception as e:
            print_error(f"Error: {e}")
        input("\nPresione Enter para continuar...")

    def run(self):
        while True:
            print_banner()
            print("1. 📤 MODO EMISOR")
            print("2. 📥 MODO RECEPTOR")
            print("3. 🗑️  BORRAR HISTORIAL DE TRANSFERENCIAS")
            print("4. 🚪 SALIR")
            print("\n")

            option = input("Seleccione opción [1-4]: ")

            if option == "1":
                self.sender_flow()
            elif option == "2":
                self.receiver_flow()
            elif option == "3":
                confirm = input(
                    "¿Está seguro de borrar todo el historial de transferencias? (s/n): "
                ).lower()
                if confirm == "s":
                    self.file_manager.clear_all_transfers()
                input("\nPresione Enter para continuar...")
            elif option == "4":
                break


if __name__ == "__main__":
    try:
        app = SecureTransferApp()
        app.run()
    except KeyboardInterrupt:
        sys.exit(0)
