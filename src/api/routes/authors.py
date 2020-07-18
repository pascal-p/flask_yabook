import sys

from flask import Blueprint, request
from api.utils.responses import response_with
from api.utils import responses as resp
from api.models.authors import Author, AuthorSchema
from api.utils.database import db

author_routes = Blueprint("author_routes", __name__)

## Create new Author
@author_routes.route('/', methods=['POST'])
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
