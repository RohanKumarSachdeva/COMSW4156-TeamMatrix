import requests

def password_gen():
    params = {"num": True, "char":True, "caps":True, "len":15}
    response = requests.get("https://passwordinator.herokuapp.com/generate", params=params)
    password = response.json()
    print(password)

    return password

