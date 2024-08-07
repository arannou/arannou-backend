""" Module for core """
from os.path import splitext
import os
from base_object import BaseObject
import yaml
from exceptions import ImportException
from validator import Validator
from model import Model
from logger import Logger



class Core:
    """ Class for the core of the app """

    def __init__(self):
        # Set current working dir to filepath
        os.chdir(os.path.dirname(__file__))

        # load all app conf
        self.logs_path      = os.path.join("./installation", "./app.logs")
        self.images_path    = os.path.join("./installation", "./images")
        self.mock_path      = os.path.join("./installation", "./mocking.json")

        # Init logger
        self.logger = Logger(self.logs_path)

        # Load schema
        self.load_schema()

        # init object validator module
        self.validator = Validator(self.schema)
        # Init model
        self.model = Model(self)


    def load_schema(self):
        """ Loads yaml swagger schema """

        self.schema = {
            "definitions": {}
        }

        with open("./static_root/swagger.yaml", 'r', encoding="utf-8") as file:
            self.schema = yaml.load(file, Loader=yaml.FullLoader)
            #self.schema = JsonRef.replace_refs(schema)

    def create_method(self, new_data, object_type):
        
        # Validator. Stops here if object is invalid
        validator_error = self.validator.validate_object_creation(object_type, new_data)
        assert validator_error is None, {"validator": validator_error}

        # Create object
        new_object = BaseObject(object_type)

        new_object.edit(new_data)

        # Add to model
        self.model.add_obj(object_type, new_object)
        return new_object.data
        
    def replace_schema(self, new_schema):
        """ To update a swagger schema """
        # update only definition part

        error_definition = self.schema["definitions"]["error"]
        self.schema["definitions"] = new_schema["definitions"]
        self.schema["definitions"]["error"] = error_definition

        # save schema
        with open('./static_root/swagger.yaml', 'w', encoding="utf-8") as outfile:
            yaml.dump(self.schema, outfile)

        # init object validator module
        self.validator.load_schema(self.schema)

    def import_image(self, image_file_name):
        """ Import and install a package """
        image_file, ext = splitext(image_file_name.filename)

        assert ext in [".jpeg", ".jpg", ".gif", ".webp", ".png"], "Invalid image extension. Filename must be jpeg, jpg, gif, webp, png"


        image_file_path = os.path.join(self.images_path, image_file_name.filename)

        # Put image into dir
        if not os.path.exists(image_file_path):
            try:
                image_file_name.save(image_file_path)
            except Exception as exception:
                raise ImportException(f"{image_file}: {str(exception)}") from exception
        else:
            raise ImportException(f"Image {image_file} is already uploaded !")

        return image_file_name


    def import_objects(self, object_file):
        with open(object_file, "r", encoding="utf-8") as objects:
            for ob in objects:
                if ob["data_type"] in self.validator.get_object_types():
                    self.create_method(ob, ob["data_type"])

        return object_file


# Singleton pattern
instance = Core()
