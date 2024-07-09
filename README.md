# To contribute

## On windows

Create a virtual environment
python -m venv .venv

Activate virtual environment
./.venv/Scripts/Activate.ps1

Install requirements
pip install -r backend/src/requirements.txt

Run project
python backend\src\wsgi.py

### Or use flask, or use vs-code launch.json
set FLASK_APP=api
cd backend/src
flask run


## On linux 

export FLASK_APP=api
cd backend/src
flask run