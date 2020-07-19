import sys, logging

from flask import Blueprint, request, url_for, render_template_string, current_app
from flask_jwt_extended import (
    jwt_refresh_token_required,
    create_access_token, create_refresh_token,
)

from api.utils.responses import response_with
from api.utils.database import db
from api.utils import responses as resp
from api.utils.token import (
    generate_verification_token,
    confirm_verification_token
)
from api.utils.mail import send_email
from api.models.users import User, UserSchema


user_routes = Blueprint("user_routes", __name__)

## sign up
@user_routes.route('/', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        ## user already defined
        if User.find_by_email(data['email']) is not None or \
           User.find_by_username(data['username']) is not None:
            return response_with(resp.INVALID_INPUT_422)

        ## ok user does not yet exist
        data['password'] = User.generate_hash(data['password'])
        user_schema = UserSchema()
        user = user_schema.load(data)

        token = generate_verification_token(data['email'])
        verif_email = url_for('user_routes.verify_email', token=token, _external=True)

        html = render_template_string("<p>Welcome! Thanks for signing up.Please follow this link to activate your account:</p> <p><a href='{{ verif_email }}'>{{ verif_email }}</a></p> <br /> <p>Thank you</p>", verification_email=verif_email)
        subject = "Please Verify your email"

        curr_env = current_app.config['ENV']
        if curr_env != 'development' and curr_env != 'testing':
            send_email(user.email, subject, html)
        else:
            logging.error(f"email: {user.email}, subject: {subject}")
            logging.error(html)
            logging.error(verif_email)

        result = user_schema.dump(user.create())
        return response_with(resp.CREATED_201)

    except Exception as ex:
        print(ex, file=sys.stderr)
        return response_with(resp.INVALID_INPUT_422)


## email validation
@user_routes.route('/confirm/<string:token>', methods=['GET'])
def verify_email(token):
    try:        
        email = confirm_verification_token(token)
        
    except:
        return response_with(resp.SERVER_ERROR_401)

    user = User.query.filter_by(email=email).first_or_404()
    if user.isVerified:
        return response_with(resp. INVALID_INPUT_422)

    else:
        user.isVerified = True
        db.session.add(user)
        db.session.commit()

    return response_with(resp.SUCCESS_200,
                         value={'message': 'E-mail verified, you can proceed to login now.'})


## sign in (aka login)
@user_routes.route('/login', methods=['POST'])
def authenticate_user():
      try:
        data = request.get_json()
        
        if data.get('email'):
            current_user = User.find_by_email(data['email'])
            
        elif data.get('username'):
            current_user = User.find_by_username(data['username'])
        else:
            # TODO: raise exception
            pass

        if not current_user:
            return response_with(resp.SERVER_ERROR_404)

        if current_user and not current_user.isVerified:
            return response_with(resp.BAD_REQUEST_400)

        if User.verify_hash(data['password'], current_user.password):
            access_token = create_access_token(identity=current_user.username, expires_delta=False)
            refresh_token = create_refresh_token(identity=current_user.username, expires_delta=False)
            return response_with(resp.SUCCESS_200,
                                 value={'message': f'Logged in as {current_user.username}',
                                        'access_token': access_token,
                                        'refresh_token': refresh_token})
        else:
            return response_with(resp.UNAUTHORIZED_401)

      except Exception as ex:
        print(f"Intercepted Exception: {ex}", file=sys.stderr)
        return response_with(resp.INVALID_INPUT_422)


## The jwt_refresh_token_required decorator insures a valid refresh token is present in the
## request before calling this endpoint. We can use the get_jwt_identity() function to get the
## identity of the refresh token, and use the create_access_token() function again to make a
## new access token for this identity.
##
## adapted from: https://flask-jwt-extended.readthedocs.io/en/stable/refresh_tokens/
##
@user_routes.route('/refresh', methods=['POST'])
@jwt_refresh_token_required
def refresh():
    try:
        current_user = get_jwt_identity()
        value = {
            'access_token': create_access_token(identity=current_user, expires_delta=False)
        }

        return response_with(resp.CREATED_201, value)

    except  Exception as ex:
        print(ex, file=sys.stderr)
        return response_with(resp.INVALID_INPUT_422)
