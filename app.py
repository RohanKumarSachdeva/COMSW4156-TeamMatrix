from flask import Flask, Response, request
from flask_cors import CORS
import json
import logging

from EncryptionServices.cipher import Cipher

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

app = Flask(__name__)
CORS(app)
crypt = Cipher()


@app.route('/')
def hello_world():
    return '<u>Welcome to Crypt Microservice!</u>'


# expected string format
# api/encrypt?application=Coursework&password=pas2345
@app.route("/api/encrypt")
def encrypt():
    # get the value of query parameters (i.e. ?origins=some-value)
    app_name = request.args.get('application')
    password = request.args.get('password')
    req = crypt.get_by_template(app_name, password)
    resp = Response(json.dumps(req, default=str), status=200, content_type="application/json")
    return resp


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001)
