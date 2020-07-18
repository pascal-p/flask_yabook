import sys

from flask import Blueprint, request
from api.utils.responses import response_with
from api.utils import responses as resp
from api.models.books import Book, BookSchema
from api.utils.database import db
from flask_jwt_extended import jwt_required

book_routes = Blueprint("book_routes", __name__)

## Create new Book
@book_routes.route('/', methods=['POST'])
@jwt_required
def create_book():
    try:
        data = request.get_json()
        book_schema = BookSchema()
        book = book_schema.load(data)
        print("DEBUG: got book:", book, file=sys.stderr)

        result = book_schema.dump(book.create())

        return response_with(resp.CREATED_201, value={"book": result})

    except Exception as ex:
        print("Intercepted Exception:", ex, file=sys.stderr)
        return response_with(resp.INVALID_INPUT_422)


## Get list of all books - TODO: Pagination
# @book_routes.route('/', methods=['GET'])
# def get_book_list():
#     fetched = Book.query.all()
#     book_schema = BookSchema(many=True, only=['author_id', 'title', 'year'])
#     books = book_schema.dump(fetched)

#     return response_with(resp.SUCCESS_200, value={"books": books})

## Get list of all books - TODO: Pagination
@book_routes.route('/', methods=['GET'])
def get_book_list():
    page = request.args.get('page', 1, type=int) # default 1st page

    pagination = Book.query.paginate(
        page, per_page=current_app.config['YABOOK_POSTS_PER_PAGE'],
        error_out=False)

    fetched = pagination.items
    prev, next = None, None

    if pagination.has_prev:
        prev = url_for('api.get_book_list', page=page-1)

    if pagination.has_next:
        next = url_for('api.get_book_list', page=page+1)

    
    book_schema = BookSchema(many=True, only=['author_id', 'title', 'year'])  
    books = book_schema.dump(fetched)

    # TODO: plug: prev_url, next_url, count
    value = {'books': books, 'prev_url': prev, 
      'next_url': next,
      'count': pagination.total
    } 

    return response_with(resp.SUCCESS_200, value=value)

## Get one specific Book
@book_routes.route('/<int:book_id>', methods=['GET'])
def get_book_detail(book_id):
    fetched = Book.query.get_or_404(book_id)
    book_schema = BookSchema()
    book = book_schema.dump(fetched)

    return response_with(resp.SUCCESS_200, value={"book": book})


## Update (whole)  Book
@book_routes.route('/<int:id>', methods=['PUT'])
@jwt_required
def update_book_detail(id):
    data, get_book = _find_book_by_id(id)

    get_book.title = data['title']
    get_book.year = data['year']

    _persist(db, get_book, action='update')
    book_schema = BookSchema()
    book = book_schema.dump(get_book)

    return response_with(resp.SUCCESS_200, value={"book": book})


## Update (partial) Book
@book_routes.route('/<int:id>', methods=['PATCH'])
@jwt_required
def modify_book_detail(id):
    data, get_book = _find_book_by_id(id)

    if data.get('title'):
        get_book.title = data['title']

    if data.get('year'):
        get_book.year = data['year']

    _persist(db, get_book, action='update')
    book_schema = BookSchema()
    book = book_schema.dump(get_book)
    return response_with(resp.SUCCESS_200, value={"book": book})

## Delete an Book
@book_routes.route('/<int:id>', methods=['DELETE'])
@jwt_required
def delete_book(id):
    get_book = Book.query.get_or_404(id)

    _persist(db, get_book, action='delete')

    return response_with(resp.SUCCESS_204)


## Internal helpers

def _find_book_by_id(id):
    data = request.get_json()
    return data, Book.query.get_or_404(id) # can be NOT FOUND

def _persist(db, book, action='add'):
    try:
        if action == 'update':
            db.session.add(book)
        elif action == 'delete':
            db.session.delete(book)
        else:
            raise Exception("action is either update or delete")

        db.session.commit()

    except Exception as ex:
        print("Intercepted Exception:", ex, file=sys.stderr)
        return response_with(resp.INVALID_INPUT_422)
