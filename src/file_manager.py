import os
import zipfile
import shutil
import re
import unicodedata
import tempfile
from . import config
from .utils import print_file, print_error, print_success, print_info


class FileManager:
    def __init__(self):
        self.session_id = None
        self.sender_dir = None
        self.receiver_dir = None

    def setup_session(self, session_id: str):
        """Configura los directorios de la sesión actual (Timestamp)."""
        self.session_id = session_id
        session_path = os.path.join(config.BASE_DIR, session_id)

        self.sender_dir = os.path.join(session_path, "sender")
        self.receiver_dir = os.path.join(session_path, "receiver")

        # Crear estructura
        for d in [self.sender_dir, self.receiver_dir]:
            if not os.path.exists(d):
                os.makedirs(d)

        print_file(f"Entorno de trabajo configurado: {session_path}")

    def get_sender_path(self, filename):
        if not self.sender_dir:
            raise Exception("Sesión no iniciada")
        return os.path.join(self.sender_dir, filename)

    def get_receiver_path(self, filename):
        if not self.receiver_dir:
            raise Exception("Sesión no iniciada")
        return os.path.join(self.receiver_dir, filename)

    def sanitize_name(self, name):
        """Elimina caracteres especiales y normaliza el nombre."""
        nfkd_form = unicodedata.normalize("NFKD", name)
        name = "".join([c for c in nfkd_form if not unicodedata.combining(c)])
        name = re.sub(r"[^a-zA-Z0-9._-]", "_", name)
        if not name:
            name = "unnamed_file"
        return name

    def stage_files(self, original_path):
        """
        Crea una copia temporal de los archivos con nombres saneados en el directorio temporal del sistema.
        Retorna (ruta_raiz_temporal, ruta_contenido_saneado).
        """
        print_file("Iniciando 'Staging' (Preparación de Archivos)...")

        # Crear directorio temporal en el sistema (%TEMP%)
        staging_root = tempfile.mkdtemp(prefix="st_staging_")
        print_file(f"  - Directorio temporal aislado: {staging_root}")

        # Manejo de rutas largas en Windows para el origen
        abs_source = os.path.abspath(original_path)
        if os.name == "nt":
            abs_source = abs_source.replace("/", "\\")
            if not abs_source.startswith("\\\\?\\"):
                abs_source = f"\\\\?\\{abs_source}"

        # Nombre base saneado
        clean_original_path = original_path.rstrip(os.sep)
        basename = os.path.basename(clean_original_path)
        sanitized_base = self.sanitize_name(basename)

        # Destino dentro del temp
        dest_path = os.path.join(staging_root, sanitized_base)

        if os.name == "nt":
            dest_path = os.path.abspath(dest_path).replace("/", "\\")
            if not dest_path.startswith("\\\\?\\"):
                dest_path = f"\\\\?\\{dest_path}"

        try:
            if os.path.isfile(abs_source):
                shutil.copy2(abs_source, dest_path)
                print_file(f"  - Archivo único copiado y renombrado: {sanitized_base}")
            else:
                if not os.path.exists(dest_path):
                    os.makedirs(dest_path)

                print_file(f"  - Copiando estructura de directorio recursivamente...")
                file_count = 0
                for root, dirs, files in os.walk(abs_source):
                    rel_path = os.path.relpath(root, abs_source)

                    if rel_path == ".":
                        current_dest_dir = dest_path
                    else:
                        parts = rel_path.split(os.sep)
                        sanitized_parts = [self.sanitize_name(p) for p in parts]
                        current_dest_dir = os.path.join(dest_path, *sanitized_parts)

                    if not os.path.exists(current_dest_dir):
                        os.makedirs(current_dest_dir)

                    for file in files:
                        sanitized_file = self.sanitize_name(file)
                        src_file = os.path.join(root, file)
                        dst_file = os.path.join(current_dest_dir, sanitized_file)
                        shutil.copy2(src_file, dst_file)
                        file_count += 1

                print_file(f"  - Total archivos procesados: {file_count}")

            print_file("  ✅ Staging completado. Archivos listos y saneados.")
            return staging_root, dest_path
        except Exception as e:
            shutil.rmtree(staging_root, ignore_errors=True)
            print_error(f"Error al preparar archivos (staging): {e}")
            raise

    def compress_path(self, path: str) -> str:
        if not self.sender_dir:
            raise Exception("Sesión no iniciada")

        print_file("Comprimiendo datos...")
        # 1. Crear copia saneada (Staging) en TEMP
        staging_root, staged_path = self.stage_files(path)

        # 2. Comprimir la copia saneada
        zip_filename = "temp.zip"
        zip_path = os.path.join(self.sender_dir, zip_filename)

        try:
            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                if os.path.isdir(staged_path):
                    parent_dir = os.path.dirname(staged_path)
                    for root, dirs, files in os.walk(staged_path):
                        for file in files:
                            file_abs_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_abs_path, parent_dir)
                            zipf.write(file_abs_path, arcname)
                else:
                    filename = os.path.basename(staged_path)
                    zipf.write(staged_path, filename)

            size_mb = os.path.getsize(zip_path) / (1024 * 1024)
            print_file(f"  - Archivo ZIP generado: {zip_path}")
            print_file(f"  - Tamaño comprimido: {size_mb:.2f} MB")
            return zip_path
        except Exception as e:
            print_error(f"Error al comprimir: {e}")
            raise
        finally:
            if os.path.exists(staging_root):
                try:
                    shutil.rmtree(staging_root)
                    print_file("  - Limpieza: Directorio temporal eliminado.")
                except Exception:
                    pass

    def decompress_file(self, zip_path: str) -> str:
        if not self.receiver_dir:
            raise Exception("Sesión no iniciada")

        try:
            print_file("Descomprimiendo archivo recibido...")
            extract_path = os.path.join(self.receiver_dir, "decrypted_files")

            if not os.path.exists(extract_path):
                os.makedirs(extract_path)

            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                file_count = len(zip_ref.namelist())
                zip_ref.extractall(extract_path)
                print_file(f"  - {file_count} archivos extraídos.")
                print_file(f"  - Ubicación: {extract_path}")

            return extract_path
        except Exception as e:
            print_error(f"Error al descomprimir: {e}")
            raise

    def read_binary(self, file_path: str) -> bytes:
        with open(file_path, "rb") as f:
            return f.read()

    def write_binary(self, file_path: str, data: bytes):
        with open(file_path, "wb") as f:
            f.write(data)

    def save_package(
        self, original_path: str, nonce: bytes, file_hash: str, ciphertext: bytes
    ) -> str:
        if not self.sender_dir:
            raise Exception("Sesión no iniciada")

        print_file("Generando Paquete Seguro (.enc)...")
        print_file("  Estructura del Paquete:")
        print_file(f"  [Nonce: 12b] + [Hash: 64b] + [Ciphertext: {len(ciphertext)}b]")

        package_filename = "payload.enc"
        package_path = os.path.join(self.sender_dir, package_filename)

        with open(package_path, "wb") as f:
            f.write(nonce)
            f.write(file_hash.encode("utf-8"))
            f.write(ciphertext)

        print_file(f"  ✅ Paquete guardado en: {package_path}")
        return package_path

    def read_package(self, package_path: str) -> tuple[bytes, str, bytes]:
        print_file("Leyendo Paquete Seguro...")
        with open(package_path, "rb") as f:
            nonce = f.read(12)
            file_hash = f.read(64).decode("utf-8")
            ciphertext = f.read()

        print_file(f"  - Nonce extraído: {nonce.hex()}")
        print_file(f"  - Hash original extraído: {file_hash}")
        print_file(f"  - Criptograma extraído: {len(ciphertext)} bytes")
        return nonce, file_hash, ciphertext

    def cleanup(self, file_path: str):
        if os.path.exists(file_path):
            os.remove(file_path)
            print_file(
                f"Limpieza: Archivo temporal {os.path.basename(file_path)} eliminado."
            )

    def clear_all_transfers(self):
        if not os.path.exists(config.BASE_DIR):
            print_info("No hay historial de transferencias para borrar.")
            return

        print_file(f"Limpiando directorio de transferencias: {config.BASE_DIR}")
        try:
            count = 0
            for item in os.listdir(config.BASE_DIR):
                item_path = os.path.join(config.BASE_DIR, item)
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                    print_file(f"  - Sesión eliminada: {item}")
                    count += 1
            print_success(f"Historial borrado. {count} sesiones eliminadas.")
        except Exception as e:
            print_error(f"Error al borrar historial: {e}")
