""" Module for common functions """
import uuid
from os import kill
from datetime import datetime

def current_date_time():
    """ Returns current date & time with format '%Y/%m/%d at %H:%M:%S'"""
    return datetime.today().strftime('%Y/%m/%d at %H:%M:%S')

def generate_id():
    """ Generates a 8 chars length uuid """
    return str(uuid.uuid4())[:8]

def valid_path_to_string(valid_path):
    """ Converts a path to a string """
    str_path=""

    for part in valid_path:
        if isinstance(part, int):
            str_path+="["+str(part)+"]"
        else:
            str_path+="/"+part

    return str_path
