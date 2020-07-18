import sys

from flask import Blueprint, request
from api.utils.responses import response_with
from api.utils import responses as resp
from api.models.users import User, UserSchema
from api.utils.database import db
from flask_jwt_extended import (
    jwt_refresh_token_required,
    create_access_token, create_refresh_token,
)
user_routes = Blueprint("user_routes", __name__)

## sign up
@user_routes.route('/', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        data['password'] = User.generate_hash(data['password'])
        user_schema = UserSchema()
        user = user_schema.load(data)
        result = user_schema.dump(user.create())

        return response_with(resp.CREATED_201)

    except Exception as ex:
        print(ex, file=sys.stderr)
        return response_with(resp.INVALID_INPUT_422)

## sign in (aka login)
@user_routes.route('/login', methods=['POST'])
def authenticate_user():
      try:
        data = request.get_json()
        current_user = User.find_by_username(data['username'])

        if not current_user:
            return response_with(resp.SERVER_ERROR_404)

        if User.verify_hash(data['password'], current_user.password):
            access_token = create_access_token(identity=data['username'], expires_delta=False)
            refresh_token = create_refresh_token(identity=data['username'], expires_delta=False)

            return response_with(resp.CREATED_201,
                                 value={'message': f'Logged in as {current_user.username}',
                                        'access_token': access_token,
                                        'refresh_token': refresh_token})
        else:
            return response_with(resp.UNAUTHORIZED_401)

      except Exception as ex:
        print(ex, file=sys.stderr)
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
