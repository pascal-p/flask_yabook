import sys

from flask import Blueprint, request, current_app, url_for
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
        author_schema = AuthorSchema()
        author = author_schema.load(data)

        result = author_schema.dump(author.create())  # .data

        return response_with(resp.CREATED_201, value={"author": result})

    except Exception as ex:
        print("Intercepted Exception:", ex, file=sys.stderr)
        return response_with(resp.INVALID_INPUT_422)


## Get list of all authors with Pagination - No Auth required (so far)
@author_routes.route('/', methods=['GET'])
def get_author_list():
    page = request.args.get('page', 1, type=int) # default 1st page, cast it as an int
    num_item_per_page = current_app.config['YABOOK_ITEMS_PER_PAGE']

    # start from first page:
    if page < 0: page = 1

    pagination = Author.query.paginate(
        page, per_page=num_item_per_page,
        error_out=False)

    count = pagination.total
    max_pages = count // num_item_per_page
    max_pages += 0 if count % num_item_per_page == 0 else 1

    fetched = pagination.items
    prev_url, next_url = None, None

    if pagination.has_prev:
        if page <= max_pages:
            prev_url = url_for('author_routes.get_author_list', page=page-1)
        else:
            # point to actual last page (for example)
            prev_url = url_for('author_routes.get_author_list', page=max_pages)

    if pagination.has_next:
        next_url = url_for('author_routes.get_author_list', page=page+1)

    author_schema = AuthorSchema(many=True, only=['first_name', 'last_name', 'id'])
    authors = author_schema.dump(fetched)
    value = {'authors': authors, 'prev_url': prev_url,
      'next_url': next_url,
      'count': count
    }

    return response_with(resp.SUCCESS_200, value=value)


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
