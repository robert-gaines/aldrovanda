from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import logging

logging.basicConfig(level=logging.INFO)

def decrypt_file(encrypted_filename, key) -> None:
    try:
        if len(key) not in [16, 24, 32]:
            raise ValueError("Invalid key size for AES. Key must be 16, 24, or 32 bytes long.")
        with open(encrypted_filename, 'rb') as encrypted_file:
            iv = encrypted_file.read(16)
            encrypted_data = encrypted_file.read()
        cipher = Cipher(algorithms.AES(key), modes.CFB(iv))
        decryptor = cipher.decryptor()
        decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()
        original_filename = encrypted_filename.replace('.enc', '')
        with open(original_filename, 'wb') as decrypted_file:
            decrypted_file.write(decrypted_data)
        print(f"File '{encrypted_filename}' has been decrypted and saved as '{original_filename}'")
    except Exception as e:
        logging.exception("Exception: {0}".format(e))
        print(f"Failed to decrypt file '{encrypted_filename}'")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python decrypt.py <encrypted_filename> <key>")
        sys.exit(1)

    encrypted_filename = sys.argv[1]
    key = (sys.argv[2]).encode('utf-8')
    decrypt_file(encrypted_filename, key)