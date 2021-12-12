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
from flask import Flask, request, render_template, g, redirect, Response, flash

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)
app.secret_key = 'matrix-client'

MATRIX_PASSWORD_MANAGEMENT_API = 'http://0.0.0.0:5001'
@app.route('/')
def index():
    return render_template("generator.html")


@app.route('/generate', methods=['POST'])
def password_gen():
    caps_bool = request.form.get('caps', '')
    spchar_bool = request.form.get('spchar', '')
    num_bool = request.form.get('num', '')

    query_params = dict()
    if num_bool:
        query_params['num'] = 'true'
    if spchar_bool:
        query_params['char'] = 'true'
    if caps_bool:
        query_params['caps'] = 'true'

    response = requests.get(MATRIX_PASSWORD_MANAGEMENT_API+'/generate',
                            params=query_params)

    generated_password = json.loads(response.text)['data']
    flash(f"Generated Password: {generated_password}")
    return render_template("generator.html")


@app.route('/create', methods=['GET', 'POST'])
def create_password():
    if request.method == 'POST':
        payload = dict()
        payload['password'] = request.form['password']
        if 'pass_strength' in request.form:
            response = requests.get(MATRIX_PASSWORD_MANAGEMENT_API + '/strength',
                                     params=payload)
            result = json.loads(response.text)['data']
            flash(f"Password {result['password']} is of {result['label']} strength."
                  f" It will take {result['estimated_guesses']} guesses to crack it.")
            return render_template("create.html")

        payload['application'] = request.form['application']
        response = requests.post(MATRIX_PASSWORD_MANAGEMENT_API + '/create',
                                   params=payload)
        message = json.loads(response.text)['data']
        if message:
            flash(message)

    return render_template("create.html")


@app.route('/retrieve', methods=['GET', 'POST'])
def retrieve_password():
    app_list = []
    if request.method == 'POST':
        payload = dict()
        if 'ret_pass_all' in request.form:
            payload['application'] = 'all'

            response = requests.get(MATRIX_PASSWORD_MANAGEMENT_API + '/retrieve',
                                    params=payload)
            results = json.loads(response.text)['data']

            for app, passwd in results.items():
                app_list.append((app, passwd))
        else:
            payload['application'] = request.form['application']
            response = requests.get(MATRIX_PASSWORD_MANAGEMENT_API + '/retrieve',
                                    params=payload)

            result = json.loads(response.text)['data']
            for key in result:
                message = f"Password for application {key}: {result[key]}"
                flash(message)

    response = requests.get(MATRIX_PASSWORD_MANAGEMENT_API + '/retrieve',
                            params={'application': 'all'})

    results = json.loads(response.text)['data']
    data = [key for key in results]

    if len(app_list) == 0:
        app_list.append(-1)

    return render_template("retrieve.html", data=data, app_list=app_list)


@app.route('/delete', methods=['GET', 'POST'])
def delete_password():

    if request.method == 'POST':
        payload = dict()
        payload['application'] = request.form['application']

        response = requests.delete(MATRIX_PASSWORD_MANAGEMENT_API + '/delete',
                                   params=payload)
        message = json.loads(response.text)['data']
        if message:
            flash(message)

    response = requests.get(MATRIX_PASSWORD_MANAGEMENT_API + '/retrieve',
                            params={'application': 'all'})
    results = json.loads(response.text)['data']
    data = [key for key in results]

    return render_template("delete.html", data=data)


@app.route('/update', methods=['GET', 'POST'])
def update_password():

    if request.method == 'POST':
        payload = dict()
        payload['password'] = request.form['password']
        payload['application'] = request.form['application']
        response = requests.post(MATRIX_PASSWORD_MANAGEMENT_API + '/update',
                                 params=payload)
        message = json.loads(response.text)['data']
        if message:
            flash(message)

    response = requests.get(MATRIX_PASSWORD_MANAGEMENT_API + '/retrieve',
                            params={'application': 'all'})
    results = json.loads(response.text)['data']
    data = [key for key in results]

    return render_template("update.html", data=data)


if __name__ == "__main__":
    import click


    @click.command()
    @click.option('--debug', is_flag=True)
    @click.option('--threaded', is_flag=True)
    @click.argument('HOST', default='0.0.0.0')
    @click.argument('PORT', default=8112, type=int)
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
