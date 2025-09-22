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
        skippable = ['error']
        self.state = {}
        for stuff in self.core.validator.get_object_types():
            if stuff in skippable:
                continue
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
                    self.state[model_type].append(BaseObject(model_type, object_data=obj))

                self.core.logger.logs("Model", "loaded "+str(len(model_obj))+" "+model_type)


    def get_obj_lists(self, object_type):
        """ List of dicts """
        return [obj.data for obj in self.state[object_type]]

    def save(self):
        """ Save object to model """
        for model in os.listdir(MODEL_PATH):
            # Read model file
            model_type = model.split('.json')[0]
            if model_type not in self.state:
                continue # unused file
            with open(os.path.join(MODEL_PATH, model), "w", encoding="utf-8") as model_file:

                # Dump result to model file
                json.dump(self.get_obj_lists(model_type), model_file, indent=2)

                self.core.logger.logs("Model", "saved "+str(len(self.get_obj_lists(model_type)))+" "+model_type)

    def get_obj(self, object_type, _id):
        """ Get object by id """
        matches=[obj for obj in self.state[object_type] if obj.data["id"] == _id]
        if len(matches) >= 1:
            return matches[0]
        return None

    def delete_obj(self, object_type, _id):
        """ Delete object"""
        # Remove it from model
        self.state[object_type] = [obj for obj in self.state[object_type] if obj.data["id"] != _id]

        # Write model on disk
        self.save()
        self.core.logger.logs("Model", "deleted "+object_type+" with id "+_id)

    def delete_all_objects(self, object_type):
        """ Remove all objects of a type """
        self.state[object_type] = []
        # Write model on disk
        self.save()

    def add_obj(self, object_type, obj):
        """" Add and save object """
        self.state[object_type].append(obj)

        # Save on disk
        self.save()

        self.core.logger.logs("Model", "added "+object_type+" with id "+obj.data["id"])

    def edit_obj(self, object_type, _id, new_data):
        edited_obj = None
        for obj in self.state[object_type]:
            if obj.data["id"] == _id:
                obj.edit(new_data)
                edited_obj = obj
                break

        if edited_obj:
            # Save on disk
            self.save()
            return edited_obj.data
        return None