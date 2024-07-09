""" Module for model """
import os
import json
from base_object import BaseObject

MODEL_PATH = "./installation/models/"
class Model:
    """ Model for data management """
    def __init__(self, core):
        self.core = core

        # Model default values
        self.state = {}
        for stuff in self.core.validator.get_object_types():
            self.state[stuff] = []

        self.load_model_if_possible()

    def load_model_if_possible(self):
        """Read model.json if exists"""
        if not os.path.exists(MODEL_PATH):
            os.makedirs(MODEL_PATH)


        self.core.logger.logs("Model", "starting using existing model "+MODEL_PATH)


        for model_type in list(self.state.keys()):
            model = os.path.join(MODEL_PATH, model_type+'.json')
            if not os.path.exists(model):
                # init file with empty data
                with open(model, "w", encoding="utf-8") as model_file:
                    model_file.write('[]')

            with open(os.path.join(MODEL_PATH, model_type+'.json'),"r", encoding="utf-8") as model_file:
                model_obj = json.load(model_file)

                # Load
                for obj in model_obj:
                    self.state[model_type].append(BaseObject(object_data=obj))



    def get_obj_lists(self, object_type):
        """ List of dicts """
        return [obj.data for obj in self.state[object_type]]

    def save(self):
        """ Save object to model """
        for model in os.listdir(MODEL_PATH):
            # Read model file
            model_type = model.split('.json')[0]
            with open(os.path.join(MODEL_PATH, model), "w", encoding="utf-8") as model_file:

                # Dump result to model file
                json.dump(self.get_obj_lists(model_type), model_file, indent=2)

    def get_obj(self, object_type, name):
        """ Get object by name """
        matches=[obj for obj in self.state[object_type] if obj.name == name]

        if len(matches) >= 1:
            return matches[0]
        return None

    def delete_obj(self, object_type, name):
        """ Delete object"""
        # Retrieve object
        obj = self.get_obj(object_type, name)

        # Remove it from model
        self.state[object_type] = [obj for obj in self.state[object_type] if obj.name != name]

        # Write model on disk
        self.save()

    def add_obj(self, object_type, obj):
        """" Add and save object """
        self.state[object_type].append(obj)

        # Save on disk
        self.save()
