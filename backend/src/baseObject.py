""" Module for baseObject """

from utils import current_date_time


class BaseObject:
    """ BaseObject managment class """
    def __init__(self, object_data = None):
        if object_data is None:
            object_data = {} # avoid W0102 dangerous-default-value

        # Minimal data
        self.data = {
            "current_state" : {},
            "creation_date": current_date_time()
        }

        if "name" in object_data:
            self.name = object_data["name"]

        # Merge minimal data with BaseObject data
        self.data = {**self.data, **object_data}

    def edit(self, new_object_data):
        """ Edit a BaseObject """

        # Update state
        self.data = {**self.data, **new_object_data}
        self.name = new_object_data["name"]
