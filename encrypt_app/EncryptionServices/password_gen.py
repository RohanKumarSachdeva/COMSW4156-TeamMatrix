import requests


def password_gen(length=12):
    """
    Uses external API to generate password
    :param length:
    :return:
    """
    params = {"num": True, "char": True, "caps": True, "len": length}
    response = requests.get("https://passwordinator.herokuapp.com/generate",
                            params=params)
    password = response.json()['data']
    return password
