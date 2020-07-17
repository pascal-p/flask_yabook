import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DEBUG = False
    TESTING = False
    # CSRF_ENABLED = True # Because API
    # SECRET_KEY = 'this-really-needs-to-be-changed'
    # SQLALCHEMY_TRACK_MODIFICATIONS = False

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL_PROD']
    DEBUG = False


class StagingConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL_STAGING']
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL_DEV']
    DEVELOPMENT = True
    DEBUG = True


class TestingConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL_TESTING']
    TESTING = True
