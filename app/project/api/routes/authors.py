import sys, logging

from flask import Blueprint, request, current_app, url_for
from flask_jwt_extended import jwt_required

from project.api.utils.responses import response_with
from project.api.utils import responses as resp
from project.api.models.authors import Author, AuthorSchema
from project.api.utils.database import db


author_routes = Blueprint("author_routes", __name__)

## Create new Author
@author_routes.route('/', methods=['POST'])
@jwt_required
def create_author():
    """
    Create author endpoint
    ---
    parameters:
      - in: body
        name: body
        schema:
          id: Author
          required:
            - first_name
            - last_name
            - books
          properties:
            first_name:
              type: string
              description: First name of the author
              default: "John"
            last_name:
              type: string
              description: Last name of the author
              default: "Doe"
      - in: header
        name: authorization
        type: string
        required: true
    security:
      - Bearer: []
    responses:
      201:
        description: Author successfully created
        schema:
          id: AuthorCreated
          properties:
            code:
              type: string
            message:
              type: string
            value:
              schema:
                id: AuthorFull
                properties:
                  first_name:
                    type: string
                  last_name:
                    type: string
                  books:
                    type: array
                    items:
                      schema:
                        id: BookSchema
      422:
        description: Invalid input arguments
        schema:
          id: invalidInput
          properties:
            code:
              type: string
            message:
              type: string
    """

    try:
        data = request.get_json()
        author_schema = AuthorSchema()
        author = author_schema.load(data)

        result = author_schema.dump(author.create())  # .data

        return response_with(resp.CREATED_201, value={"author": result})

    except Exception as ex:
        logging.error(f"Intercepted Exception: {ex}")
        return response_with(resp.INVALID_INPUT_422)


## Get list of all authors with Pagination - No Auth required (so far)
@author_routes.route('/', methods=['GET'])
def get_author_list():
    """
    Get author list endpoint
    ---
    parametrers:
    responses:
      200:
        description: Author List
        schema:
          properties:
            code:
              type: string
            message:
              type: string
            count:
              type: integer
            next_url:
              type: string
            prev_url:
              type: string
            authors:
              type: array
              items:
                schema:
                properties:
                  id:
                    type: integer
                  first_name:
                    type: string
                  last_name:
                    type: string
    """

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
    """
    Get author details endpoint
    ---
    parameters:
      - name: author_id
        in: path
        description: author ID
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Author Details
        schema:
          properties:
            code:
              type: string
            message:
              type: string
            author:
              schema:
              properties:
                id:
                  type: integer
                first_name:
                  type: string
                last_name:
                  type: string
      404:
        description: Invalid input arguments
        schema:
          id: invalidInput
          properties:
            code:
              type: string
            message:
              type: string
    """

    fetched = Author.query.get_or_404(author_id)
    author_schema = AuthorSchema()
    author = author_schema.dump(fetched)

    return response_with(resp.SUCCESS_200, value={"author": author})


## Update (whole)  Author
@author_routes.route('/<int:id>', methods=['PUT'])
@jwt_required
def update_author_detail(id):
    """
    Update author endpoint
    ---
    parameters:
      - in: body
        name: body
        schema:
          id: Author
          required:
            - first_name
            - last_name
          properties:
            first_name:
              type: string
              description: First name of the author
            last_name:
              type: string
              description: Last name of the author
      - name: id
        in: path
        description: author ID
        required: true
        schema:
          type: integer
      - in: header
        name: authorization
        type: string
        required: true
    security:
      - Bearer: []
    responses:
      200:
        description: Author successfully updated
        schema:
          id: AuthorModified
          properties:
            code:
              type: string
            message:
              type: string
            value:
              schema:
                id: AuthorFull
                properties:
                  first_name:
                    type: string
                  last_name:
                    type: string
                  created_at:
                    type: string
                  books:
                    type: array
                    items:
                      schema:
                        id: BookSchema
      422:
        description: Invalid input arguments
        schema:
          id: invalidInput
          properties:
            code:
              type: string
            message:
              type: string
    """

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
    """
    Partial Update author endpoint
    ---
    parameters:
      - in: body
        name: body
        schema:
          id: Author
          optional:
            - first_name
            - last_name
          properties:
            first_name:
              type: string
              description: First name of the author
            last_name:
              type: string
              description: Last name of the author
      - name: id
        in: path
        description: author ID
        required: true
        schema:
          type: integer
      - in: header
        name: authorization
        type: string
        required: true
    security:
      - Bearer: []
    responses:
      200:
        description: Author successfully updated
        schema:
          id: AuthorModified
          properties:
            code:
              type: string
            message:
              type: string
            value:
              schema:
                id: AuthorFull
                properties:
                  first_name:
                    type: string
                  last_name:
                    type: string
                  created_at:
                    type: string
                    format: date-time
                  books:
                    type: array
                    items:
                      schema:
                        id: BookSchema
      422:
        description: Invalid input arguments
        schema:
          id: invalidInput
          properties:
            code:
              type: string
            message:
              type: string
    """

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
    """
    Delete author endpoint
    ---
    parameters:
      - name: id
        in: path
        description: author ID
        required: true
        schema:
          type: integer
      - in: header
        name: authorization
        type: string
        required: true
    security:
      - Bearer: []
    responses:
      204:
        description: Author successfully deleted
        schema:
      422:
        description: Invalid input arguments
        schema:
          id: invalidInput
          properties:
            code:
              type: string
            message:
              type: string

    """
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
        logging.error(f"Intercepted Exception: {ex}")
        return response_with(resp.INVALID_INPUT_422)
