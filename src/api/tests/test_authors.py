import json
import io
import unittest

from api.utils.test_base import RootTestCase
from api.models.authors import Author
# from api.models.books import Book
from datetime import datetime
from flask_jwt_extended import create_access_token

CONTENT_TYPE = 'application/json'


def create_authors():
    aut1 = Author(first_name="John", last_name="Doe")
    aut2 = Author(first_name="Jane", last_name="Doe")
    return aut1, aut2


def author_factory():
    aut1, aut2 = create_authors()
    aut1.create()
    aut2.create()
    return


class TestAuthors(RootTestCase):

    def setUp(self):
        super().setUp()
        author_factory()
        self.login()  # gen. token for auth

    def tearDown(self):
       super().tearDown()

    def login(self):
        self.token = create_access_token(identity='test@corto.org', fresh=True)
        return

    def test_create_author(self):
        author = {
            'first_name': 'Johny',
            'last_name': 'Bambleboo'
        }
        resp = self.app.post('/api/authors/',
                             data=json.dumps(author),
                             content_type=CONTENT_TYPE,
                             headers= {'Authorization': 'Bearer ' + self.token}
        )
        data = json.loads(resp.data)

        self.assertEqual(201, resp.status_code)
        self.assertTrue('author' in data)
        self.assertTrue('created' in data['code'])
        return

    def test_create_author_no_authorization(self):
        author = {
            'first_name': 'Johny',
            'last_name': 'Bambleboo'
        }
        resp = self.app.post('/api/authors/',
                             data=json.dumps(author),
                             content_type=CONTENT_TYPE,
                             # NO Authorization header
        )
        data = json.loads(resp.data)

        self.assertEqual(401, resp.status_code)
        return

    def test_create_author_no_name(self):
        author = {
            'first_name': 'Julien',
            # No last_name
        }
        resp = self.app.post('/api/authors/',
                             data=json.dumps(author),
                             content_type=CONTENT_TYPE,
                             headers= {'Authorization': 'Bearer ' + self.token}
        )
        data = json.loads(resp.data)

        self.assertEqual(422, resp.status_code)
        return

    # def test_upload_avatar(self):
    #     resp = self.app.post('/api/authors/avatar/2',
    #                          data=dict(avatar=(io.BytesIO(b'test'), 'test_file.jpg')),
    #                          content_type='multipart/form-data',
    #                          headers= {'Authorization': 'Bearer ' + self.token}
    #     )

    #     self.assertEqual(200, resp.status_code)
    #     return

    # def test_upload_avatar_with_csv_file(self):
    #     resp = self.app.post('/api/authors/avatar/2',
    #                          data=dict(file=(io.BytesIO(b'test'), 'test_file.csv')),
    #                          content_type='multipart/form-data',
    #                          headers= {'Authorization': 'Bearer '+ self.token}
    #     )

    #     self.assertEqual(422, resp.status_code)
    #     return

    def test_get_authors(self):
        resp = self.app.get('/api/authors/',
                            content_type=CONTENT_TYPE,
        )
        data = json.loads(resp.data)

        self.assertEqual(200, resp.status_code)
        self.assertTrue('authors' in data)
        return

    def test_get_author_detail(self):
        resp = self.app.get('/api/authors/2',
                            content_type=CONTENT_TYPE,
        )
        data = json.loads(resp.data)

        self.assertEqual(200, resp.status_code)
        self.assertTrue('author' in data)
        return

    def test_update_author(self):
        author = {
            'first_name': 'Henri'
            # NO last_name => PATCH
        }

        resp = self.app.patch('/api/authors/2',
                              data=json.dumps(author),
                              content_type=CONTENT_TYPE,
                              headers= {'Authorization': 'Bearer ' + self.token}
        )

        self.assertEqual(200, resp.status_code)
        return

    def test_delete_author(self):
        resp = self.app.delete('/api/authors/2',
                               content_type=CONTENT_TYPE,
                               headers={'Authorization': 'Bearer ' + self.token}
        )

        self.assertEqual(204, resp.status_code)
        return


if __name__ == '__main__':
    unittest.main()
