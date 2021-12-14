#!/usr/bin/env python

"""
Columbia's COMS W4156 Advanced Software Engineering
Client

To run locally:

    python server.py

Go to http://localhost:8111 in your browser.
"""

import os
import requests
import json
from flask import Flask, request, abort
from flask import render_template, redirect, flash, session
from pip._vendor import cachecontrol

import google
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow

from datetime import timedelta
import pathlib

MATRIX_SERVICE_API = 'http://0.0.0.0:5001'

CREATE_API_ENDPOINT = '/create'
RETRIEVE_API_ENDPOINT = '/retrieve'
UPDATE_API_ENDPOINT = '/update'
DELETE_API_ENDPOINT = '/delete'
GENERATE_API_ENDPOINT = '/generate'
STRENGTH_API_ENDPOINT = '/strength'

OAUTH_TIMEOUT = 10
tmpl_dir = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)
app.secret_key = 'matrix-client'

file = open("keys.txt", "r")
keys = file.read().splitlines()
file.close()

app.config['SESSION_COOKIE_NAME'] = 'google-login-session'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=OAUTH_TIMEOUT)
GOOGLE_CLIENT_ID = keys[1]
client_secrets_file = os.path.join(
    pathlib.Path(__file__).parent, "client_secret.json")
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile",
            "https://www.googleapis.com/auth/userinfo.email",
            "openid"],
    redirect_uri="http://127.0.0.1:5000/authorize"
)


def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return redirect('/')
        else:
            return function()
    wrapper.__name__ = function.__name__
    return wrapper


@app.route('/')
def index():
    if "google_id" in session:
        return redirect('/generate')
    return "<H1>Welcome to Password Manager, " \
           "hit login to continue! </H1> <br>" \
           "<a href='/login'><button>Login</button></a>"


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
    token_request = google.auth.transport.requests.Request(
        session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )

    session["google_id"] = id_info.get("sub")
    session["name"] = id_info.get("name")
    session['email'] = id_info.get("email")

    return redirect("/generate")


@app.route('/generate', methods=['GET', 'POST'])
@login_is_required
def password_gen():
    if request.method == 'POST':
        caps_bool = request.form.get('caps', '')
        spchar_bool = request.form.get('spchar', '')
        num_bool = request.form.get('num', '')

        query_params = dict()
        query_params['num'] = 'true' if num_bool else 'false'
        query_params['spchar'] = 'true' if spchar_bool else 'false'
        query_params['caps'] = 'true' if caps_bool else 'false'

        response = requests.get(MATRIX_SERVICE_API + GENERATE_API_ENDPOINT,
                                params=query_params,
                                json={'user_email': session['email']})

        generated_password = json.loads(response.text)['data']
        flash(f"Generated Password: {generated_password}")

    return render_template("generator.html", user=session['name'])


@app.route('/create', methods=['GET', 'POST'])
@login_is_required
def create_password():
    if request.method == 'POST':
        payload = dict()
        payload['password'] = request.form['password']
        if 'pass_strength' in request.form:
            response = requests.get(MATRIX_SERVICE_API +
                                    STRENGTH_API_ENDPOINT,
                                    params=payload,
                                    json={'user_email': session['email']})
            result = json.loads(response.text)['data']
            if response.status_code != 200:
                flash(f"{result}")
            else:
                flash(f"Password {result['password']} "
                      f"is of {result['label']} strength."
                      f" It will take {result['estimated_guesses']}"
                      f" guesses to crack it.")
            return render_template("create.html", user=session['name'])

        payload['application'] = request.form['application']
        response = requests.post(MATRIX_SERVICE_API +
                                 CREATE_API_ENDPOINT,
                                 params=payload,
                                 json={'user_email': session['email']})
        message = json.loads(response.text)['data']
        if message:
            flash(message)

    return render_template("create.html", user=session['name'])


@app.route('/retrieve', methods=['GET', 'POST'])
@login_is_required
def retrieve_password():
    app_list = []
    if request.method == 'POST':
        payload = dict()

        if 'ret_pass_all' in request.form:
            payload['application'] = 'all'

            response = requests.get(MATRIX_SERVICE_API +
                                    RETRIEVE_API_ENDPOINT,
                                    params=payload,
                                    json={'user_email': session['email']})
            results = json.loads(response.text)['data']

            for app, passwd in results.items():
                app_list.append((app, passwd))
        else:
            if 'application' not in request.form:
                flash("No app selected for retrieving password.")
            else:
                payload['application'] = request.form['application']
                response = requests.get(MATRIX_SERVICE_API +
                                        RETRIEVE_API_ENDPOINT,
                                        params=payload,
                                        json={'user_email': session['email']})

                result = json.loads(response.text)['data']
                if response.status_code != 200:
                    flash(f"{result}")
                else:
                    for key in result:
                        message = f"Password for application" \
                                  f" {key}: {result[key]}"
                        flash(message)

    response = requests.get(MATRIX_SERVICE_API + RETRIEVE_API_ENDPOINT,
                            params={'application': 'all'},
                            json={'user_email': session['email']})

    results = json.loads(response.text)['data']
    data = [key for key in results]

    if len(app_list) == 0:
        app_list.append(-1)

    return render_template("retrieve.html", data=data,
                           app_list=app_list, user=session['name'])


@app.route('/delete', methods=['GET', 'POST'])
@login_is_required
def delete_password():

    if request.method == 'POST':
        payload = dict()
        if 'application' not in request.form:
            flash("No app selected for deleting password.")
        else:
            payload['application'] = request.form['application']

            response = requests.delete(MATRIX_SERVICE_API +
                                       DELETE_API_ENDPOINT,
                                       params=payload,
                                       json={'user_email': session['email']})
            message = json.loads(response.text)['data']
            if message:
                flash(message)

    response = requests.get(MATRIX_SERVICE_API +
                            RETRIEVE_API_ENDPOINT,
                            params={'application': 'all'},
                            json={'user_email': session['email']})
    results = json.loads(response.text)['data']
    data = [key for key in results]

    return render_template("delete.html", data=data, user=session['name'])


@app.route('/update', methods=['GET', 'POST'])
@login_is_required
def update_password():

    if request.method == 'POST':
        payload = dict()

        if 'application' not in request.form:
            flash("No app selected for updating password.")
        else:
            payload['application'] = request.form['application']
            payload['password'] = request.form['password']
            response = requests.post(MATRIX_SERVICE_API +
                                     UPDATE_API_ENDPOINT,
                                     params=payload,
                                     json={'user_email': session['email']})
            message = json.loads(response.text)['data']
            if message:
                flash(message)

    response = requests.get(MATRIX_SERVICE_API +
                            RETRIEVE_API_ENDPOINT,
                            params={'application': 'all'},
                            json={'user_email': session['email']})
    results = json.loads(response.text)['data']
    data = [key for key in results]

    return render_template("update.html", data=data, user=session['name'])


@app.route('/logout')
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    import click

    @click.command()
    @click.option('--debug', is_flag=True)
    @click.option('--threaded', is_flag=True)
    @click.argument('HOST', default='127.0.0.1')
    @click.argument('PORT', default=5000, type=int)
    def run(debug, threaded, host, port):
        """
    This function handles command line parameters.
    Run the server using:

        python server.py

    Show the help text using:

        python server.py --help

    """

        HOST, PORT = host, port
        print("running on %s:%d" % (HOST, PORT))
        app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

    run()
