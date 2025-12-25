"""
ESICORP Processor - Procesamiento seguro de archivos

Este módulo maneja el procesamiento de archivos según las especificaciones ESICORP:
- Patrón de archivos: Area-DD-MM-AAAA.Sede
- Integridad: SHA-256
- Codificación: Base64
- Confidencialidad: AES-256-CBC
- Empaquetado: ZIP

Autor: Grupo ESICORP - UNAD
"""

import os
import re
import hashlib
import base64
import zipfile
from pathlib import Path
from datetime import datetime
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


class ESICORPProcessor:
    """Procesador de archivos con seguridad ESICORP."""

    # Regex para archivos ESICORP: Area-DD-MM-AAAA.Sede
    FILE_PATTERN = re.compile(r"^[A-Za-z]+-\d{2}-\d{2}-\d{4}\.[A-Za-z]+$")

    def __init__(self, salida_dir="./salida", procesados_dir="./procesados"):
        """
        Inicializa el procesador ESICORP.

        Args:
            salida_dir (str): Directorio de archivos de entrada
            procesados_dir (str): Directorio de archivos procesados
        """
        self.salida_dir = Path(salida_dir)
        self.procesados_dir = Path(procesados_dir)
        self.salida_dir.mkdir(exist_ok=True)
        self.procesados_dir.mkdir(exist_ok=True)

    @staticmethod
    def calcular_hash_sha256(file_path):
        """
        INTEGRIDAD: Calcula el hash SHA-256 de un archivo.

        Args:
            file_path (Path): Ruta al archivo

        Returns:
            str: Hash SHA-256 en formato hexadecimal
        """
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    @staticmethod
    def generar_clave_aes():
        """
        CONFIDENCIALIDAD: Genera una clave AES-256 y un IV aleatorio.

        Returns:
            tuple: (clave de 32 bytes, IV de 16 bytes)
        """
        clave = os.urandom(32)  # AES-256 requiere 32 bytes
        iv = os.urandom(16)  # AES-CBC requiere IV de 16 bytes
        return clave, iv

    @staticmethod
    def cifrar_aes_256_cbc(data, clave, iv):
        """
        CONFIDENCIALIDAD: Cifra datos usando AES-256 en modo CBC.

        Args:
            data (bytes): Datos a cifrar
            clave (bytes): Clave AES de 32 bytes
            iv (bytes): Vector de inicialización de 16 bytes

        Returns:
            bytes: Datos cifrados
        """
        # Aplicar padding PKCS7
        padding_length = 16 - (len(data) % 16)
        data_padded = data + bytes([padding_length] * padding_length)

        # Crear cifrador AES-256-CBC
        cipher = Cipher(algorithms.AES(clave), modes.CBC(iv), backend=default_backend())

        encryptor = cipher.encryptor()
        encrypted_data = encryptor.update(data_padded) + encryptor.finalize()

        return encrypted_data

    def buscar_archivos(self, strict=True):
        """
        Busca archivos que cumplan con el patrón ESICORP.

        Args:
            strict (bool): Si True, solo acepta archivos con el patrón correcto.
                          Si False, acepta cualquier archivo.

        Returns:
            list: Lista de archivos Path que coinciden
        """
        archivos = []

        if not self.salida_dir.exists():
            return archivos

        for file_path in self.salida_dir.iterdir():
            if not file_path.is_file():
                continue

            if strict:
                if self.FILE_PATTERN.match(file_path.name):
                    archivos.append(file_path)
            else:
                # Modo no estricto: acepta cualquier archivo
                archivos.append(file_path)

        return archivos

    def procesar_archivo(self, file_path, verbose=True):
        """
        Procesa un archivo aplicando todas las capas de seguridad ESICORP.

        Flujo:
        1. INTEGRIDAD: Calcular hash SHA-256
        2. CODIFICACIÓN: Convertir a Base64
        3. CONFIDENCIALIDAD: Cifrar con AES-256-CBC
        4. EMPAQUETADO: Crear ZIP con .enc + .hash.txt + metadata

        Args:
            file_path (Path): Ruta al archivo a procesar
            verbose (bool): Mostrar mensajes de progreso

        Returns:
            Path: Ruta al archivo ZIP final, o None si falla
        """
        if verbose:
            print(f"\n📄 Procesando: {file_path.name}")
            print("-" * 60)

        try:
            base_name = file_path.stem

            # PASO 1: INTEGRIDAD - Calcular hash SHA-256
            if verbose:
                print("🔍 [INTEGRIDAD] Calculando hash SHA-256...")
            hash_original = self.calcular_hash_sha256(file_path)
            hash_file = self.procesados_dir / f"{base_name}.hash.txt"

            with open(hash_file, "w") as f:
                f.write(f"SHA-256: {hash_original}\n")
                f.write(f"Archivo: {file_path.name}\n")
                f.write(f"Fecha: {datetime.now().isoformat()}\n")

            if verbose:
                print(f"   ✅ Hash: {hash_original[:32]}...")

            # PASO 2: CODIFICACIÓN - Convertir a Base64
            if verbose:
                print("📝 [CODIFICACIÓN] Convirtiendo a Base64...")
            with open(file_path, "rb") as f:
                file_data = f.read()
            file_base64 = base64.b64encode(file_data)

            if verbose:
                print(f"   ✅ Codificado ({len(file_base64)} bytes)")

            # PASO 3: CONFIDENCIALIDAD - Cifrar con AES-256-CBC
            if verbose:
                print("🔐 [CONFIDENCIALIDAD] Cifrando con AES-256-CBC...")
            clave, iv = self.generar_clave_aes()
            encrypted_data = self.cifrar_aes_256_cbc(file_base64, clave, iv)

            # Guardar archivo cifrado (con IV y clave para demostración)
            enc_file = self.procesados_dir / f"{base_name}.enc"
            with open(enc_file, "wb") as f:
                # Formato: [IV 16 bytes][Clave 32 bytes][Datos cifrados]
                # NOTA: En producción, la clave se intercambiaría por canal separado
                f.write(iv)
                f.write(clave)
                f.write(encrypted_data)

            if verbose:
                print(f"   ✅ Cifrado ({len(encrypted_data)} bytes)")

            # PASO 4: EMPAQUETADO - Crear ZIP
            if verbose:
                print("📦 [EMPAQUETADO] Creando archivo ZIP...")
            zip_file = self.procesados_dir / f"{base_name}.zip"

            with zipfile.ZipFile(zip_file, "w", zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(enc_file, enc_file.name)
                zipf.write(hash_file, hash_file.name)

                # Añadir metadata
                metadata = f"""ESICORP - Archivo Seguro
Archivo Original: {file_path.name}
Procesado: {datetime.now().isoformat()}
Hash SHA-256: {hash_original}
Algoritmo Cifrado: AES-256-CBC
"""
                zipf.writestr("metadata.txt", metadata)

            # Limpiar archivos temporales
            enc_file.unlink()
            hash_file.unlink()

            if verbose:
                print(f"   ✅ ZIP creado: {zip_file.name}")
                print(f"   Tamaño: {zip_file.stat().st_size} bytes")
                print("✅ Procesamiento completado\n")

            return zip_file

        except Exception as e:
            print(f"❌ ERROR al procesar {file_path.name}: {e}")
            return None

    def procesar_desde_ruta(self, ruta, es_carpeta=False):
        """
        Procesa archivo(s) desde una ruta personalizada.

        Args:
            ruta (Path): Ruta al archivo o carpeta
            es_carpeta (bool): True si es una carpeta

        Returns:
            list: Lista de archivos ZIP procesados
        """
        archivos_a_procesar = []

        if es_carpeta:
            print(f"\n📁 Procesando archivos de la carpeta: {ruta}")
            # Buscar todos los archivos en la carpeta
            for file_path in ruta.iterdir():
                if file_path.is_file():
                    archivos_a_procesar.append(file_path)

            if not archivos_a_procesar:
                print("⚠️  No se encontraron archivos en la carpeta")
                return []

            print(f"✅ Encontrados {len(archivos_a_procesar)} archivo(s):")
            for f in archivos_a_procesar:
                print(f"   • {f.name}")
        else:
            # Es un archivo individual
            if not ruta.is_file():
                print(f"❌ La ruta no es un archivo: {ruta}")
                return []

            archivos_a_procesar = [ruta]
            print(f"📄 Procesando archivo: {ruta.name}")

        # Procesar cada archivo
        archivos_procesados = []
        for file_path in archivos_a_procesar:
            zip_file = self.procesar_archivo(file_path)
            if zip_file:
                archivos_procesados.append(zip_file)

        if archivos_procesados:
            print("\n" + "=" * 60)
            print(
                f"✅ Procesados: {len(archivos_procesados)}/{len(archivos_a_procesar)} archivos"
            )
            print("=" * 60)

        return archivos_procesados

    def procesar_todos(self, permitir_seleccion=True):
        """
        Busca y procesa todos los archivos que cumplan el patrón ESICORP.
        Si no encuentra archivos con el patrón y permitir_seleccion=True,
        permite procesar cualquier archivo.

        Args:
            permitir_seleccion (bool): Permitir procesar archivos sin patrón

        Returns:
            list: Lista de archivos ZIP procesados exitosamente
        """
        print("\n" + "=" * 60)
        print("BÚSQUEDA Y PROCESAMIENTO DE ARCHIVOS ESICORP")
        print("=" * 60)

        # Buscar archivos con patrón estricto
        archivos_encontrados = self.buscar_archivos(strict=True)

        if not archivos_encontrados:
            print("⚠️  No se encontraron archivos con el patrón: Area-DD-MM-AAAA.Sede")
            print(f"   Directorio: {self.salida_dir.absolute()}")
            print("\n   Ejemplos válidos:")
            print("   - Finanzas-12-12-2025.lima")
            print("   - Compras-23-02-2023.santiago")
            print("   - Ventas-10-11-2023.buenosaires")

            if permitir_seleccion:
                print(
                    "\n⚠️  ADVERTENCIA: Los archivos deben seguir el patrón para uso en producción."
                )
                continuar = input(
                    "\n¿Desea procesar TODOS los archivos en ./salida de todas formas? (s/n): "
                ).lower()

                if continuar == "s":
                    # Buscar cualquier archivo (modo no estricto)
                    archivos_encontrados = self.buscar_archivos(strict=False)

                    if not archivos_encontrados:
                        print("\n⚠️  No hay archivos en el directorio ./salida")
                        return []

                    print(
                        f"\n⚠️  Procesando {len(archivos_encontrados)} archivo(s) SIN validar patrón:"
                    )
                    for f in archivos_encontrados:
                        print(f"   • {f.name}")
                else:
                    return []
            else:
                return []

        else:
            print(
                f"✅ Encontrados {len(archivos_encontrados)} archivo(s) con patrón correcto:"
            )
            for f in archivos_encontrados:
                print(f"   • {f.name}")

        # Procesar cada archivo
        archivos_procesados = []
        for file_path in archivos_encontrados:
            zip_file = self.procesar_archivo(file_path)
            if zip_file:
                archivos_procesados.append(zip_file)

        print("=" * 60)
        print(
            f"✅ Procesamiento completado: {len(archivos_procesados)}/{len(archivos_encontrados)} archivos"
        )
        print("=" * 60)

        return archivos_procesados
