import os
import base64
import hashlib
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from . import config
from .utils import print_crypto, print_error


class CryptoManager:
    def __init__(self):
        print_crypto("Inicializando motor criptográfico...")
        print_crypto(f"Algoritmo: AES-256-GCM (Galois/Counter Mode)")
        print_crypto(f"Derivación de clave: PBKDF2HMAC-SHA256")

        self.key = self._derive_key(config.SHARED_PASSWORD, config.SALT)
        self.aesgcm = AESGCM(base64.urlsafe_b64decode(self.key))

        print_crypto("Motor criptográfico listo.")

    def _derive_key(self, password: str, salt: bytes) -> bytes:
        print_crypto(f"Derivando clave maestra...")
        print_crypto(f"  - Password: {'*' * len(password)}")
        print_crypto(f"  - Salt: {salt.hex()} (Protección contra Rainbow Tables)")
        print_crypto(f"  - Iteraciones: {config.KDF_ITERATIONS} (Factor de trabajo)")

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=config.KEY_LENGTH,
            salt=salt,
            iterations=config.KDF_ITERATIONS,
        )
        derived_key = base64.urlsafe_b64encode(kdf.derive(password.encode()))

        print_crypto(
            f"  - Clave derivada (32 bytes): {derived_key[:10].decode()}...[TRUNCADO]"
        )
        return derived_key

    def encrypt_data(self, data: bytes) -> tuple[bytes, bytes]:
        print_crypto("Iniciando proceso de cifrado simétrico...")

        # Generar Nonce
        nonce = os.urandom(12)
        print_crypto(f"  1. Generando Nonce aleatorio (12 bytes): {nonce.hex()}")
        print_crypto("     (Esencial para evitar patrones en mensajes repetidos)")

        # Cifrar
        print_crypto(f"  2. Cifrando {len(data)} bytes de datos...")
        ciphertext = self.aesgcm.encrypt(nonce, data, None)

        # El tag de autenticación está al final del ciphertext en esta implementación de cryptography
        tag_size = 16
        actual_ciphertext_len = len(ciphertext) - tag_size

        print_crypto(f"  3. Generando Tag de Autenticación (16 bytes) para integridad.")
        print_crypto(f"  - Resultado: {len(ciphertext)} bytes (Ciphertext + Tag)")

        return nonce, ciphertext

    def decrypt_data(self, nonce: bytes, ciphertext: bytes) -> bytes:
        """
        Descifra los datos usando AES-GCM.
        Lanza una excepción si la autenticación falla.
        """
        print_crypto("Iniciando proceso de descifrado y verificación...")
        print_crypto(f"  - Nonce recibido: {nonce.hex()}")
        print_crypto(f"  - Tamaño del criptograma: {len(ciphertext)} bytes")

        try:
            print_crypto("  1. Verificando Tag de Autenticación (Integridad)...")
            plaintext = self.aesgcm.decrypt(nonce, ciphertext, None)
            print_crypto("     ✅ Tag válido. Los datos no han sido manipulados.")

            print_crypto("  2. Descifrando contenido (Confidencialidad)...")
            print_crypto(f"     ✅ Datos recuperados: {len(plaintext)} bytes.")
            return plaintext
        except Exception as e:
            print_error(
                "Fallo en descifrado: La integridad del archivo está comprometida o la clave es incorrecta."
            )
            print_crypto(
                "     ❌ El Tag de autenticación GCM no coincide. ¡ALERTA DE SEGURIDAD!"
            )
            raise e

    def generate_hash(self, data: bytes) -> str:
        print_crypto("Calculando Huella Digital (Hash)...")
        print_crypto("  - Algoritmo: SHA-256")
        digest = hashlib.sha256(data).hexdigest()
        print_crypto(f"  - Hash resultante: {digest}")
        return digest
