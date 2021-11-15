from cryptography.fernet import Fernet


class Cipher:
    def __init__(self):
        self.key = Fernet.generate_key()
        self.crypt = Fernet(self.key)

    def encipher(self, password):
        """
        Encrypts the provided password
        :param password:
        :return:
        """
        e_password = self.crypt.encrypt(bytes(password, 'utf-8'))
        print(f"Encrypted password: {str(e_password, 'utf8')}")
        return e_password

    def decipher(self, e_password):
        """
        Decrypts an encrypted password
        :param e_password:
        :return:
        """
        d_password = self.crypt.decrypt(e_password)
        print(f"Decrypted password: {str(d_password, 'utf8')}")

