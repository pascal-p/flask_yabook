import sys

from flask import Blueprint, request
from api.utils.responses import response_with
from api.utils import responses as resp
from api.models.authors import Author, AuthorSchema
from api.utils.database import db
from flask_jwt_extended import jwt_required

author_routes = Blueprint("author_routes", __name__)

## Create new Author
@author_routes.route('/', methods=['POST'])
@jwt_required
def create_author():
    try:
        data = request.get_json()
        print("DEBUG: got data:", data, file=sys.stderr)
        author_schema = AuthorSchema()
        print("DEBUG: got author_schema:", author_schema, file=sys.stderr)
        author = author_schema.load(data)
        print("DEBUG: got author:", author, file=sys.stderr)

        result = author_schema.dump(author.create())  # .data

        return response_with(resp.CREATED_201, value={"author": result})

    except Exception as ex:
        print("Intercepted Exception:", ex, file=sys.stderr)
        return response_with(resp.INVALID_INPUT_422)


## Get list of all authors - TODO: Pagination
@author_routes.route('/', methods=['GET'])
@jwt_required
def get_author_list():
    fetched = Author.query.all()
    author_schema = AuthorSchema(many=True, only=['first_name', 'last_name', 'id'])
    authors = author_schema.dump(fetched)

    return response_with(resp.SUCCESS_200, value={"authors": authors})


## Get one specific Author
@author_routes.route('/<int:author_id>', methods=['GET'])
def get_author_detail(author_id):
    fetched = Author.query.get_or_404(author_id)
    author_schema = AuthorSchema()
    author = author_schema.dump(fetched)

    return response_with(resp.SUCCESS_200, value={"author": author})


## Update (whole)  Author
@author_routes.route('/<int:id>', methods=['PUT'])
@jwt_required
def update_author_detail(id):
    data, get_author = _find_author_by_id(id)

    get_author.first_name = data['first_name']
    get_author.last_name = data['last_name']

    _persist(db, get_author, action='update')
    author_schema = AuthorSchema()
    author = author_schema.dump(get_author)

    return response_with(resp.SUCCESS_200, value={"author": author})


## Update (partial) Author
@author_routes.route('/<int:id>', methods=['PATCH'])
@jwt_required
def modify_author_detail(id):
    data, get_author = _find_author_by_id(id)

    if data.get('first_name'):
        get_author.first_name = data['first_name']

    if data.get('last_name'):
        get_author.last_name = data['last_name']

    _persist(db, get_author, action='update')
    author_schema = AuthorSchema()
    author = author_schema.dump(get_author)
    return response_with(resp.SUCCESS_200, value={"author": author})

## Delete an Author
@author_routes.route('/<int:id>', methods=['DELETE'])
@jwt_required
def delete_author(id):
    get_author = Author.query.get_or_404(id)

    _persist(db, get_author, action='delete')

    return response_with(resp.SUCCESS_204)


## Internal helpers

def _find_author_by_id(id):
    data = request.get_json()
    return data, Author.query.get(id) # can be NOT FOUND

def _persist(db, author, action='add'):
    try:
        if action == 'update':
            db.session.add(author)
        elif action == 'delete':
            db.session.delete(author)
        else:
            raise Exception("action is either update or delete")

        db.session.commit()

    except Exception as ex:
        print("Intercepted Exception:", ex, file=sys.stderr)
        return response_with(resp.INVALID_INPUT_422)
