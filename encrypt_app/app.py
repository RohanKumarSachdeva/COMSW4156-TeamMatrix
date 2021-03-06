from flask import Flask, request, Response
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
import logging
import db
import os
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

api_data_type = 'application/json'
error_invalid_app_name = 'Invalid application name.'
error_pass_len_short = 'Password length should be atleast 8.'
error_pass_len_long = 'Password length should not be more than 15.'

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
    app.db = os.environ.get('DB_NAME', 'prod_sqlite_db')
    db.init_db(app.db)
    return app


def clear_app(dbname):
    db.clear(dbname)


@app.route('/')
def hello_world():
    return '<u>Welcome to Matrix Microservice!</u>'


@app.route('/create', methods=['POST'])
def create():
    app_name = request.args.get('application')
    password = request.args.get('password')
    password = parse.unquote(password)

    if not app_name or app_name == 'all':
        message = error_invalid_app_name
        return Response(json.dumps({'data': message}),
                        status=BAD_REQUEST_STATUS_CODE,
                        mimetype=api_data_type)

    if not password or len(password) < 8:
        message = error_pass_len_short
        return Response(json.dumps({'data': message}),
                        status=BAD_REQUEST_STATUS_CODE,
                        mimetype=api_data_type)

    if len(password) > 15:
        message = error_pass_len_long
        return Response(json.dumps({'data': message}),
                        status=BAD_REQUEST_STATUS_CODE,
                        mimetype=api_data_type)

    if '"' in password or "\\" in password:
        message = 'Password must not contain \\ or "'
        return Response(json.dumps({'data': message}),
                        status=BAD_REQUEST_STATUS_CODE,
                        mimetype=api_data_type)

    user_id = request.json['user_email']
    result = db.get_record(app.db, user_id, app_name)
    if not result:
        cipher = Cipher()
        encrypt_pw, encryption_key = cipher.encipher(password)
        db.add_record(app.db, (user_id, app_name, encrypt_pw, encryption_key))

        message = 'Password saved successfully!'
        return Response(json.dumps({'data': message}),
                        status=SUCCESS_STATUS_CODE,
                        mimetype=api_data_type)
    else:
        message = 'A password for this application exists already.' \
                  'Please use /update endpoint.'
        return Response(json.dumps({'data': message}),
                        status=BAD_REQUEST_STATUS_CODE,
                        mimetype=api_data_type)


@app.route('/retrieve', methods=['GET'])
def retrieve():
    app_name = request.args.get('application')
    if not app_name:
        message = error_invalid_app_name
        return Response(json.dumps({'data': message}),
                        status=BAD_REQUEST_STATUS_CODE,
                        mimetype=api_data_type)

    user_id = request.json['user_email']

    result = db.get_record(app.db, user_id, app_name)
    passwords = {}
    for row in result:
        cipher = Cipher(key=row[2])
        plain_password = cipher.decipher(row[1])
        passwords[row[0]] = plain_password
    message = passwords
    return Response(json.dumps({'data': message}),
                    status=SUCCESS_STATUS_CODE,
                    mimetype=api_data_type)


@app.route('/update', methods=['POST'])
def update():
    app_name = request.args.get('application')
    password = request.args.get('password')
    password = parse.unquote(password)

    if not app_name or app_name == 'all':
        message = error_invalid_app_name
        return Response(json.dumps({'data': message}),
                        status=BAD_REQUEST_STATUS_CODE,
                        mimetype=api_data_type)

    if not password or len(password) < 8:
        message = error_pass_len_short
        return Response(json.dumps({'data': message}),
                        status=BAD_REQUEST_STATUS_CODE,
                        mimetype=api_data_type)

    if len(password) > 15:
        message = error_pass_len_long
        return Response(json.dumps({'data': message}),
                        status=BAD_REQUEST_STATUS_CODE,
                        mimetype=api_data_type)

    if '"' in password or "\\" in password:
        message = 'Password must not contain \\ or "'
        return Response(json.dumps({'data': message}),
                        status=BAD_REQUEST_STATUS_CODE,
                        mimetype=api_data_type)

    user_id = request.json['user_email']
    result = db.get_record(app.db, user_id, app_name)

    if result:
        cipher = Cipher()
        encrypt_pw, encryption_key = cipher.encipher(password)
        db.update_record(app.db,
                         (user_id, app_name,
                          encrypt_pw, encryption_key))

        message = 'Password updated successfully!'
        return Response(json.dumps({'data': message}),
                        status=SUCCESS_STATUS_CODE,
                        mimetype=api_data_type)
    else:
        message = 'No such application exists. Please use /create endpoint.'
        return Response(json.dumps({'data': message}),
                        status=NOT_FOUND_STATUS_CODE,
                        mimetype=api_data_type)


@app.route('/delete', methods=['DELETE'])
def delete():
    app_name = request.args.get('application')
    if not app_name:
        message = error_invalid_app_name
        return Response(json.dumps({'data': message}),
                        status=BAD_REQUEST_STATUS_CODE,
                        mimetype=api_data_type)

    user_id = request.json['user_email']
    result = db.get_record(app.db, user_id, app_name)
    if not result:
        message = f'Application {app_name} does not exist in the database.'
        return Response(json.dumps({'data': message}),
                        status=NOT_FOUND_STATUS_CODE,
                        mimetype=api_data_type)

    db.delete_record(app.db, user_id, app_name)
    message = f'Deleted passwords for {app_name} application(s).'
    return Response(json.dumps({'data': message}),
                    status=SUCCESS_STATUS_CODE,
                    mimetype=api_data_type)


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
                        mimetype=api_data_type)

    length = int(length)
    if length < 8:
        message = error_pass_len_short
        return Response(json.dumps({'data': message}),
                        status=BAD_REQUEST_STATUS_CODE,
                        mimetype=api_data_type)

    if length > 15:
        message = error_pass_len_long
        return Response(json.dumps({'data': message}),
                        status=BAD_REQUEST_STATUS_CODE,
                        mimetype=api_data_type)

    for query_param in [num, spchar, caps]:
        if query_param.lower() not in ['true', 'false']:
            message = '/generate endpoint only accepts true' \
                      ' or false values for query string params.'
            return Response(json.dumps({'data': message}),
                            status=BAD_REQUEST_STATUS_CODE,
                            mimetype=api_data_type)

    num = True if num.lower() == 'true' else False
    spchar = True if spchar.lower() == 'true' else False
    caps = True if caps.lower() == 'true' else False

    passcode = password_gen(length, num, spchar, caps)
    print(passcode)
    return Response(json.dumps({'data': passcode}),
                    status=SUCCESS_STATUS_CODE,
                    mimetype=api_data_type)


@app.route('/strength', methods=['GET'])
def strength():
    password = request.args.get('password')
    password = parse.unquote(password)

    if not password:
        message = 'Password cannot be empty.'
        return Response(json.dumps({'data': message}),
                        status=BAD_REQUEST_STATUS_CODE,
                        mimetype=api_data_type)

    message = strength_checker(password)
    return Response(json.dumps({'data': message}),
                    status=SUCCESS_STATUS_CODE,
                    mimetype=api_data_type)


if __name__ == '__main__':
    app.db = os.environ.get('DB_NAME', 'prod_sqlite_db')
    db.init_db(app.db)
    app.run(host="0.0.0.0", port=5001, debug=True)
