""" Module for exceptions """
import traceback

class BaseException(Exception):
    """ Base of all exception """
    def __init__(self, message):
        super().__init__(message)
        print(type(self).__name__)
        print(message)
        print(traceback.format_exc())

class ImportException(BaseException):
    """ Import related"""