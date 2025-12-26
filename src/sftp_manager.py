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
            print("🔑 Generando llaves RSA de 4096 bits...")
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

            print(f"✅ Llaves generadas exitosamente:")
            print(f"   Privada: {self.private_key_path}")
            print(f"   Pública: {self.public_key_path}")

            return self.private_key_path, self.public_key_path

        except Exception as e:
            print(f"❌ Error al generar llaves: {e}")
            return None, None

    def mostrar_instrucciones_configuracion(self, hostname, username):
        """
        Muestra instrucciones para configurar la llave pública en el servidor.

        Args:
            hostname (str): Nombre o IP del servidor
            username (str): Usuario del servidor
        """
        print("\n" + "🔴" * 30)
        print("⚠️  CONFIGURACIÓN REQUERIDA - SERVIDOR LINUX ⚠️")
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
            print("❌ ERROR: paramiko no está instalado")
            print("   Ejecute: pip install paramiko")
            return None, None

        if not self.verificar_llaves():
            print("❌ ERROR: No se encontraron llaves RSA")
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

            print("✅ Conexión SFTP establecida exitosamente")
            return sftp_client, ssh_client

        except paramiko.AuthenticationException:
            print("\n❌ ERROR DE AUTENTICACIÓN")
            print("=" * 60)
            print("La llave pública no está configurada en el servidor.")
            self.mostrar_instrucciones_configuracion(hostname, username)
            return None, None

        except paramiko.SSHException as e:
            print(f"❌ ERROR SSH: {e}")
            return None, None

        except Exception as e:
            print(f"❌ ERROR de conexión: {e}")
            print(f"   Verifique que {hostname}:{port} sea accesible")
            return None, None

    def subir_archivo(self, sftp_client, local_path, remote_path):
        """
        Sube un archivo al servidor SFTP.

        Args:
            sftp_client: Cliente SFTP conectado
            local_path (str/Path): Ruta local del archivo
            remote_path (str): Ruta remota de destino

        Returns:
            bool: True si la subida fue exitosa
        """
        try:
            local_path = Path(local_path)

            print(f"📤 Subiendo: {local_path.name}")
            print(f"   Destino: {remote_path}")

            # Transferir archivo
            sftp_client.put(str(local_path), remote_path)

            # Verificar tamaño
            remote_size = sftp_client.stat(remote_path).st_size
            local_size = local_path.stat().st_size

            if remote_size == local_size:
                print(f"   ✅ Subido exitosamente ({local_size} bytes)")
                return True
            else:
                print(f"   ⚠️  Advertencia: Tamaño difiere")
                return False

        except PermissionError as e:
            print(f"   ❌ ERROR: Permiso denegado")
            print(f"      💡 Solución: En el servidor, ejecuta:")
            print(
                f"         sudo chown {sftp_client.normalize('').split('/')[-2]}:grupo {remote_path.rsplit('/', 2)[0]}/"
            )
            print(f"         sudo chmod 755 {remote_path.rsplit('/', 2)[0]}/")
            return False
        except IOError as e:
            if "Permission denied" in str(e) or "[Errno 13]" in str(e):
                print(f"   ❌ ERROR: Permiso denegado para escribir en:")
                print(f"      {remote_path}")
                print(f"\n      💡 Soluciones posibles:")
                print(f"      1. Verifica que el directorio exista")
                print(f"      2. Verifica permisos del directorio")
                print(f"      3. En el servidor, ejecuta:")
                print(f"         sudo mkdir -p {remote_path.rsplit('/', 1)[0]}")
                print(
                    f"         sudo chown $USER:$USER {remote_path.rsplit('/', 1)[0]}"
                )
                print(f"         sudo chmod 755 {remote_path.rsplit('/', 1)[0]}")
            else:
                print(f"   ❌ ERROR: {e}")
            return False
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
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
