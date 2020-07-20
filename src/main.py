import os, sys, logging
from flask import Flask, jsonify, Blueprint, request
from flask_jwt_extended import JWTManager
from flask_swagger import swagger
from flask_swagger_ui import get_swaggerui_blueprint

from api.utils.database import db
from api.utils.responses import response_with
from api.utils import responses as resp
from api.utils.mail import mail

from api.routes.authors import author_routes
from api.routes.books import book_routes
from api.routes.users import user_routes


def create_app():
    app = Flask(__name__)

    if os.environ.get('ENV') == 'production':
        from api.config.config import ProductionConfig
        app.config.from_object(ProductionConfig())

    elif os.environ.get('ENV') == 'testing':
        from api.config.config import TestingConfig
        app.config.from_object(TestingConfig())

    elif os.environ.get('ENV') == 'staging':
        from api.config.config import StagingConfig
        app.config.from_object(StagingConfig())

    else:
        from api.config.config import DevelopmentConfig
        app.config.from_object(DevelopmentConfig())
        print("=> DEBUG: ", app.config)

    app.register_blueprint(author_routes, url_prefix=app.config['URL_PREFIX'] + 'authors')
    app.register_blueprint(book_routes, url_prefix=app.config['URL_PREFIX'] + 'books')
    app.register_blueprint(user_routes, url_prefix=app.config['URL_PREFIX'] + 'users')

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

    @app.route("/api/spec")
    def spec():
        swag = swagger(app, prefix=app.config['URL_PREFIX'])
        swag['info']['base'] = request.host_url  # "http://localhost:5000"
        swag['info']['version'] = app.config['API_VER']
        swag['info']['title'] = app.config['APP_NAME']
        return jsonify(swag)

    jwt = JWTManager(app)
    mail.init_app(app)

    swaggerui_blueprint = get_swaggerui_blueprint('/api/docs', '/api/spec', 
                                                  config={'app_name': app.config['APP_NAME']}) 
    app.register_blueprint(swaggerui_blueprint,
                           url_prefix='/api/docs') # SWAGGER_URL)  # where is it define?


    if os.environ.get('ENV') != 'testing':
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
    app.run(port=app.config['PORT'], host=app.config['HOST'], use_reloader=False)
