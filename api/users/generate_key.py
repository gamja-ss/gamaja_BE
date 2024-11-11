from cryptography.fernet import Fernet


def generate_key():
    return Fernet.generate_key()


if __name__ == "__main__":
    key = generate_key()
    print(key.decode())
