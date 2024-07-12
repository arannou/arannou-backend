# To contribute

## On windows

Create a virtual environment
python -m venv .venv

Activate virtual environment
./.venv/Scripts/Activate.ps1

Install requirements
pip install -r requirements.txt

Run project with flask (or use vs-code launch.json)

flask run

## On linux

Create a virtual environment
virtualenv ./venv
source venv/bin/activate

Install requirements
pip install -r requirements.txt

flask run

### Or

gunicorn app:app

# Linting
