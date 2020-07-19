import logging

from itsdangerous import URLSafeTimedSerializer
from flask import current_app

def get_serializer():
    return URLSafeTimedSerializer(current_app.config['SECRET_KEY'])

def generate_verification_token(email):
    # generate a token using email address:
    serializer = get_serializer()
    return serializer.dumps(email,
                            salt=current_app.config['SECURITY_PASSWORD_SALT'])


def confirm_verification_token(token):
    serializer = get_serializer()
    try:
        email = serializer.loads(token,
                                 salt=str(current_app.config['SECURITY_PASSWORD_SALT']),
                                 max_age=int(current_app.config['EMAIL_TOKEN_EXP']))

    except Exception as ex:
        logging.error(ex)
        return ex

    else:
        return email
