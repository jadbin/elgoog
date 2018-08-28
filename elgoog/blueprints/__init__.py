# coding=utf-8

from elgoog.blueprints.search import search_blueprint


def register_blueprints(app):

    app.register_blueprint(search_blueprint, url_prefix='/api')
