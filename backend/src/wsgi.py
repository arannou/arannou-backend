#!/bin/python3.9

from api import app
from waitress import serve
serve(app, host='0.0.0.0', port=8080)