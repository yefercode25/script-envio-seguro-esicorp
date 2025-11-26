import sys
import os
import random
import traceback
import tkinter as tk
from datetime import datetime
from tkinter import filedialog
from src import config
from src.crypto_manager import CryptoManager
from src.file_manager import FileManager
from src.network_manager import NetworkManager
from src.cli_parser import crear_parser
from src.sender import Sender
from src.receiver import Receiver
from src.utils import (
    print_banner,
    print_success,
    print_error,
    print_info,
)


class SecureTransferApp:
    def __init__(self):
        self.crypto = CryptoManager()
        self.file_manager = FileManager()
        self.network = NetworkManager()
        self.sender = Sender(self.crypto, self.file_manager, self.network)
        self.receiver = Receiver(self.crypto, self.file_manager, self.network)

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
    # FLUJO DE ENVÍO (SENDER) - MODO INTERACTIVO
    # ==========================================
    def sender_flow(self):
        print_banner()
        print("=== MODO EMISOR ===")

        # 1. Configurar Sesión (Timestamp)
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.file_manager.setup_session(session_id)
        print_info(f"ID de Sesión generado: {session_id}")

        # 2. Datos de Conexión y Autenticación con Reintentos
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
                    if auth_attempts == 0:
                        # Enviar archivo por primera vez
                        success = self.sender.send_interactive(
                            self.get_input_path, dest_ip, dest_port, 
                            security_code, session_id
                        )
                    else:
                        # Reintentar con paquete ya generado
                        pkg_path = self.file_manager.get_sender_path("payload.enc")
                        original_filename = "archivo"  # Se reemplazará en el siguiente envío
                        success = self.network.send_file(
                            dest_ip, dest_port, pkg_path, security_code, 
                            session_id, original_filename
                        )

                    if success:
                        print("\n✅ ENVÍO COMPLETADO.")
                        print_info("El archivo ha sido entregado al receptor.")
                        input("\nPresione Enter para volver...")
                        return

                except ConnectionError as e:
                    print_error(f"Error de conexión: {e}")
                    retry = input(
                        "¿Desea reintentar ingresando nueva IP/Puerto? (s/n): "
                    ).lower()
                    if retry == "s":
                        break
                    else:
                        return

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
    # FLUJO DE RECEPCIÓN (RECEIVER) - MODO INTERACTIVO
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
                self.receiver.decrypt_interactive(file_path)
                input("\nPresione Enter para continuar...")
            elif choice == "2":
                self.receiver.validate_integrity(file_path)
                input("\nPresione Enter para continuar...")
            elif choice == "3":
                break

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
        parser = crear_parser()
        args = parser.parse_args()
        
        app = SecureTransferApp()
        
        # Modo Interactivo
        if args.interactivo:
            app.run()
        
        # Modo Emisor Automático
        elif args.emisor:
            if not args.archivo:
                parser.error("El modo emisor requiere --archivo/-a")
            if not args.destino_ip:
                parser.error("El modo emisor requiere --ip/-d")
            if not args.codigo:
                parser.error("El modo emisor requiere --codigo/-c")
            
            # Validar puerto
            if args.puerto < 1024 or args.puerto > 65535:
                print_error("El puerto debe estar entre 1024 y 65535")
                sys.exit(1)
            
            exito = app.sender.send_auto(args.archivo, args.destino_ip, args.puerto, args.codigo)
            sys.exit(0 if exito else 1)
        
        # Modo Receptor Automático
        elif args.receptor:
            if not args.codigo:
                parser.error("El modo receptor requiere --codigo/-c")
            
            # Validar puerto si se especifica
            if args.puerto != config.DEFAULT_PORT and (args.puerto < 0 or args.puerto > 65535):
                print_error("El puerto debe estar entre 0 y 65535 (0 = asignación automática)")
                sys.exit(1)
            
            exito = app.receiver.receive_auto(args.puerto, args.codigo, args.desencriptar)
            sys.exit(0 if exito else 1)
        
        # Modo Desencriptar Archivo Local
        elif args.desencriptar_archivo:
            exito = app.receiver.decrypt_local_file(args.desencriptar_archivo)
            sys.exit(0 if exito else 1)
            
    except KeyboardInterrupt:
        print("\n\nInterrumpido por el usuario")
        sys.exit(0)
    except Exception as e:
        print_error(f"Error fatal: {e}")
        traceback.print_exc()
        sys.exit(1)
