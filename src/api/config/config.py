import os
basedir = os.path.abspath(os.path.dirname(__file__))



def assign_or_raise(key):
    if not os.environ.get(key):
        raise ValueError(f"No {key} set for Flask application")
    return os.environ.get(key)


def assign_with_default(key, dval):
    return os.environ.get(key) if os.environ.get(key) else dval


class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = False # Because API
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    YABOOK_ITEMS_PER_PAGE = 3
    EMAIL_TOKEN_EXP=assign_with_default('EMAIL_TOKEN_EXP', 3600)

    SQLALCHEMY_DATABASE_URI = os.environ['DB_URL']
    SQLALCHEMY_DATABASE_URI = assign_or_raise('DB_URL')

    JWT_ACCESS_TOKEN_EXPIRES = assign_with_default('JWT_ACCESS_TOKEN_EXPIRES', 600)
    JWT_REFRESH_TOKEN_EXPIRES = assign_with_default('JWT_REFRESH_TOKEN_EXPIRES', 86400)

    JWT_SECRET_KEY = assign_or_raise('JWT_SECRET_KEY')
    SECRET_KEY = assign_or_raise('SECRET_KEY')
    SECURITY_PASSWORD_SALT= assign_or_raise('SECURITY_PASSWORD_SALT')

    MAIL_DEFAULT_SENDER = 'yabook@nowhere.org'
    MAIL_SERVER         = None  # 'email_providers_smtp_address'
    MAIL_PORT           = None  # <mail_server_port>
    MAIL_USERNAME       = None  # 'your_email_address'
    MAIL_PASSWORD       = None  # 'your_email_password'
    MAIL_USE_TLS        = True
    MAIL_USE_SSL        = False


class ProductionConfig(Config):
    ENV = 'production'
    DEBUG = False
    YABOOK_POSTS_PER_PAGE = 10
    # overwriet MAIL PREFS


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
