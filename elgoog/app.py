# coding=utf-8

import os
from os.path import dirname, join

from flask import Flask
from flask_cors import CORS

from elgoog.blueprints import register_blueprints
from elgoog import utils
from elgoog import config


def set_config(app):
    home_dir = os.environ.get('ELGOOG_HOME')
    if home_dir is None:
        home_dir = dirname(dirname(__file__))
        app.config['HOME_DIR'] = home_dir

    conf_dir = os.environ.get('ELGOOG_CONF_DIR')
    c = utils.load_config(join(conf_dir, 'elgoog.py'))
    config.elgoog_token = c.get('elgoog_token')


def create_app():
    app = Flask(__name__)

    CORS(app)
    set_config(app)
    register_blueprints(app)

    return app
