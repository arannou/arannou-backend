""" Module for api endpoints"""
import os
import json
from logging.config import dictConfig
import traceback
from flask import Flask, request, redirect, render_template
from flask_cors import CORS
from baseObject import BaseObject
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
    else :
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
            new_data = request.get_json()
            # Validator. Stops here if object is invalid
            validator_error = core.instance.validator.validate_object_creation(object_type, new_data)
            assert validator_error is None, {"validator": validator_error}

            # Create object
            new_object = BaseObject()

            new_object.edit(new_data)

            if not new_object["name"]:
                new_object["name"] = generate_id()
            assert core.instance.model.get_obj(object_type, new_object["name"]) is None, "Object already exist with that name"

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

    def import_method():
        object_file = request.files[object_type]
        imported = core.instance.import_object(object_file, object_type)
        return imported.data
    
    return endpoint_wrapper(object_type, import_method)


def endpoint_wrapper(object_type, endpoint_method):
    """ Wrap api actions with exceptions and map objects """
    
    try:
        if object_type in core.instance.validator.get_object_types():
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


# if __name__ == "__main__":
#     HOST = "0.0.0.0"
#     port = int(os.getenv('PORT', "81"))

#     app.run(host=HOST, port=port)