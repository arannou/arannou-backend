""" Module for api endpoints"""
import os
import json
from logging.config import dictConfig
import traceback
from flask import Flask, request, redirect, render_template
from flask_cors import CORS
from banana import Banana
from validator import Validator
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
            'filename': '../installation/app.logs'
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


# init object validator module
core.instance.validator = Validator()


@app.route('/')
def index():
    """ Redirect to index """
    return redirect("/index.html")

@app.route('/api/')
def version():
    """ Return current version of instance """
    return {
        "status":"ok",
        "version": core.instance.version
    }

################
# Schemas mgnt #
################

@app.route('/api/schema')
def get_schema():
    """ Return schema """
    return core.instance.schema

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
            new_data = request.get_json()
            # Validator. Stops here if object is invalid
            validator_error = core.instance.validator.validate_object_creation(object_type, new_data)
            assert validator_error is None, {"validator": validator_error}

            # Create object
            if object_type == "bananas":
                new_object = Banana()
            elif object_type == "apples":
                new_object = Banana()

            new_object.edit(new_data)

            # TODO check unicity on name
            # Add to model
            core.instance.model.add_obj(object_type, new_object)
            return new_object.data
        
        return endpoint_wrapper(object_type, create_method)
    else :
        return {"error" : "request does not contain json body"}, 400

@app.route('/api/<object_type>/<object_name>', methods = ['PUT'])
def edit_object(object_type, object_name):
    """ Edit a given object if possible """
    if request.is_json:
        def edit_method():
            new_data = request.get_json()
            new_object = core.instance.model.get_obj(object_type, object_name)
            assert new_object, f"{object_type} with name {object_name} is not found"

            # Validator
            validator_error = core.instance.validator.validate_object_edit(object_type, new_data)
            assert validator_error is None, {"validator": validator_error}

            new_object.edit(new_data)
            core.instance.model.save()
            core.instance.logger.logs(object_type, object_name+" has been edited")

            return new_object.data
        
        return endpoint_wrapper(object_type, edit_method)
    else :
        return {"error" : "request does not contain json body"}, 400

@app.route('/api/<object_type>/<object_name>', methods = ['DELETE'])
def delete_object(object_type, object_name):
    """ Delete a given object if possible """

    def delete_method():
        assert core.instance.model.get_obj(object_type, object_name), f"{object_type} with name '{object_name}' not found"
        core.instance.model.delete_obj(object_type, object_name)
        return object_name

    return endpoint_wrapper(object_type, delete_method)


@app.route('/api/<object_type>/import', methods=['POST'])
def import_object(object_type):
    """ Import a object from file """

    def banana_method():
        object_file = request.files[object_type]
        imported = core.instance.import_banana(object_file)
        return imported.data
    
    def apple_method():
        object_file = request.files[object_type]
        imported = core.instance.import_apple(object_file)
        return imported.data

    return endpoint_wrapper(object_type, banana_method, apple_method)


def endpoint_wrapper(object_type, endpoint_method):
    """ Wrap api actions with exceptions and map objects """
    try:
        if object_type in ['apples', 'bananas']:
            return endpoint_method(), 201
        else:
            # unknown type of object
            err = {"error" : f"unable to create {object_type}", "details": "This kind of object doesn't exist" }
            print(json.dumps(err))
            return err, 400
    except AssertionError as exception:
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


if __name__ == "__main__":
    HOST = "0.0.0.0"
    port = int(os.getenv('PORT', "81"))

    app.run(host=HOST, port=port)