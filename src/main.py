import os
import sys
import logging
from flask import Flask, jsonify, Blueprint, request
from flask_jwt_extended import JWTManager

from api.config.database import DevelopmentConfig

from api.utils.database import db
from api.utils.responses import response_with
from api.utils import responses as resp

from api.routes.authors import author_routes
from api.routes.books import book_routes
from api.routes.users import user_routes


def create_app():
    app = Flask(__name__)
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')

    for key, dval in [('JWT_ACCESS_TOKEN_EXPIRES', 600),
                      ('JWT_REFRESH_TOKEN_EXPIRES', 86400)]:
        val = os.environ.get('JWT_ACCESS_TOKEN_EXPIRES')
        app.config[key] = dval if val is None else val
    
    if os.environ.get('WORK_ENV') == 'PROD':
        app_config = ProductionConfig

    elif os.environ.get('WORK_ENV') == 'TEST':
        app_config = TestingConfig

    elif os.environ.get('WORK_ENV') == 'STAGING':
        app_config = StagingConfig

    else:
        app_config = DevelopmentConfig

    app.config.from_object(app_config)
    app.register_blueprint(author_routes, url_prefix='/api/authors')
    app.register_blueprint(book_routes, url_prefix='/api/books')
    app.register_blueprint(user_routes, url_prefix='/api/users')

    @app.after_request
    def add_header(response):
        return response

    @app.errorhandler(400)
    def bad_request(err):
        logging.error(err)
        return response_with(resp.BAD_REQUEST_400)

    @app.errorhandler(404)
    def not_found(err):
        logging.error(err)
        return response_with(resp.SERVER_ERROR_404)

    @app.errorhandler(500)
    def server_error(err):
        logging.error(e)
        return response_with(resp.SERVER_ERROR_500)

    jwt = JWTManager(app)
    db.init_app(app)

    with app.app_context():
        db.create_all()

    ## Using the expired_token_loader decorator, we will now call
    ## this function whenever an expired but otherwise valid access
    ## token attempts to access an endpoint
    @jwt.expired_token_loader
    def expired_token_callback(expired_token):
        token_type = expired_token['type']
        value = {
            'sub_status': 666,
            'msg': f'The {token_type} token has expired'
        }
        return response_with(resp.UNAUTHORIZED_401, value)
        
    return app, jwt


if __name__ == "__main__":
    app, jwt = create_app()
    app.run(port=5000, host="0.0.0.0", use_reloader=False)
