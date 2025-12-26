"""
SFTP Manager - Gestión de conexiones SFTP y llaves RSA

Este módulo proporciona funcionalidad reutilizable para:
- Generación y gestión de llaves RSA de 4096 bits
- Autenticación SFTP mediante llave pública
- Transferencia segura de archivos

Autor: Grupo ESICORP - UNAD
"""

import os
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

try:
    import paramiko
except ImportError:
    paramiko = None


class SFTPManager:
    """Gestor de conexiones SFTP y llaves RSA."""

    def __init__(self, keys_dir="./keys"):
        """
        Inicializa el gestor SFTP.

        Args:
            keys_dir (str): Directorio para almacenar llaves RSA
        """
        self.keys_dir = Path(keys_dir)
        self.keys_dir.mkdir(exist_ok=True)
        self.private_key_path = self.keys_dir / "id_rsa"
        self.public_key_path = self.keys_dir / "id_rsa.pub"

    def verificar_llaves(self):
        """
        Verifica si existen las llaves RSA.

        Returns:
            bool: True si existen ambas llaves, False en caso contrario
        """
        return self.private_key_path.exists() and self.public_key_path.exists()

    def generar_llaves(self, force=False):
        """
        AUTENTICACIÓN: Genera un par de llaves RSA de 4096 bits.

        Args:
            force (bool): Si True, regenera las llaves aunque existan

        Returns:
            tuple: (ruta_privada, ruta_publica) o (None, None) si falla
        """
        if self.verificar_llaves() and not force:
            return self.private_key_path, self.public_key_path

        try:
            print("[KEY] Generando llaves RSA de 4096 bits...")
            print("   (Esto puede tomar unos segundos)")

            # AUTENTICACIÓN: Generar par de llaves RSA de 4096 bits
            private_key = rsa.generate_private_key(
                public_exponent=65537, key_size=4096, backend=default_backend()
            )

            # Serializar llave privada
            private_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption(),
            )

            # Guardar llave privada
            with open(self.private_key_path, "wb") as f:
                f.write(private_pem)
            os.chmod(self.private_key_path, 0o600)

            # Extraer y serializar llave pública
            public_key = private_key.public_key()
            public_pem = public_key.public_bytes(
                encoding=serialization.Encoding.OpenSSH,
                format=serialization.PublicFormat.OpenSSH,
            )

            # Guardar llave pública
            with open(self.public_key_path, "wb") as f:
                f.write(public_pem)

            print(f"[OK] Llaves generadas exitosamente:")
            print(f"   Privada: {self.private_key_path}")
            print(f"   Pública: {self.public_key_path}")

            return self.private_key_path, self.public_key_path

        except Exception as e:
            print(f"[X] Error al generar llaves: {e}")
            return None, None

    def mostrar_instrucciones_configuracion(self, hostname, username):
        """
        Muestra instrucciones para configurar la llave pública en el servidor.

        Args:
            hostname (str): Nombre o IP del servidor
            username (str): Usuario del servidor
        """
        print("\n" + "🔴" * 30)
        print("[!]  CONFIGURACIÓN REQUERIDA - SERVIDOR LINUX [!]")
        print("🔴" * 30)
        print("\nPara autenticarse en el servidor SFTP, copie la llave pública:")
        print(f"\n1. Archivo: {self.public_key_path.absolute()}")
        print("2. Contenido a copiar:")

        try:
            with open(self.public_key_path, "r") as f:
                print(f"   {f.read().strip()}")
        except:
            pass

        print("\n3. En el servidor Linux, ejecute:")
        print(f"   ssh {username}@{hostname}")
        print("   mkdir -p ~/.ssh")
        print("   echo '[LLAVE_PUBLICA_COPIADA]' >> ~/.ssh/authorized_keys")
        print("   chmod 700 ~/.ssh")
        print("   chmod 600 ~/.ssh/authorized_keys")
        print("\n" + "=" * 60)

    def conectar_sftp(self, hostname, username, port=22, timeout=10):
        """
        AUTENTICACIÓN: Establece conexión SFTP usando llave privada RSA.

        Args:
            hostname (str): IP o nombre del servidor
            username (str): Usuario SFTP
            port (int): Puerto SSH (default: 22)
            timeout (int): Tiempo de espera en segundos

        Returns:
            tuple: (sftp_client, ssh_client) o (None, None) si falla
        """
        if paramiko is None:
            print("[X] ERROR: paramiko no está instalado")
            print("   Ejecute: pip install paramiko")
            return None, None

        if not self.verificar_llaves():
            print("[X] ERROR: No se encontraron llaves RSA")
            print("   Genere las llaves primero con generar_llaves()")
            return None, None

        try:
            print(f"🔌 Conectando a {username}@{hostname}:{port}...")

            # Crear cliente SSH
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # AUTENTICACIÓN: Cargar llave privada
            private_key = paramiko.RSAKey.from_private_key_file(
                str(self.private_key_path)
            )

            # Conectar usando autenticación por llave pública
            ssh_client.connect(
                hostname=hostname,
                port=port,
                username=username,
                pkey=private_key,
                timeout=timeout,
                look_for_keys=False,
                allow_agent=False,
            )

            # Abrir sesión SFTP
            sftp_client = ssh_client.open_sftp()

            print("[OK] Conexión SFTP establecida exitosamente")
            return sftp_client, ssh_client

        except paramiko.AuthenticationException:
            print("\n[X] ERROR DE AUTENTICACIÓN")
            print("=" * 60)
            print("La llave pública no está configurada en el servidor.")
            self.mostrar_instrucciones_configuracion(hostname, username)
            return None, None

        except paramiko.SSHException as e:
            print(f"[X] ERROR SSH: {e}")
            return None, None

        except Exception as e:
            print(f"[X] ERROR de conexión: {e}")
            print(f"   Verifique que {hostname}:{port} sea accesible")
            return None, None

    def subir_archivo(self, sftp_client, local_path, remote_path, extraer=True):
        """
        Sube un archivo al servidor SFTP con output muy descriptivo.

        Args:
            sftp_client: Cliente SFTP conectado
            local_path (str/Path): Ruta local del archivo
            remote_path (str): Ruta remota de destino
            extraer (bool): Si True, extrae el ZIP en el servidor

        Returns:
            bool: True si la subida fue exitosa
        """
        try:
            local_path = Path(local_path)

            print("\n" + "=" * 60)
            print(f"[>>] Iniciando transferencia de archivo")
            print("=" * 60)
            print(f"[INFO] Archivo local: {local_path.name}")
            print(f"[INFO] Tamano: {local_path.stat().st_size:,} bytes")
            print(f"[INFO] Destino remoto: {remote_path}")
            print()

            # Transferir archivo
            print("[PROC] Iniciando transferencia SFTP...")
            sftp_client.put(str(local_path), remote_path)
            print("[OK] Archivo transferido exitosamente")
            print()

            # Verificar tamaño
            print("[CHK] Verificando integridad del archivo...")
            remote_size = sftp_client.stat(remote_path).st_size
            local_size = local_path.stat().st_size

            if remote_size == local_size:
                print(f"[OK] Verificacion exitosa: {local_size:,} bytes")
                print(f"[OK] Archivo remoto y local coinciden")
            else:
                print(f"[!] Advertencia: Tamano difiere")
                print(f"    Local: {local_size:,} bytes")
                print(f"    Remoto: {remote_size:,} bytes")
                return False

            # Extraer ZIP si se solicita
            if extraer and local_path.suffix == ".zip":
                print()
                print("[>>] Iniciando extraccion en servidor...")
                print(f"[INFO] Archivo ZIP: {remote_path}")

                # Obtener directorio de destino
                remote_dir = remote_path.rsplit("/", 1)[0]
                zip_filename = remote_path.rsplit("/", 1)[1]
                extract_dir = zip_filename.replace(".zip", "")

                print(f"[INFO] Directorio de extraccion: {remote_dir}/{extract_dir}/")
                print()

                # Ejecutar comando unzip en el servidor
                ssh_client = sftp_client.get_channel().get_transport().open_session()

                # Comando: cd al directorio, crear carpeta, extraer
                cmd = f"cd {remote_dir} && mkdir -p {extract_dir} && unzip -o {zip_filename} -d {extract_dir}"
                print(f"[PROC] Ejecutando comando de extraccion...")
                print(f"[CMD] {cmd}")
                print()

                ssh_client.exec_command(cmd)
                exit_status = ssh_client.recv_exit_status()

                if exit_status == 0:
                    print("[OK] Extraccion completada exitosamente")
                    print(f"[OK] Archivos extraidos en: {remote_dir}/{extract_dir}/")
                    print(f"[OK] Archivo ZIP original conservado: {remote_path}")
                else:
                    print(
                        f"[!] Advertencia: El comando de extraccion retorno codigo {exit_status}"
                    )
                    print(f"[TIP] Verifica que 'unzip' este instalado en el servidor")
                    print(
                        f"[TIP] Instalar con: sudo apt-get install unzip (Debian/Ubuntu)"
                    )

                ssh_client.close()

            print("=" * 60)
            return True

        except PermissionError as e:
            print(f"   [X] ERROR: Permiso denegado")
            print(f"      [TIP] Solución: En el servidor, ejecuta:")
            print(
                f"         sudo chown {sftp_client.normalize('').split('/')[-2]}:grupo {remote_path.rsplit('/', 2)[0]}/"
            )
            print(f"         sudo chmod 755 {remote_path.rsplit('/', 2)[0]}/")
            return False
        except IOError as e:
            if "Permission denied" in str(e) or "[Errno 13]" in str(e):
                print(f"   [X] ERROR: Permiso denegado para escribir en:")
                print(f"      {remote_path}")
                print(f"\n      [TIP] Soluciones posibles:")
                print(f"      1. Verifica que el directorio exista")
                print(f"      2. Verifica permisos del directorio")
                print(f"      3. En el servidor, ejecuta:")
                print(f"         sudo mkdir -p {remote_path.rsplit('/', 1)[0]}")
                print(
                    f"         sudo chown $USER:$USER {remote_path.rsplit('/', 1)[0]}"
                )
                print(f"         sudo chmod 755 {remote_path.rsplit('/', 1)[0]}")
            else:
                print(f"   [X] ERROR: {e}")
            return False
        except Exception as e:
            print(f"   [X] ERROR: {e}")
            return False

    def cerrar_conexion(self, sftp_client, ssh_client):
        """
        Cierra conexiones SFTP y SSH.

        Args:
            sftp_client: Cliente SFTP
            ssh_client: Cliente SSH
        """
        try:
            if sftp_client:
                sftp_client.close()
            if ssh_client:
                ssh_client.close()
            print("🔌 Conexión SFTP cerrada")
        except:
            pass
