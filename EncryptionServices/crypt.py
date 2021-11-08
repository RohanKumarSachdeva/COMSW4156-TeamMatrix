from cryptography.fernet import Fernet

key = Fernet.generate_key()
crypt = Fernet(key)
e_password = crypt.encrypt(b'password123')
d_password = crypt.decrypt(e_password)
print(key)
print(e_password)
print(str(e_password, 'utf8'))
print(d_password)

