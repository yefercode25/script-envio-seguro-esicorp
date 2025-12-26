import sys
import traceback
from src import config
from src.sftp_manager import SFTPManager
from src.esicorp_processor import ESICORPProcessor
from src.network_utils import mostrar_info_servidor
from src.cli_parser import crear_parser
from src.utils import print_banner, print_error, print_info


class ESICORPApp:
    """Aplicación ESICORP - Transferencia segura vía SFTP/SSH."""

    def __init__(self):
        self.sftp_mgr = SFTPManager(keys_dir=config.KEYS_DIR)
        self.processor = ESICORPProcessor(
            salida_dir=config.SALIDA_DIR, procesados_dir=config.PROCESADOS_DIR
        )

    # ==========================================
    # FLUJO ESICORP SFTP - ENVÍO DE ARCHIVOS
    # ==========================================
    def enviar_archivos(self):
        """Flujo principal: Procesar y enviar archivos vía SFTP."""
        print_banner()
        print("=== ENVÍO DE ARCHIVOS VÍA SFTP ===\n")

        # PASO 1: Verificar/Generar llaves RSA
        print("=" * 60)
        print("PASO 1: VERIFICACIÓN DE LLAVES RSA")
        print("=" * 60)

        if not self.sftp_mgr.verificar_llaves():
            print("[!]  No se encontraron llaves RSA.")
            generar = input(
                "¿Desea generar nuevas llaves de 4096 bits? (s/n): "
            ).lower()
            if generar == "s":
                priv, pub = self.sftp_mgr.generar_llaves()
                if not priv:
                    print_error("No se pudieron generar las llaves. Abortando.")
                    input("\nPresione Enter para continuar...")
                    return

                # Solicitar configuración del servidor
                hostname = input("\n>> IP del servidor SFTP: ").strip()
                username = input(">> Usuario SFTP: ").strip()

                self.sftp_mgr.mostrar_instrucciones_configuracion(hostname, username)
                input("\n➡️  Presione ENTER cuando haya configurado el servidor... ")
            else:
                print_error("Llaves requeridas para continuar. Abortando.")
                input("\nPresione Enter para continuar...")
                return
        else:
            print("[OK] Llaves RSA encontradas\n")

        # PASO 2: Seleccionar archivos a procesar
        print("\n" + "=" * 60)
        print("PASO 2: SELECCIÓN DE ARCHIVOS")
        print("=" * 60)
        print("\n1. 📂 Usar archivos de ./salida (patrón ESICORP)")
        print("2. [EDIT] Seleccionar archivo/carpeta manualmente")

        opcion = input("\nOpción [1-2]: ").strip()

        if opcion == "2":
            # Selección manual
            from src.file_selector import solicitar_archivo_o_carpeta

            ruta, es_carpeta = solicitar_archivo_o_carpeta()

            if not ruta:
                print_info("Selección cancelada.")
                input("\nPresione Enter para continuar...")
                return

            # Procesar desde ruta personalizada
            archivos_procesados = self.processor.procesar_desde_ruta(ruta, es_carpeta)
        else:
            # Procesar desde ./salida
            archivos_procesados = self.processor.procesar_todos()

        if not archivos_procesados:
            print_info("No hay archivos para enviar.")
            input("\nPresione Enter para continuar...")
            return

        # PASO 3: Configuración y envío SFTP
        print("\n" + "=" * 60)
        print("PASO 3: CONFIGURACION Y ENVIO SFTP")
        print("=" * 60)
        print()
        print("[INFO] Configuracion del servidor de destino")
        print("[TIP] Ingrese los datos del servidor SFTP remoto")
        print("[TIP] Presione Enter para usar valores por defecto")
        print()

        hostname = (
            input(
                f"[?] IP del servidor SFTP [{config.SFTP_CONFIG['hostname']}]: "
            ).strip()
            or config.SFTP_CONFIG["hostname"]
        )
        username = (
            input(f"[?] Usuario SFTP [{config.SFTP_CONFIG['username']}]: ").strip()
            or config.SFTP_CONFIG["username"]
        )
        port = input(
            f"[?] Puerto SFTP [{config.SFTP_CONFIG['port']}]: "
        ).strip() or str(config.SFTP_CONFIG["port"])
        port = int(port) if port.isdigit() else 22
        remote_path = (
            input(f"[?] Ruta remota [{config.SFTP_CONFIG['remote_path']}]: ").strip()
            or config.SFTP_CONFIG["remote_path"]
        )

        print()
        print("[INFO] Configuracion establecida:")
        print(f"       Servidor: {username}@{hostname}:{port}")
        print(f"       Destino: {remote_path}")
        print()

        # Conectar SFTP
        sftp_client, ssh_client = self.sftp_mgr.conectar_sftp(
            hostname=hostname, username=username, port=port
        )

        if not sftp_client:
            print_error("No se pudo establecer conexión SFTP.")
            print_info(f"Archivos procesados en: {config.PROCESADOS_DIR}")
            input("\nPresione Enter para continuar...")
            return

        # Asegurar que remote_path termine con /
        if not remote_path.endswith("/"):
            remote_path = remote_path + "/"

        try:
            # Enviar archivos
            exitosos = 0
            for zip_file in archivos_procesados:
                remote_file = remote_path + zip_file.name
                if self.sftp_mgr.subir_archivo(sftp_client, zip_file, remote_file):
                    exitosos += 1

            print("\n" + "=" * 60)
            print(
                f"[OK] Resultado: {exitosos}/{len(archivos_procesados)} archivos enviados"
            )
            print("=" * 60)

            if exitosos == len(archivos_procesados):
                print("\n[***] ¡PROCESO COMPLETADO EXITOSAMENTE!")

        finally:
            self.sftp_mgr.cerrar_conexion(sftp_client, ssh_client)

        input("\nPresione Enter para continuar...")

    # ==========================================
    # MOSTRAR INFORMACIÓN DEL SERVIDOR
    # ==========================================
    def mostrar_info(self):
        """Muestra información del servidor para conexiones entrantes."""
        from src.display_utils import mostrar_info_completa

        # Mostrar toda la información
        mostrar_info_completa()

        input("\nPresione Enter para continuar...")

    # ==========================================
    # GESTIÓN DE LLAVES
    # ==========================================
    def gestionar_llaves(self):
        """Gestiona las llaves RSA (ver, generar, eliminar)."""
        while True:
            print_banner()
            print("=== GESTIÓN DE LLAVES RSA ===\n")

            if self.sftp_mgr.verificar_llaves():
                print("[OK] Llaves RSA existentes:")
                print(f"   Privada: {self.sftp_mgr.private_key_path}")
                print(f"   Pública: {self.sftp_mgr.public_key_path}\n")
                print("1. 👁️  Ver llave pública")
                print("2. [PROC] Regenerar llaves")
                print("3. [<] Volver")
                opcion = input("\nOpción [1-3]: ").strip()

                if opcion == "1":
                    try:
                        with open(self.sftp_mgr.public_key_path, "r") as f:
                            print("\n" + "=" * 60)
                            print("LLAVE PÚBLICA RSA:")
                            print("=" * 60)
                            print(f.read())
                            print("=" * 60)
                    except Exception as e:
                        print_error(f"Error al leer llave: {e}")
                    input("\nPresione Enter para continuar...")
                elif opcion == "2":
                    confirmar = input(
                        "¿Regenerar llaves? Esto invalidará la llave actual (s/n): "
                    ).lower()
                    if confirmar == "s":
                        self.sftp_mgr.generar_llaves(force=True)
                        input("\nPresione Enter para continuar...")
                elif opcion == "3":
                    break
            else:
                print("[!]  No hay llaves RSA generadas.\n")
                print("1. [KEY] Generar llaves nuevas")
                print("2. [<] Volver")
                opcion = input("\nOpción [1-2]: ").strip()

                if opcion == "1":
                    self.sftp_mgr.generar_llaves()
                    input("\nPresione Enter para continuar...")
                elif opcion == "2":
                    break

    # ==========================================
    # MENÚ PRINCIPAL
    # ==========================================
    def run(self):
        """Ejecuta el menú principal de la aplicación."""
        while True:
            print_banner()
            print("1. [TOOL] VERIFICAR/CONFIGURAR SSH")
            print("   Verificar estado del servicio SSH y configurar si es necesario")
            print()
            print("2. [SEC] INTERCAMBIO AUTOMATICO DE LLAVES")
            print("   Intercambiar llaves RSA entre cliente y servidor via sockets")
            print()
            print("3. [KEY] GESTION DE LLAVES RSA")
            print("   Ver, generar o regenerar llaves RSA de 4096 bits")
            print()
            print("4. [INFO] INFORMACION DEL SERVIDOR")
            print("   Ver IP, hostname, usuario y estado del servicio SSH")
            print()
            print("5. [UP] ENVIAR ARCHIVOS (SFTP)")
            print("   Procesar y enviar archivos via SFTP con cifrado AES-256")
            print()
            print("6. [TOOL] LIMPIAR CONFIGURACIONES Y ARCHIVOS")
            print("   Eliminar llaves, archivos procesados y limpiar servidor remoto")
            print()
            print("7. [EXIT] SALIR")
            print()

            option = input("Seleccione opcion [1-7]: ").strip()

            if option == "1":
                self.verificar_ssh()
            elif option == "2":
                self.intercambio_llaves()
            elif option == "3":
                self.gestionar_llaves()
            elif option == "4":
                self.mostrar_info()
            elif option == "5":
                self.enviar_archivos()
            elif option == "6":
                self.limpiar_sistema()
            elif option == "7":
                print("\n[BYE] Hasta luego!")
                break

    # ==========================================
    # LIMPIEZA DE CONFIGURACIONES Y ARCHIVOS
    # ==========================================
    def limpiar_sistema(self):
        """Limpia configuraciones, llaves y archivos procesados."""
        from src import cleanup_utils

        print_banner()
        print("LIMPIEZA DE CONFIGURACIONES Y ARCHIVOS")
        print("=" * 60)
        print()
        print("Opciones de limpieza disponibles:")
        print()
        print("1. [X] LIMPIAR TODO (LOCAL)")
        print("   Elimina llaves RSA y archivos procesados localmente")
        print()
        print("2. [X] LIMPIAR SERVIDOR REMOTO")
        print("   Elimina archivos del directorio remoto /home/grupo1/upload/")
        print()
        print("3. [X] LIMPIAR TODO (LOCAL + REMOTO)")
        print("   Ejecuta ambas limpiezas")
        print()
        print("4. [<] VOLVER")
        print()

        opcion = input("Seleccione opcion [1-4]: ").strip()

        if opcion == "1":
            cleanup_utils.limpiar_todo_local()
            input("\nPresione Enter para continuar...")
        elif opcion == "2":
            print()
            print("[INFO] Configuracion del servidor remoto")
            hostname = (
                input(
                    f"[?] IP del servidor [{config.SFTP_CONFIG['hostname']}]: "
                ).strip()
                or config.SFTP_CONFIG["hostname"]
            )
            username = (
                input(f"[?] Usuario [{config.SFTP_CONFIG['username']}]: ").strip()
                or config.SFTP_CONFIG["username"]
            )
            port = input(f"[?] Puerto [22]: ").strip() or "22"
            port = int(port) if port.isdigit() else 22
            remote_path = (
                input(
                    f"[?] Ruta a limpiar [{config.SFTP_CONFIG['remote_path']}]: "
                ).strip()
                or config.SFTP_CONFIG["remote_path"]
            )
            print()
            print("[PROC] Conectando al servidor...")
            sftp_client, ssh_client = self.sftp_mgr.conectar_sftp(
                hostname=hostname, username=username, port=port
            )
            if sftp_client:
                cleanup_utils.limpiar_directorio_remoto(sftp_client, remote_path)
                self.sftp_mgr.cerrar_conexion(sftp_client, ssh_client)
            else:
                print("[X] No se pudo conectar al servidor")
            input("\nPresione Enter para continuar...")
        elif opcion == "3":
            # Limpiar todo - ORDEN CORRECTO: Remoto primero, luego local
            print()
            confirmacion = (
                input("[!] Limpiar TODO (remoto + local)? (s/N): ").strip().lower()
            )

            if confirmacion == "s":
                # PRIMERO: Limpiar remoto (mientras las llaves aún existen)
                print()
                print("[INFO] Paso 1: Limpieza remota")
                hostname = (
                    input(
                        f"[?] IP del servidor [{config.SFTP_CONFIG['hostname']}]: "
                    ).strip()
                    or config.SFTP_CONFIG["hostname"]
                )
                username = (
                    input(f"[?] Usuario [{config.SFTP_CONFIG['username']}]: ").strip()
                    or config.SFTP_CONFIG["username"]
                )
                port = int(input(f"[?] Puerto [22]: ").strip() or "22")
                remote_path = (
                    input(
                        f"[?] Ruta a limpiar [{config.SFTP_CONFIG['remote_path']}]: "
                    ).strip()
                    or config.SFTP_CONFIG["remote_path"]
                )

                print()
                sftp_client, ssh_client = self.sftp_mgr.conectar_sftp(
                    hostname=hostname, username=username, port=port
                )

                if sftp_client:
                    cleanup_utils.limpiar_directorio_remoto(sftp_client, remote_path)
                    self.sftp_mgr.cerrar_conexion(sftp_client, ssh_client)
                    print()
                else:
                    print("[X] No se pudo conectar al servidor")
                    print("[!] Continuando con limpieza local...")
                    print()

                # SEGUNDO: Limpiar local (ahora que ya no necesitamos las llaves)
                print("[INFO] Paso 2: Limpieza local")
                cleanup_utils.limpiar_todo_local()
            else:
                print("[i] Operacion cancelada")

            input("\nPresione Enter para continuar...")

        # ==========================================

    # VERIFICACIÓN DE SSH
    # ==========================================
    def verificar_ssh(self):
        """Verifica y configura el servicio SSH."""
        from src.ssh_service import verificar_y_configurar_ssh

        # NO borrar pantalla
        verificar_y_configurar_ssh()
        input("\nPresione Enter para continuar...")

    # ==========================================
    # INTERCAMBIO AUTOMÁTICO DE LLAVES
    # ==========================================
    def intercambio_llaves(self):
        """Menú de intercambio automático de llaves RSA."""
        from src.key_exchange import modo_servidor_intercambio, modo_cliente_intercambio

        while True:
            print_banner()
            print("[SEC] INTERCAMBIO AUTOMÁTICO DE LLAVES RSA")
            print("=" * 60)
            print("\n1. [SRV]  MODO SERVIDOR (Escuchar conexiones)")
            print("2. [CLI] MODO CLIENTE (Conectar a servidor)")
            print("3. [<] VOLVER")
            print("\n")

            opcion = input("Seleccione opción [1-3]: ").strip()

            if opcion == "1":
                # Modo servidor
                print_banner()
                modo_servidor_intercambio()
                input("\nPresione Enter para continuar...")

            elif opcion == "2":
                # Modo cliente
                print_banner()
                modo_cliente_intercambio()
                input("\nPresione Enter para continuar...")

            elif opcion == "3":
                break
            else:
                print("\n[!]  Opción inválida")
                input("\nPresione Enter para continuar...")


# ==========================================
# PUNTO DE ENTRADA PRINCIPAL
# ==========================================
if __name__ == "__main__":
    try:
        parser = crear_parser()
        args = parser.parse_args()

        app = ESICORPApp()

        # Modo Interactivo
        if args.interactivo:
            app.run()

        # Modo ESICORP SFTP (CLI)
        elif args.esicorp:
            print_banner()
            print("=== MODO ESICORP SFTP (AUTOMÁTICO) ===\n")

            # Verificar/generar llaves
            if not app.sftp_mgr.verificar_llaves():
                print("[!]  Generando llaves RSA...")
                priv, pub = app.sftp_mgr.generar_llaves()
                if not priv:
                    print_error("No se pudieron generar las llaves.")
                    sys.exit(1)

            # Procesar archivos
            archivos_procesados = app.processor.procesar_todos()
            if not archivos_procesados:
                print_info("No hay archivos para procesar.")
                sys.exit(0)

            # Configuración SFTP
            hostname = args.sftp_host or config.SFTP_CONFIG["hostname"]
            username = args.sftp_user or config.SFTP_CONFIG["username"]
            port = args.sftp_port or config.SFTP_CONFIG["port"]
            remote_path = args.sftp_path or config.SFTP_CONFIG["remote_path"]

            # Conectar y enviar
            sftp_client, ssh_client = app.sftp_mgr.conectar_sftp(
                hostname=hostname, username=username, port=port
            )

            if not sftp_client:
                print_error("No se pudo establecer conexión SFTP.")
                sys.exit(1)

            try:
                exitosos = 0
                for zip_file in archivos_procesados:
                    remote_file = remote_path + zip_file.name
                    if app.sftp_mgr.subir_archivo(sftp_client, zip_file, remote_file):
                        exitosos += 1

                if exitosos == len(archivos_procesados):
                    print("\n[***] ¡PROCESO COMPLETADO EXITOSAMENTE!")
                    sys.exit(0)
                else:
                    sys.exit(1)
            finally:
                app.sftp_mgr.cerrar_conexion(sftp_client, ssh_client)

        # Mostrar información del servidor
        elif hasattr(args, "info") and args.info:
            print_banner()
            mostrar_info_servidor()
            sys.exit(0)

    except KeyboardInterrupt:
        print("\n\n[!]  Interrumpido por el usuario")
        sys.exit(0)
    except Exception as e:
        print_error(f"Error fatal: {e}")
        traceback.print_exc()
        sys.exit(1)
