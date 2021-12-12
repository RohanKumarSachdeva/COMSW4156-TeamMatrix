from flask import Flask, request, Response
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
import logging
import db
import json
from urllib import parse

from EncryptionServices.password_gen import password_gen
from EncryptionServices.strength_checker import strength_checker
from EncryptionServices.cipher import Cipher

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

app = Flask(__name__)
CORS(app)

SUCCESS_STATUS_CODE = 200
BAD_REQUEST_STATUS_CODE = 400
NOT_FOUND_STATUS_CODE = 404

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
    return '<u>Welcome to Matrix Microservice!</u>'


@app.route('/create', methods=['POST'])
def create():
    app_name = request.args.get('application')
    password = request.args.get('password')
    password = parse.unquote(password)

    if not app_name or app_name == 'all':
        message = 'Invalid application name.'
        return Response(json.dumps({'data': message}),
                        status=BAD_REQUEST_STATUS_CODE,
                        mimetype='application/json')

    if not password or len(password) < 8:
        message = 'Password length should be atleast 8.'
        return Response(json.dumps({'data': message}),
                        status=BAD_REQUEST_STATUS_CODE,
                        mimetype='application/json')

    if len(password) > 15:
        message = 'Password length should not be more than 15.'
        return Response(json.dumps({'data': message}),
                        status=BAD_REQUEST_STATUS_CODE,
                        mimetype='application/json')

    if '"' in password or "\\" in password:
        message = 'Password must not contain \\ or "'
        return Response(json.dumps({'data': message}),
                        status=BAD_REQUEST_STATUS_CODE,
                        mimetype='application/json')

    user_id = 'abc@gmail.com'
    result = db.get_record(user_id, app_name)
    if not result:
        cipher = Cipher()
        encrypt_pw, encryption_key = cipher.encipher(password)
        db.add_record((user_id, app_name, encrypt_pw, encryption_key))

        message = 'Password created successfully!'
        return Response(json.dumps({'data': message}),
                        status=SUCCESS_STATUS_CODE,
                        mimetype='application/json')
    else:
        message = 'A password for this application exists already. Please use /update endpoint.'
        return Response(json.dumps({'data': message}),
                        status=BAD_REQUEST_STATUS_CODE,
                        mimetype='application/json')


@app.route('/retrieve', methods=['GET'])
def retrieve():
    app_name = request.args.get('application')
    if not app_name:
        message = 'Invalid application name.'
        return Response(json.dumps({'data': message}),
                        status=BAD_REQUEST_STATUS_CODE,
                        mimetype='application/json')

    user_id = 'abc@gmail.com'
    result = db.get_record(user_id, app_name)
    passwords = {}
    for row in result:
        cipher = Cipher(key=row[2])
        plain_password = cipher.decipher(row[1])
        passwords[row[0]] = plain_password
    message = passwords
    return Response(json.dumps({'data': message}),
                    status=SUCCESS_STATUS_CODE,
                    mimetype='application/json')


@app.route('/update', methods=['POST'])
def update():
    app_name = request.args.get('application')
    password = request.args.get('password')
    password = parse.unquote(password)

    if not app_name or app_name == 'all':
        message = 'Invalid application name.'
        return Response(json.dumps({'data': message}),
                        status=BAD_REQUEST_STATUS_CODE,
                        mimetype='application/json')

    if not password or len(password) < 8:
        message = 'Password length should be atleast 8.'
        return Response(json.dumps({'data': message}),
                        status=BAD_REQUEST_STATUS_CODE,
                        mimetype='application/json')

    if len(password) > 15:
        message = 'Password length should not be more than 15.'
        return Response(json.dumps({'data': message}),
                        status=BAD_REQUEST_STATUS_CODE,
                        mimetype='application/json')

    if '"' in password or "\\" in password:
        message = 'Password must not contain \\ or "'
        return Response(json.dumps({'data': message}),
                        status=BAD_REQUEST_STATUS_CODE,
                        mimetype='application/json')

    user_id = 'abc@gmail.com'
    result = db.get_record(user_id, app_name)

    if result:
        cipher = Cipher()
        encrypt_pw, encryption_key = cipher.encipher(password)
        db.update_record((user_id, app_name, encrypt_pw, encryption_key))

        message = 'Password updated successfully!'
        return Response(json.dumps({'data': message}),
                        status=SUCCESS_STATUS_CODE,
                        mimetype='application/json')
    else:
        message = 'No such application exists. Please use /create endpoint.'
        return Response(json.dumps({'data': message}),
                        status=NOT_FOUND_STATUS_CODE,
                        mimetype='application/json')


@app.route('/delete', methods=['DELETE'])
def delete():
    user_id = 'abc@gmail.com'
    app_name = request.args.get('application')
    if not app_name:
        message = 'Invalid application name.'
        return Response(json.dumps({'data': message}),
                        status=BAD_REQUEST_STATUS_CODE,
                        mimetype='application/json')

    result = db.get_record(user_id, app_name)
    if not result:
        message = f'Application {app_name} does not exist in the database.'
        return Response(json.dumps({'data': message}),
                        status=NOT_FOUND_STATUS_CODE,
                        mimetype='application/json')

    db.delete_record(user_id, app_name)
    message = f'Deleted passwords for {app_name} application(s).'
    return Response(json.dumps({'data': message}),
                    status=SUCCESS_STATUS_CODE,
                    mimetype='application/json')


@app.route('/generate', methods=['GET'])
def generate():
    num = request.args.get('num', 'true')
    length = request.args.get('len', '12')
    spchar = request.args.get('spchar', 'true')
    caps = request.args.get('caps', 'true')

    if not length.isdigit():
        message = 'num query param is invalid.'
        return Response(json.dumps({'data': message}),
                        status=BAD_REQUEST_STATUS_CODE,
                        mimetype='application/json')

    length = int(length)
    if length < 8:
        message = 'Password length should be atleast 8.'
        return Response(json.dumps({'data': message}),
                        status=BAD_REQUEST_STATUS_CODE,
                        mimetype='application/json')

    if length > 15:
        message = 'Password length should not be more than 15.'
        return Response(json.dumps({'data': message}),
                        status=BAD_REQUEST_STATUS_CODE,
                        mimetype='application/json')

    for query_param in [num, spchar, caps]:
        if query_param.lower() not in ['true', 'false']:
            message = '/generate endpoint only accepts true' \
                      ' or false values for query string params.'
            return Response(json.dumps({'data': message}),
                            status=BAD_REQUEST_STATUS_CODE,
                            mimetype='application/json')

    num = True if num.lower() == 'true' else False
    spchar = True if spchar.lower() == 'true' else False
    caps = True if caps.lower() == 'true' else False

    passcode = password_gen(length, num, spchar, caps)
    print(passcode)
    return Response(json.dumps({'data': passcode}),
                    status=SUCCESS_STATUS_CODE,
                    mimetype='application/json')


@app.route('/strength', methods=['GET'])
def strength():
    password = request.args.get('password')
    password = parse.unquote(password)

    if not password:
        message = 'Password cannot be empty.'
        return Response(json.dumps({'data': message}),
                        status=BAD_REQUEST_STATUS_CODE,
                        mimetype='application/json')

    message = strength_checker(password)
    return Response(json.dumps({'data': message}),
                    status=SUCCESS_STATUS_CODE,
                    mimetype='application/json')


if __name__ == '__main__':
    db.init_db()
    app.run(host="0.0.0.0", port=5001, debug=True)
