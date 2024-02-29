""" Module for validation for inputs """
import json

from jsonschema import SchemaError, ValidationError, validate
import jsonref
import core
import utils

class Validator:
    """ Validated inputs """
    def __init__(self):
        # Load ref parsed schema
        self.schemas = jsonref.loads(json.dumps(core.instance.schema))


    def validate_syntax(self, object_type, data):
        """ Perform validation from json schema """
        try:
            validate(instance=data, schema=self.schemas['definitions'][object_type])
        except (ValidationError, SchemaError) as exception:

            # Small custo for required prop use case
            if str(exception.relative_schema_path.pop()) == "required":
                prop_path = self.format_required_errors(exception)
                message = "is required"
            else:
                prop_path = utils.valid_path_to_string(exception.path)
                message = exception.message

            return { prop_path: {"type": "syntax", "message": message }}
        return None

    def format_required_errors(self, required_error):
        """ Mandatory since 'required errors' don't return correct missing property. """

        # Message is always formated like that: '<field>' is a required property. So a split will do the job to retrieve missing field
        missing_prop = required_error.message.split("'")[1]

        return utils.valid_path_to_string(required_error.path)+"/"+missing_prop

    def validate_object_creation(self, object, new_debug_data):
        """ Check syntax of object """
        return self.validate_syntax(object, new_debug_data)
    
    def validate_object_edit(self, object, new_debug_data):
        """ Check syntax of object """
        return self.validate_syntax(object, new_debug_data)
    
