from flask import Flask, request
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
import logging
import db

from EncryptionServices.password_gen import password_gen
from EncryptionServices.cipher import Cipher

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

app = Flask(__name__)
CORS(app)

# Swagger config
SWAGGER_URL = '/swagger'
API_URL = '/static/api-spec.json'
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Password Manager"
    }
)
app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)


def get_app():
    db.init_db()
    return app


def clear_app():
    db.clear()


@app.route('/')
def hello_world():
    return '<u>Welcome to Crypt Microservice!</u>'


@app.route('/create', methods=['POST'])
def create():
    app_name = request.args.get('application')
    password = request.args.get('password')

    if app_name == 'all':
        return {
            'message': 'Invalid application name.'
        }

    user_id = 'abc@gmail.com'
    result = db.get_record(user_id, app_name)
    if not result:
        cipher = Cipher()
        encrypt_pw, encryption_key = cipher.encipher(password)
        db.add_record((user_id, app_name, encrypt_pw, encryption_key))

        return {
            'message': 'Password created successfully!'
        }
    else:
        return {
            'message': 'A password for this application exists already.'
                       'Please use /update endpoint.'
        }


@app.route('/retrieve', methods=['GET'])
def retrieve():
    app_name = request.args.get('application')
    user_id = 'abc@gmail.com'
    result = db.get_record(user_id, app_name)
    passwords = {}
    for row in result:
        cipher = Cipher(key=row[2])
        plain_password = cipher.decipher(row[1])
        passwords[row[0]] = plain_password
    return {
        'message': passwords
    }


@app.route('/update', methods=['POST'])
def update():
    app_name = request.args.get('application')
    password = request.args.get('password')
    if app_name == 'all':
        return {
            'message': 'Invalid application name.'
        }

    user_id = 'abc@gmail.com'
    result = db.get_record(user_id, app_name)

    if result:
        cipher = Cipher()
        encrypt_pw, encryption_key = cipher.encipher(password)
        db.update_record((user_id, app_name, encrypt_pw, encryption_key))

        return {
            'message': 'Password updated successfully!'
        }
    else:
        return {
            'message': 'No such application exists.'
                       'Please use /create endpoint.'
        }


@app.route('/delete', methods=['DELETE'])
def delete():
    app_name = request.args.get('application')
    user_id = 'abc@gmail.com'
    db.delete_record(user_id, app_name)
    return {
        'message': f'Deleted passwords for {app_name} application(s).'
    }


@app.route('/generate', methods=['GET'])
def generate():
    num = request.args.get('num', 'true')
    length = request.args.get('len', '12')
    spchar = request.args.get('spchar', 'true')
    caps = request.args.get('caps', 'true')

    if not length.isdigit():
        return {
                'message': 'num query param is invalid'
            }

    length = int(length)
    if int(length) < 8:
        return {
            'message': 'password length should be atleast 8'
        }
    for query_param in [num, spchar, caps]:
        if query_param.lower() not in ['true', 'false']:
            return {
                'message': '/generate endpoint only accepts true '
                           'or false values for query string params.'
            }

    num = True if num.lower() == 'true' else False
    spchar = True if spchar.lower() == 'true' else False
    caps = True if caps.lower() == 'true' else False
    print("Input received:", num, spchar, caps)
    return {'message': password_gen(length, num, spchar, caps)}


if __name__ == '__main__':
    db.init_db()
    app.run(host="0.0.0.0", port=5001, debug=True)
