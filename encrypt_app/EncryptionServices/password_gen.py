import requests


def password_gen(length=12, num=True, spchar=True, caps=True):
    """
    Uses external API to generate password
    :param length: password length
    :param num: boolean to allow numbers in password
    :param spchar: boolean to allow special chars in password
    :param caps: boolean to allow uppercase letters in password
    :return:
    """
    params = {'len': length}
    if num:
        params['num'] = True
    if spchar:
        params['char'] = True
    if caps:
        params['caps'] = True

    response = requests.get("https://passwordinator.herokuapp.com/generate",
                            params=params)
    password = response.json()['data']
    return password
