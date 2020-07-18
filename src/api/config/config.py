import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = False # Because API
    # SECRET_KEY = 'this-really-needs-to-be-changed'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    YABOOK_ITEMS_PER_PAGE = 3

    key = 'DB_URL'
    if not os.environ.get(key):
        raise ValueError(f"No {key} set for Flask application")
    SQLALCHEMY_DATABASE_URI = os.environ['DB_URL']

    key = 'JWT_ACCESS_TOKEN_EXPIRES'
    JWT_ACCESS_TOKEN_EXPIRES = os.environ.get(key) if os.environ.get(key) else 600

    key = 'JWT_REFRESH_TOKEN_EXPIRES'
    JWT_REFRESH_TOKEN_EXPIRES = os.environ.get(key) if os.environ.get(key) else 86400

    key = 'JWT_SECRET_KEY'
    if not os.environ.get(key):
        raise ValueError(f"No {key} set for Flask application")
    JWT_SECRET_KEY = os.environ.get(key)


class ProductionConfig(Config):
    ENV = 'production'
    DEBUG = False
    YABOOK_POSTS_PER_PAGE = 10


class StagingConfig(Config):
    ENV = 'staging'
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    ENV = 'development'
    DEVELOPMENT = True
    DEBUG = True


class TestingConfig(Config):
    ENV = 'testing'
    TESTING = True
