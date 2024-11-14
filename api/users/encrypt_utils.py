import os

from cryptography.fernet import Fernet

# def generate_key():
#     return Fernet.generate_key()


KEY = os.environ.get("ENCRYPTION_KEY")
fernet = Fernet(KEY.encode("utf-8"))


def encrypt(data):
    try:
        return fernet.encrypt(data.encode("utf-8")).decode("utf-8")
    except Exception as e:
        raise ValueError(f"Encryption failed: {str(e)}")


def decrypt(encrypted_data):
    try:
        return fernet.decrypt(encrypted_data.encode("utf-8")).decode("utf-8")
    except Exception as e:
        raise ValueError(f"Decryption failed: {str(e)}")
