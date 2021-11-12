from cryptography.fernet import Fernet


class Cipher:
    def __init__(self):
        self.key = Fernet.generate_key()
        self.crypt = Fernet(self.key)

    def encipher(self, app_name, password):
        e_password = self.crypt.encrypt(bytes(password, 'utf-8'))
        print(f"Encrypted password for application {app_name} is {str(e_password, 'utf8')}")
        self.decipher(app_name, e_password)
        return e_password

    def decipher(self, app_name, e_password):
        d_password = self.crypt.decrypt(e_password)
        print(f"Decrypted password for application {app_name} is {str(d_password,'utf8')}")

    def get_by_template(self, app_name, password):
        return self.encipher(app_name, password)
