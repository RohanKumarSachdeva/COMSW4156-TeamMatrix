from flask import Flask, Response, request
from flask_restful import Resource, Api
from flask_cors import CORS

from flask_apispec import marshal_with, doc, use_kwargs
from flask_apispec.views import MethodResource
from flask_apispec.extension import FlaskApiSpec

from apispec.ext.marshmallow import MarshmallowPlugin
from apispec import APISpec

from marshmallow import Schema, fields
from webargs.flaskparser import parser, abort

import json
import logging
import db

from EncryptionServices.password_gen import password_gen
from EncryptionServices.cipher import Cipher

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

app = Flask(__name__)
api = Api(app)
CORS(app)


class EncryptResponseSchema(Schema):
    message = fields.Str(default='')


class EncryptRequestSchema(Schema):
    application = fields.String(required=True, description="Application Name")
    password = fields.String(required=True, description="Plaintext Password")


class DecryptRequestSchema(Schema):
    application = fields.String(required=True, description="Application Name")


@doc(description='Encryption endpoint.', tags=['password manager'])
@use_kwargs(EncryptRequestSchema, location='query')
@marshal_with(EncryptResponseSchema)  # marshalling
class CreateAPI(MethodResource, Resource):
    def post(self, **kwargs):
        app_name = kwargs['application']
        password = kwargs['password']

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
                'message': 'A password for this application exists already. Please use /update endpoint.'
            }


@doc(description='Decryption endpoint.', tags=['password manager'])
@use_kwargs(DecryptRequestSchema, location='query')
@marshal_with(EncryptResponseSchema)  # marshalling
class RetrieveAPI(MethodResource, Resource):
    def get(self, **kwargs):
        app_name = kwargs['application']

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


@doc(description='Password update endpoint.', tags=['password manager'])
@use_kwargs(EncryptRequestSchema, location='query')
@marshal_with(EncryptResponseSchema)  # marshalling
class UpdateAPI(MethodResource, Resource):
    def post(self, **kwargs):
        app_name = kwargs['application']
        password = kwargs['password']

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
                'message': 'No such application exists. Please use /create endpoint.'
            }


@doc(description='Password delete endpoint.', tags=['password manager'])
@use_kwargs(DecryptRequestSchema, location='query')
@marshal_with(EncryptResponseSchema)  # marshalling
class DeleteAPI(MethodResource, Resource):
    def delete(self, **kwargs):
        app_name = kwargs['application']
        user_id = 'abc@gmail.com'

        db.delete_record(user_id, app_name)
        return {
            'message': f'Deleted passwords for {app_name} application(s).'
        }


@app.route('/')
def hello_world():
    return '<u>Welcome to Crypt Microservice!</u>'


@parser.error_handler
def handle_request_parsing_error(err, req, schema, *, error_status_code, error_headers):
    """webargs error handler that uses Flask-RESTful's abort function to return
    a JSON error response to the client.
    """
    abort(error_status_code, errors=err.messages)


app.config.update({
    'APISPEC_SPEC': APISpec(
        title='ASE Project',
        version='v1',
        plugins=[MarshmallowPlugin()],
        openapi_version='2.0.0'
    ),
    'APISPEC_SWAGGER_URL': '/swagger/',  # URI to access API Doc JSON
    'APISPEC_SWAGGER_UI_URL': '/swagger-ui/'  # URI to access UI of API Doc
})

docs = FlaskApiSpec(app)


@doc(description='Generate endpoint.', tags=['password manager'])
@marshal_with(EncryptResponseSchema)  # marshalling
class GenerateAPI(MethodResource, Resource):
    def get(self):
        req = password_gen()
        resp = Response(json.dumps(req, default=str), status=200, content_type="application/json")
        return {
            'message': resp
        }


if __name__ == '__main__':
    db.init_db()
    api.add_resource(CreateAPI, '/create')
    api.add_resource(RetrieveAPI, '/retrieve')
    api.add_resource(UpdateAPI, '/update')
    api.add_resource(DeleteAPI, '/delete')
    api.add_resource(GenerateAPI, '/generate')
    docs.register(CreateAPI)
    docs.register(RetrieveAPI)
    docs.register(UpdateAPI)
    docs.register(DeleteAPI)
    docs.register(GenerateAPI)
    app.run(host="0.0.0.0", port=5001, debug=True)
