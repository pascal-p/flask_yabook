import sys, logging

from flask import Blueprint, request, current_app, url_for
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
        result = book_schema.dump(book.create())

        return response_with(resp.CREATED_201, value={"book": result})

    except Exception as ex:
        logging.error(f"Intercepted Exception: {ex}")
        return response_with(resp.INVALID_INPUT_422)


## Get list of all books with Pagination - No Auth required (so far)
@book_routes.route('/', methods=['GET'])
def get_book_list():
    page = request.args.get('page', 1, type=int) # default 1st page, cast it as an int
    num_item_per_page = current_app.config['YABOOK_ITEMS_PER_PAGE']

    # start from first page:
    if page < 0: page = 1

    pagination = Book.query.paginate(
        page, per_page=num_item_per_page,
        error_out=False)

    count = pagination.total
    max_pages = count // num_item_per_page
    max_pages += 0 if count % num_item_per_page == 0 else 1

    fetched = pagination.items
    prev_url, next_url = None, None

    if pagination.has_prev:
        if page <= max_pages:
            prev_url = url_for('book_routes.get_book_list', page=page-1)
        else:
            # point to actual last page (for example)
            prev_url = url_for('book_routes.get_book_list', page=max_pages)

    if pagination.has_next:
        next_url = url_for('book_routes.get_book_list', page=page+1)

    book_schema = BookSchema(many=True, only=['author_id', 'title', 'year'])
    books = book_schema.dump(fetched)
    value = {'books': books, 'prev_url': prev_url,
      'next_url': next_url,
      'count': count
    }

    return response_with(resp.SUCCESS_200, value=value)

## Get one specific Book
@book_routes.route('/<int:book_id>', methods=['GET'])
def get_book_detail(book_id):
    fetched = Book.query.get_or_404(book_id)
    book_schema = BookSchema()
    book = book_schema.dump(fetched)

    return response_with(resp.SUCCESS_200, value={"book": book})


## Update (whole) Book
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
        logging.error(f"Intercepted Exception: {ex}")
        return response_with(resp.INVALID_INPUT_422)
