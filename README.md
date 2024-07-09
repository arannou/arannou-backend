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
cd backend/src
flask run


## On linux

Create a virtual environment
virtualenv ./venv
source venv/bin/activate

Install requirements
pip install -r backend/src/requirements.txt

cd backend/src
flask run
## Or
gunicorn --config gunicorn_config.py app:app