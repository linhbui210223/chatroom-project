import unittest
import os
import base64
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

from server.encryption import (
    generate_aes_key,
    encrypt_aes,
    decrypt_aes,
    load_rsa_public_key,
    load_rsa_private_key,
    encrypt_rsa,
    decrypt_rsa,
)

class TestEncryption(unittest.TestCase):

    def test_aes_encryption_decryption(self):
        aes_key = generate_aes_key()
        message = "This is a secret message."

        encrypted_message = encrypt_aes(aes_key, message)
        decrypted_message = decrypt_aes(aes_key, encrypted_message)

        self.assertEqual(message, decrypted_message)

    def test_rsa_encryption_decryption(self):
        # Generate RSA keys for testing
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        public_key = private_key.public_key()

        # Serialize keys to PEM format for loading
        private_key_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        )
        public_key_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

        # Save keys to temporary files
        with open("temp_private_key.pem", "wb") as f:
            f.write(private_key_pem)
        with open("temp_public_key.pem", "wb") as f:
            f.write(public_key_pem)

        # Load keys from files
        loaded_private_key = load_rsa_private_key("temp_private_key.pem")
        loaded_public_key = load_rsa_public_key("temp_public_key.pem")

        # Test encryption and decryption
        message = b"This is a secret message."
        encrypted_message = encrypt_rsa(loaded_public_key, message)
        decrypted_message = decrypt_rsa(loaded_private_key, encrypted_message)

        self.assertEqual(message, decrypted_message)

        # Clean up temporary files
        os.remove("temp_private_key.pem")
        os.remove("temp_public_key.pem")

if __name__ == "__main__":
    unittest.main()