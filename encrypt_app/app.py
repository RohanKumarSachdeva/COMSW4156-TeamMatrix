from flask import Flask, request, redirect, url_for, session, abort
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
import logging
import db
import os
import pathlib
import requests
import google
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
from datetime import timedelta
from EncryptionServices.password_gen import password_gen
from EncryptionServices.cipher import Cipher

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()
logger.setLevel(logging.INFO)
file = open("keys.txt", "r")
keys = file.read().splitlines()
file.close()

app = Flask(__name__)
app.secret_key = keys[0]
app.config['SESSION_COOKIE_NAME'] = 'google-login-session'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=2)
GOOGLE_CLIENT_ID = keys[1]
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secret.json")
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
CORS(app)

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email",
            "openid"],
    redirect_uri="http://127.0.0.1:5000/authorize"
)

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


def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return abort(401)  # Authorization required
        else:
            return function()
    wrapper.__name__ = function.__name__
    return wrapper


def get_app():
    db.init_db()
    return app


def clear_app():
    db.clear()


@app.route('/')
def hello_world():
    return "Welcome to Password Manager, hit login to continue! <a href='/login'><button>Login</button></a>"


@app.route('/login')
def login():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)


@app.route('/authorize')
def authorize():
    flow.fetch_token(authorization_response=request.url)

    if not session["state"] == request.args["state"]:
        abort(500)  # State does not match!

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )

    session["google_id"] = id_info.get("sub")
    session["name"] = id_info.get("name")
    session['email'] = id_info.get("email")
    # print(session)
    return redirect("/welcome")


@app.route('/create', methods=['POST'])
@login_is_required
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
@login_is_required
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
@login_is_required
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
@login_is_required
def delete():
    app_name = request.args.get('application')
    user_id = 'abc@gmail.com'
    db.delete_record(user_id, app_name)
    return {
        'message': f'Deleted passwords for {app_name} application(s).'
    }


@app.route('/generate', methods=['GET'])
@login_is_required
def generate():
    return {'message': password_gen()}


@app.route('/welcome')
@login_is_required
def welcome():

    return f"Welcome {session['name']} you are logged in with email {session['email']}. " \
           f"You can now Create, Retrieve, Update and Delete passwords" \
           f" <a href='/logout'><button>Logout</button></a>"


@app.route('/logout')
def logout():
    session.clear()
    return redirect("/")


if __name__ == '__main__':
    db.init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
