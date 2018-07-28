"""Main configuration file for project."""

import yaml
import os
import pathlib


PROJECT_NAME = 'flask-readw'
PROJECT_HOME_PATH = pathlib.Path(os.path.realpath(__file__)).parents[1]
READW_SCRIPT_PATH = PROJECT_HOME_PATH.joinpath('run.sh')

RAW_VAULT_PATH = pathlib.Path('/raw_vault/')

NUM_RETRIES = 2


# debug is true by default
DEBUG = bool(os.getenv('DEBUG', True))

_secrets_file = 'secrets.yml' if DEBUG else 'secrets.production.yml'

_secrets_path = PROJECT_HOME_PATH.joinpath('config', _secrets_file)

# get our secrets
with _secrets_path.open() as f:
    _SECRETS = yaml.load(f)

class _Config(object):
    """Holds flask configuration to be consumed by Flask's from_object method."""
    DEBUG = False
    SECRET_KEY = _SECRETS['flask']['SECRET_KEY']
    JSONIFY_PRETTYPRINT_REGULAR = False

class _DevelopmentConfig(_Config):
    """Configuration for development environment."""
    DEBUG = True

config = _DevelopmentConfig if DEBUG else _Config