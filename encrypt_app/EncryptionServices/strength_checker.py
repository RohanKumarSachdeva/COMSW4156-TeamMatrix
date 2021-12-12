import json
import requests


def strength_checker(password):
    """
    Checks strength of the given password and
    returns score, verdict and number of guesses.
    :param password:
    :return:
    """
    url = "https://password-utils.p.rapidapi.com/password/check/"
    data = {"password": password}
    payload = json.dumps(data)
    headers = {
        'content-type': "application/json",
        'x-rapidapi-host': "password-utils.p.rapidapi.com",
        'x-rapidapi-key': "afd78c5abcmsh505035d57d05aa1p1529dajsn642939b5585e"
    }

    response = requests.request("POST", url, data=payload, headers=headers)

    return response.json()
