""" Module for api endpoints"""
import json
from logging.config import dictConfig
import os
import traceback
from hashlib import blake2b
from flask import Flask, request, redirect, render_template
from flask_cors import CORS
from exceptions import ImportException, GommetteException

import core

# Create flask app
dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {
        'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            'formatter': 'default'
        },
        'file': {
            'class': 'logging.FileHandler',
            'formatter': 'default',
            'filename': './installation/app.logs'
        }
    },
    'root': {
        'level': 'DEBUG',
        'handlers': ['wsgi', 'file']
    }
})

# Create flask app
app = Flask(__name__, static_url_path="/", static_folder="./static_root")

app.config['JSON_SORT_KEYS'] = False

# Enable cors
cors = CORS(app)

def is_authorized(password, myhash):
    """ Check if password is correct """
    hasher = blake2b()
    hasher.update(password.encode('utf-8'))
    return hasher.hexdigest().encode('utf-8') == myhash

@app.route('/')
def index():
    """ Redirect to index """
    return redirect("/index.html")

@app.route('/api/')
def version():
    """ Return current version of instance """
    return {
        "status":"ok"
    }

################
# Schemas mgnt #
################

@app.route('/api/schema')
def get_schema():
    """ Return schema """
    return core.instance.schema

@app.route('/api/schema', methods = ['POST'])
def post_schema():
    """ Return schema """
    if request.is_json:
        new_schema = request.get_json()
        core.instance.replace_schema(new_schema)
        return 'ok', 201

    return {"error" : "request does not contain json body"}, 400

@app.route('/api/swagger', strict_slashes=False)
def swagger():
    """ Return swagger file """
    return render_template('swagger.html', schema_uri="/api/schema")

############
# CRUDS #
############

@app.route('/api/<object_type>')
def get_all_objects(object_type):
    """ Get all objects of one kind """

    return {object_type: core.instance.model.get_obj_lists(object_type)}

@app.route('/api/<object_type>', methods = ['POST'])
def create_object(object_type):
    """ Create an object from scratch if possible"""
    if request.is_json:
        def create_method():
            return core.instance.create_method(request.get_json(), object_type)
        return endpoint_wrapper(
            object_type,
            create_method)
    # else
    return {"error" : "request does not contain json body"}, 400

@app.route('/api/<object_type>/<object_id>', methods = ['PUT'])
def edit_object(object_type, object_id):
    """ Edit a given object if possible """
    if request.is_json:
        def edit_method():
            new_data = request.get_json()
            new_object = core.instance.model.get_obj(object_type, object_id)
            assert new_object, f"{object_type} with id {object_id} is not found"

            # Validator
            validator_error = core.instance.validator.validate_object_edit(object_type, new_data)
            assert validator_error is None, {"validator": validator_error}

            new_object.edit(new_data)
            core.instance.model.save()
            core.instance.logger.logs(object_type, object_id+" has been edited")

            return new_object.data

        return endpoint_wrapper(object_type, edit_method)

    return {"error" : "request does not contain json body"}, 400

@app.route('/api/<object_type>/<object_id>', methods = ['DELETE'])
def delete_object(object_type, object_id):
    """ Delete a given object if possible """

    def delete_method():
        assert core.instance.model.get_obj(object_type, object_id), f"{object_type} with id '{object_id}' not found"
        core.instance.model.delete_obj(object_type, object_id)
        return {"id": object_id}

    return endpoint_wrapper(object_type, delete_method)

@app.route('/api/import', methods=['POST'])
def import_objects():
    """ Import object from file """

    def import_method():
        object_file = request.files[object_file]
        imported = core.instance.import_objects(object_file)
        return imported.data

    return endpoint_wrapper("error", import_method)


@app.route('/api/upload-image/<category>', methods=['POST'])
def import_image(category):
    """ Import image """

    def import_method():
        if 'image' not in request.files:
            raise ImportException('No image part in the request')

        file = request.files['image']
        if file.filename == '':
            raise ImportException('No selected file')

        folder='images/'+category
        if not os.path.exists(folder):
            os.makedirs(folder)

        image_path = os.path.join(folder, file.filename)
        file.save(image_path)

        return image_path

    return endpoint_wrapper("error", import_method)

def endpoint_wrapper(object_type, endpoint_method):
    """ Wrap api actions with exceptions and map objects """

    try:
        if object_type in core.instance.validator.get_object_types():
            return endpoint_method(), 201

        # else unknown type of object
        err = {"error" : f"unable to create {object_type}", "details": "This kind of object doesn't exist" }
        print(json.dumps(err))
        return err, 400
    except (ImportException, AssertionError) as exception:
        err = {"error" : f"Error with {object_type}", "details": exception.args[0] }
        print(json.dumps(err))
        print(type(exception).__name__)
        print(traceback.format_exc())
        return err, 400
    except Exception as exception: #pylint: disable=broad-except
        err = {"error" : f"Error with {object_type}", "details": exception.args }
        print(json.dumps(err))
        print(type(exception).__name__)
        print(traceback.format_exc())
        return err, 400


# Special gommettes
GOMMETTES_HASH = b'23e1db3a8a421bdeae3773cf31c6cce116afa4c63c11c510f78c858cbec77a03ff164b10c8dffdc218e15791b66e0feac7657314c441fc6df43cc1b12ab52aca'

@app.route("/api/gommette/reset", methods=["POST"])
def reset_scores_api():
    """ Set scores of all users to 0"""
    try:
        data = request.get_json()

        if "password" not in data:
            raise GommetteException("Missing password")
        if not is_authorized(data["password"], GOMMETTES_HASH):
            raise GommetteException("Bad password")

        all_names = [user["name"] for user in core.instance.model.get_obj_lists("gommette")]
        core.instance.delete_all_objects("gommette")
        for user in all_names:
            obj = {
                "name": user,
                "score": 0
            }
            core.instance.create_method(obj, "gommette")
        return "ok", 200
    except GommetteException as exception:
        return {"error": exception.strerror}, 400

@app.route("/api/gommette/overwrite", methods=["POST"])
def overwrite_scores_api():
    """ Erase all users and scores and set new ones """
    try:
        data = request.get_json()
        if "password" not in data:
            raise GommetteException("Missing password")
        if "data" not in data:
            raise GommetteException("Missing data")
        if not is_authorized(data["password"], GOMMETTES_HASH):
            raise GommetteException("Bad password")

        # check format of data["scores"]
        if not isinstance(data["data"], list):
            raise GommetteException("Error: data must be a list")
        scores = data["data"]
        for score in scores:
            # Validator
            validator_error = core.instance.validator.validate_object_edit("gommette", score)
            assert validator_error is None, {"validator": validator_error}

        core.instance.delete_all_objects("gommette")
        core.instance.bulk_create_objects("gommette", data["scores"])

        return "ok", 200
    except GommetteException as exception:
        return {"error": exception.strerror}, 400
    except AssertionError as exception:
        err = {"error" : "Error with gommette", "details": exception.args[0] }
        return err, 400
