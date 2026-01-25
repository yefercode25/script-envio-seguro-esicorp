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
from pathlib import Path
from datetime import datetime
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


class ESICORPProcessor:
    """Procesador de archivos con seguridad ESICORP."""

    # Regex para archivos ESICORP - Anexo 6
    # Formato: (FE|NOM|EQUIV)-NNNNNNNN.txt
    # FE = Factura Electrónica, NOM = Nómina, EQUIV = Documento Equivalente
    FILE_PATTERN = re.compile(r"^(FE|NOM|EQUIV)-\d{8}\.txt$")

    def __init__(self, salida_dir="./salida", procesados_dir="./procesados"):
        """
        Inicializa el procesador ESICORP.

        Args:
            salida_dir (str): Directorio de archivos de entrada (Anexo 6: /Dian/XXX)
            procesados_dir (str): Directorio de archivos procesados
        """
        self.salida_dir = Path(salida_dir)
        self.procesados_dir = Path(procesados_dir)

        # Validar que el directorio de salida existe (CRÍTICO para Anexo 6)
        if not self.salida_dir.exists():
            print(f"\n{'=' * 60}")
            print("[!] ADVERTENCIA: Directorio de origen no encontrado")
            print(f"{'=' * 60}")
            print(f"Directorio: {self.salida_dir.absolute()}")
            print()
            print("[INFO] Para cumplir con el Anexo 6 de ESICORP:")
            print("   1. La ruta debe ser: /Dian/XXX (donde XXX es la sede)")
            print("   2. Configure la variable de entorno ESICORP_DIAN_PATH")
            print("   3. Cree el directorio con permisos adecuados:")
            print()
            print(f"      sudo mkdir -p {self.salida_dir}")
            print(f"      sudo chown $USER:$USER {self.salida_dir}")
            print(f"      sudo chmod 755 {self.salida_dir}")
            print()
            print("[INFO] Creando directorio automáticamente para desarrollo...")
            print(f"{'=' * 60}\n")

            # Crear directorio para desarrollo/testing
            self.salida_dir.mkdir(parents=True, exist_ok=True)

        # Crear directorio de procesados
        self.procesados_dir.mkdir(parents=True, exist_ok=True)

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

    @staticmethod
    def descifrar_aes_256_cbc(encrypted_data, clave, iv):
        """
        CONFIDENCIALIDAD: Descifra datos usando AES-256 en modo CBC.

        Args:
            encrypted_data (bytes): Datos cifrados
            clave (bytes): Clave AES de 32 bytes
            iv (bytes): Vector de inicialización de 16 bytes

        Returns:
            bytes: Datos descifrados sin padding
        """
        # Crear descifrador AES-256-CBC
        cipher = Cipher(algorithms.AES(clave), modes.CBC(iv), backend=default_backend())

        decryptor = cipher.decryptor()
        decrypted_data_padded = decryptor.update(encrypted_data) + decryptor.finalize()

        # Remover padding PKCS7
        padding_length = decrypted_data_padded[-1]
        decrypted_data = decrypted_data_padded[:-padding_length]

        return decrypted_data

    def buscar_archivos_encriptados(self, directorio):
        """
        Busca archivos .enc que tengan su correspondiente .hash.txt

        Args:
            directorio (Path o str): Directorio donde buscar

        Returns:
            list: Lista de tuplas (enc_file, hash_file) de archivos completos
        """
        directorio = Path(directorio)
        pares_completos = []

        if not directorio.exists():
            return pares_completos

        # Buscar todos los archivos .enc
        archivos_enc = list(directorio.glob("*.enc"))

        for enc_file in archivos_enc:
            # Buscar el archivo .hash.txt correspondiente
            base_name = enc_file.stem  # nombre sin extensión
            hash_file = directorio / f"{base_name}.hash.txt"

            if hash_file.exists():
                pares_completos.append((enc_file, hash_file))

        return pares_completos

    def desencriptar_archivo(
        self, enc_file, hash_file, verificar_hash=True, verbose=True
    ):
        """
        Desencripta un archivo .enc y verifica su integridad.

        Flujo inverso al cifrado:
        1. Verificar hash SHA-256 del archivo cifrado
        2. Leer archivo .enc (IV + clave + datos cifrados)
        3. Descifrar con AES-256-CBC
        4. Decodificar de Base64
        5. Guardar archivo original

        Args:
            enc_file (Path): Archivo cifrado (.enc)
            hash_file (Path): Archivo con hash (.hash.txt)
            verificar_hash (bool): Si True, verifica integridad antes de descifrar
            verbose (bool): Mostrar mensajes de progreso

        Returns:
            Path: Ruta al archivo desencriptado, o None si falla
        """
        if verbose:
            print(f"\n[PROC] Desencriptando: {enc_file.name}")
            print("-" * 60)

        try:
            # PASO 1: Verificar integridad (opcional pero recomendado)
            if verificar_hash:
                if verbose:
                    print("[1/4] [INTEGRIDAD] Verificando hash SHA-256...")

                # Leer hash esperado
                with open(hash_file, "r") as f:
                    lineas = f.readlines()
                    hash_esperado = lineas[0].split(": ")[1].strip()

                # Calcular hash del archivo cifrado
                hash_actual = self.calcular_hash_sha256(enc_file)

                if hash_actual != hash_esperado:
                    print(f"   [X] Hash no coincide!")
                    print(f"       Esperado: {hash_esperado[:32]}...")
                    print(f"       Actual:   {hash_actual[:32]}...")
                    return None

                if verbose:
                    print(f"   [OK] Hash verificado correctamente")

            # PASO 2: Leer archivo cifrado
            if verbose:
                print("[2/4] [LECTURA] Leyendo archivo cifrado...")

            with open(enc_file, "rb") as f:
                # Formato: [IV 16 bytes][Clave 32 bytes][Datos cifrados]
                iv = f.read(16)
                clave = f.read(32)
                encrypted_data = f.read()

            if verbose:
                print(
                    f"   [OK] Leídos: IV ({len(iv)}B), Clave ({len(clave)}B), Datos ({len(encrypted_data)}B)"
                )

            # PASO 3: Descifrar con AES-256-CBC
            if verbose:
                print("[3/4] [CONFIDENCIALIDAD] Descifrando con AES-256-CBC...")

            decrypted_base64 = self.descifrar_aes_256_cbc(encrypted_data, clave, iv)

            if verbose:
                print(f"   [OK] Descifrado ({len(decrypted_base64)} bytes)")

            # PASO 4: Decodificar de Base64
            if verbose:
                print("[4/4] [CODIFICACIÓN] Decodificando de Base64...")

            original_data = base64.b64decode(decrypted_base64)

            if verbose:
                print(f"   [OK] Decodificado ({len(original_data)} bytes)")

            # PASO 5: Guardar archivo original
            # Nombre: quitar .enc y agregar .txt
            output_file = enc_file.parent / f"{enc_file.stem}_decrypted.txt"

            with open(output_file, "wb") as f:
                f.write(original_data)

            if verbose:
                print(f"\n[OK] Archivo desencriptado exitosamente")
                print(f"   [>>] Guardado en: {output_file.name}")
                print(f"   [>>] Tamaño: {len(original_data)} bytes")

            return output_file

        except Exception as e:
            print(f"[X] ERROR al desencriptar {enc_file.name}: {e}")
            import traceback

            traceback.print_exc()
            return None

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

        Flujo según Anexo 6:
        1. CODIFICACIÓN: Convertir a Base64 (Unicode64)
        2. CONFIDENCIALIDAD: Cifrar con AES-256-CBC
        3. INTEGRIDAD: Calcular hash SHA-256 del archivo CIFRADO

        Args:
            file_path (Path): Ruta al archivo a procesar
            verbose (bool): Mostrar mensajes de progreso

        Returns:
            tuple: (enc_file, hash_file) para transmisión dual, o (None, None) si falla
        """
        if verbose:
            print(f"\n[PROC] Procesando: {file_path.name}")
            print("-" * 60)

        try:
            base_name = file_path.stem

            # PASO 1: CODIFICACIÓN - Base64 (Unicode64 según Anexo 6)
            if verbose:
                print("[1/3] [CODIFICACIÓN] Convirtiendo a Base64 (Unicode64)...")
            with open(file_path, "rb") as f:
                file_data = f.read()
            file_base64 = base64.b64encode(file_data)

            if verbose:
                print(f"   [OK] Codificado ({len(file_base64)} bytes)")

            # PASO 2: CONFIDENCIALIDAD - Cifrar con AES-256-CBC
            if verbose:
                print("[2/3] [CONFIDENCIALIDAD] Cifrando con AES-256-CBC...")
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
                print(f"   [OK] Cifrado ({len(encrypted_data)} bytes)")
                print(f"   [OK] Archivo cifrado: {enc_file.name}")

            # PASO 3: INTEGRIDAD - Calcular hash SHA-256 del archivo CIFRADO
            if verbose:
                print(
                    "[3/3] [INTEGRIDAD] Calculando hash SHA-256 del archivo cifrado..."
                )

            # ✅ CORREGIDO: Hash del archivo cifrado, NO del original
            hash_cifrado = self.calcular_hash_sha256(enc_file)
            hash_file = self.procesados_dir / f"{base_name}.hash.txt"

            with open(hash_file, "w") as f:
                f.write(f"SHA-256: {hash_cifrado}\n")
                f.write(f"Archivo Cifrado: {enc_file.name}\n")
                f.write(f"Archivo Original: {file_path.name}\n")
                f.write(f"Fecha: {datetime.now().isoformat()}\n")

            if verbose:
                print(f"   [OK] Hash del cifrado: {hash_cifrado[:32]}...")

            # ✅ ANEXO 6: NO empaquetar en ZIP
            # El Anexo 6 requiere transmisión DUAL de archivos separados:
            # 1. archivo.enc (archivo cifrado)
            # 2. archivo.hash (hash SHA-256 del cifrado)

            if verbose:
                print("\n[OK] Procesamiento completado")
                print("   [>>] Archivos generados para transmisión:")
                print(f"       1. {enc_file.name} ({enc_file.stat().st_size} bytes)")
                print(f"       2. {hash_file.name} ({hash_file.stat().st_size} bytes)")

            # Retornar tupla con ambos archivos (transmisión dual)
            return enc_file, hash_file

        except Exception as e:
            print(f"[X] ERROR al procesar {file_path.name}: {e}")
            return None, None

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
            print(f"\n[DIR] Procesando archivos de la carpeta: {ruta}")
            # Buscar todos los archivos en la carpeta
            for file_path in ruta.iterdir():
                if file_path.is_file():
                    archivos_a_procesar.append(file_path)

            if not archivos_a_procesar:
                print("[!]  No se encontraron archivos en la carpeta")
                return []

            print(f"[OK] Encontrados {len(archivos_a_procesar)} archivo(s):")
            for f in archivos_a_procesar:
                print(f"   • {f.name}")
        else:
            # Es un archivo individual
            if not ruta.is_file():
                print(f"[X] La ruta no es un archivo: {ruta}")
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
                f"[OK] Procesados: {len(archivos_procesados)}/{len(archivos_a_procesar)} archivos"
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
            print("[!]  No se encontraron archivos con el patrón del Anexo 6")
            print(f"   Directorio: {self.salida_dir.absolute()}")
            print("\n[INFO] Patrón requerido (Anexo 6): (FE|NOM|EQUIV)-NNNNNNNN.txt")
            print("   - FE     = Factura Electrónica")
            print("   - NOM    = Nómina Electrónica")
            print("   - EQUIV  = Documento Equivalente")
            print("\n   Ejemplos válidos:")
            print("   - FE-20250122.txt")
            print("   - NOM-20231215.txt")
            print("   - EQUIV-20240310.txt")

            if permitir_seleccion:
                print(
                    "\n[!]  ADVERTENCIA: Los archivos deben seguir el patrón para uso en producción."
                )
                continuar = input(
                    "\n¿Desea procesar TODOS los archivos en ./salida de todas formas? (s/n): "
                ).lower()

                if continuar == "s":
                    # Buscar cualquier archivo (modo no estricto)
                    archivos_encontrados = self.buscar_archivos(strict=False)

                    if not archivos_encontrados:
                        print("\n[!]  No hay archivos en el directorio ./salida")
                        return []

                    print(
                        f"\n[!]  Procesando {len(archivos_encontrados)} archivo(s) SIN validar patrón:"
                    )
                    for f in archivos_encontrados:
                        print(f"   • {f.name}")
                else:
                    return []
            else:
                return []

        else:
            print(
                f"[OK] Encontrados {len(archivos_encontrados)} archivo(s) con patrón correcto:"
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
            f"[OK] Procesamiento completado: {len(archivos_procesados)}/{len(archivos_encontrados)} archivos"
        )
        print("=" * 60)

        return archivos_procesados
