"""
Script de desencriptacion ESICORP para ejecutar en el servidor Linux

Este script se ejecuta en el servidor después de recibir y extraer los archivos.
Realiza el proceso inverso: Base64 decode -> AES decrypt -> verify hash -> archivo original
"""

import os
import sys
import base64
import hashlib
from pathlib import Path
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


def descifrar_archivo(archivo_enc, archivo_salida):
    """
    Descifra un archivo .enc y lo devuelve a su estado original

    Args:
        archivo_enc: Archivo cifrado (.enc)
        archivo_salida: Nombre del archivo original a crear

    Returns:
        bool: True si el descifrado fue exitoso
    """
    try:
        print(f"[PROC] Descifrando: {archivo_enc}")

        # Leer archivo cifrado (Base64)
        with open(archivo_enc, "rb") as f:
            datos_base64 = f.read()

        # Decodificar Base64
        print("  [>>] Decodificando Base64...")
        datos_cifrados = base64.b64decode(datos_base64)

        # Extraer IV (primeros 16 bytes)
        iv = datos_cifrados[:16]
        datos_cifrados = datos_cifrados[16:]

        # Extraer clave (últimos 32 bytes)
        clave = datos_cifrados[-32:]
        datos_cifrados = datos_cifrados[:-32]

        print(f"  [>>] Descifrando AES-256-CBC...")

        # Descifrar con AES
        cipher = Cipher(algorithms.AES(clave), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        datos_descifrados = decryptor.update(datos_cifrados) + decryptor.finalize()

        # Remover padding PKCS7
        padding_length = datos_descifrados[-1]
        datos_originales = datos_descifrados[:-padding_length]

        # Guardar archivo original
        with open(archivo_salida, "wb") as f:
            f.write(datos_originales)

        print(f"  [OK] Archivo descifrado: {archivo_salida}")
        print(f"  [OK] Tamaño: {len(datos_originales)} bytes")

        return True

    except Exception as e:
        print(f"  [X] Error al descifrar: {e}")
        return False


def verificar_hash(archivo, archivo_hash):
    """
    Verifica el hash SHA-256 del archivo

    Args:
        archivo: Archivo a verificar
        archivo_hash: Archivo .hash.txt con el hash esperado

    Returns:
        bool: True si el hash coincide
    """
    try:
        print(f"[CHK] Verificando integridad...")

        # Leer hash esperado
        with open(archivo_hash, "r") as f:
            hash_esperado = f.read().strip()

        # Calcular hash del archivo
        sha256 = hashlib.sha256()
        with open(archivo, "rb") as f:
            while chunk := f.read(8192):
                sha256.update(chunk)
        hash_calculado = sha256.hexdigest()

        if hash_calculado == hash_esperado:
            print(f"  [OK] Hash verificado correctamente")
            print(f"  [OK] SHA-256: {hash_calculado[:16]}...")
            return True
        else:
            print(f"  [X] Hash NO coincide!")
            print(f"      Esperado: {hash_esperado}")
            print(f"      Calculado: {hash_calculado}")
            return False

    except Exception as e:
        print(f"  [X] Error al verificar hash: {e}")
        return False


def procesar_directorio(directorio):
    """
    Procesa todos los archivos .enc en un directorio

    Args:
        directorio: Directorio con archivos extraídos
    """
    directorio = Path(directorio)

    if not directorio.exists():
        print(f"[X] Directorio no existe: {directorio}")
        return

    print("\n" + "=" * 60)
    print("DESENCRIPTACION AUTOMATICA - SERVIDOR ESICORP")
    print("=" * 60)
    print(f"[INFO] Directorio: {directorio}")
    print()

    # Buscar archivos .enc
    archivos_enc = list(directorio.glob("*.enc"))

    if not archivos_enc:
        print("[i] No se encontraron archivos cifrados (.enc)")
        return

    print(f"[INFO] Encontrados {len(archivos_enc)} archivo(s) cifrado(s)")
    print()

    exitos = 0
    for archivo_enc in archivos_enc:
        # Determinar nombre del archivo original (quitar .enc)
        nombre_base = archivo_enc.stem
        archivo_salida = directorio / nombre_base
        archivo_hash = directorio / f"{nombre_base}.hash.txt"

        # Descifrar
        if descifrar_archivo(archivo_enc, archivo_salida):
            # Verificar hash si existe
            if archivo_hash.exists():
                if verificar_hash(archivo_salida, archivo_hash):
                    exitos += 1
                    print(f"  [***] Archivo restaurado exitosamente")
                else:
                    print(f"  [!] Archivo descifrado pero hash no coincide")
                    # Eliminar archivo con hash incorrecto
                    archivo_salida.unlink()
            else:
                print(f"  [!] No hay archivo hash para verificar")
                exitos += 1

        print()

    print("=" * 60)
    print(f"[OK] Procesados: {exitos}/{len(archivos_enc)} archivos")
    print("=" * 60)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 decrypt_esicorp.py <directorio>")
        sys.exit(1)

    directorio = sys.argv[1]
    procesar_directorio(directorio)
