import json
import io
import unittest

from api.utils.test_base import RootTestCase
from api.models.authors import Author
from api.models.books import Book
from datetime import datetime
from flask_jwt_extended import create_access_token


CONTENT_TYPE = 'application/json'


def create_books():
    aut1 = Author(first_name="Jane", last_name="Doe").create()
    aut2 = Author(first_name="Hugo", last_name="P").create()

    bk1a1 = Book(title="Test Book 1", year=1970, author_id=aut1.id)
    bk2a1 = Book(title="Test Book 2", year=1981, author_id=aut1.id)

    bk1a2 = Book(title="Test Book 3", year=1986, author_id=aut2.id)
    bk2a2 = Book(title="Test Book 4", year=1992, author_id=aut2.id)
    bk3a2 = Book(title="Test Book 4", year=1972, author_id=aut2.id)
    return [bk1a1, bk2a1], [bk1a2, bk2a2, bk3a2]


def book_factory():
    bks_a1, bks_a2 = create_books()
    for book in bks_a1:
        book.create()

    for book in bks_a2:
        book.create()

    return


class TestAuthors(RootTestCase):

    def setUp(self):
        super().setUp()
        book_factory()
        self.login()  # gen. token for auth

    def tearDown(self):
       super().tearDown()

    def login(self):
        self.token = create_access_token(identity='test@corto.org', fresh=True)
        return

    def test_create_book(self):
        book = {
            'title': 'Corto toujours un peu plus loin',
            'year': 1984,
            'author_id': 2
        }
        resp = self.app.post('/api/books/',
                             data=json.dumps(book),
                             content_type=CONTENT_TYPE,
                             headers= {'Authorization': 'Bearer ' + self.token}
        )
        data = json.loads(resp.data)

        self.assertEqual(201, resp.status_code)
        self.assertTrue('book' in data)
        return

    def test_create_book_with_no_author(self):
        book = {
            'title': 'Corto toujours un peu plus loin',
            'year': 1982
        }
        resp = self.app.post('/api/books/',
                             data=json.dumps(book),
                             content_type=CONTENT_TYPE,
                             headers= {'Authorization': 'Bearer ' + self.token}
        )
        data = json.loads(resp.data)

        self.assertEqual(422, resp.status_code)
        return

    def test_create_book_no_authorization(self):
        book = {
            'title': 'Corto toujours un peu plus loin',
            'year': 1982,
            'author_id': 2
        }
        resp = self.app.post('/api/books/',
                             data=json.dumps(book),
                             content_type=CONTENT_TYPE,
                             # NO Authorization
        )
        data = json.loads(resp.data)

        self.assertEqual(401, resp.status_code)
        return

    def test_get_books(self):
        resp = self.app.get('/api/books/',
                            content_type=CONTENT_TYPE,
        )
        data = json.loads(resp.data)

        self.assertEqual(200, resp.status_code)
        self.assertTrue('books' in data)
        return

    def test_get_book_details(self):
        resp = self.app.get('/api/books/2',
                            content_type=CONTENT_TYPE,
        )
        data = json.loads(resp.data)

        self.assertEqual(200, resp.status_code)
        self.assertTrue('book' in data)
        return

    def test_update_book(self):
        book = {
            'year': 2002,
            'title': 'Amelie'
        }
        resp = self.app.patch('/api/books/2',
                              data=json.dumps(book),
                              content_type=CONTENT_TYPE,
                              headers= {'Authorization': 'Bearer ' + self.token}
        )

        self.assertEqual(200, resp.status_code)
        return


if __name__ == '__main__':
    unittest.main()
