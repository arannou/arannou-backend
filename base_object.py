""" Module for base_object """

from utils import current_date_time, generate_id

class BaseObject:
    """ BaseObject managment class """
    def __init__(self, object_type, object_data = None):
        if object_data is None:
            object_data = {} # avoid W0102 dangerous-default-value

        # Minimal data
        self.data = {
            "id" : generate_id(),
            "type" : object_type,
            "creation_date": current_date_time()
        }

        self.id = self.data["id"]

        # Merge minimal data with BaseObject data
        self.data = {**self.data, **object_data}

    def edit(self, new_object_data):
        """ Edit a BaseObject """

        # Update state
        self.data = {**self.data, **new_object_data}
