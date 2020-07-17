import os
from flask import Flask
from flask import jsonify

from api.utils.database import db
from api.utils.responses import response_with
import api.utils.responses as resp

# app = Flask(__name__)

def create_app():
    app = Flask(__name__)

    if os.environ.get('WORK_ENV') == 'PROD':
        app_config = ProductionConfig
    elif os.environ.get('WORK_ENV') == 'TEST':
        app_config = TestingConfig
    elif os.environ.get('WORK_ENV') == 'STAGING':
        app_config = StagingConfig
    else:
        app_config = DevelopmentConfig

    app.config.from_object(config)

    @app.after_request
    def add_header(response):
        return response

    @app.errorhandler(400)
    def bad_request(err):
        logging.error(err)
        return response_with(resp.BAD_REQUEST_400)

    @app.errorhandler(500)
    def server_error(err):
        logging.error(e)
        return response_with(resp.SERVER_ERROR_500)

    @app.errorhandler(404)
    def not_found(err):
        logging.error(err)
        return response_with(resp.SERVER_ERROR_404)

    db.init_app(app)

    with app.app_context():
        db.create_all()

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(port=5000, host="0.0.0.0", use_reloader=False)
