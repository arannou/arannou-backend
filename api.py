""" Module for api endpoints"""
import json
from logging.config import dictConfig
import os
import traceback
from flask import Flask, request, redirect, render_template
from flask_cors import CORS
from base_object import BaseObject
from exceptions import ImportException
from utils import generate_id
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
        
        return endpoint_wrapper(
            object_type,
            core.instance.create_method(request.get_json(), object_type))
    else :
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
        return object_id

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
    except Exception as exception:
        err = {"error" : f"Error with {object_type}", "details": exception.args }
        print(json.dumps(err))
        print(type(exception).__name__)
        print(traceback.format_exc())
        return err, 400
