#!/bin/bash

if [ ! -d venv ]; then
    python3 -m venv venv
    source venv/bin/activate
    pip install -U pip setuptools
    deactivate
fi

source venv/bin/activate

if [ ! -f requirements.txt ]; then
    pip install -r requirements-base.txt
    pip freeze > requirements.txt
fi

if [[ -n $DEBUG && $DEBUG == true ]]; then
    # trying to install requirements if we get any error
    flask run -h 0.0.0.0 || pip install -r requirements.txt && flask run -h 0.0.0.0
else
    pip install -r requirements.txt
    gunicorn --config=config/gunicorn.py flask_readw:app
fi

exec