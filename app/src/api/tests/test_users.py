import json
import unittest

from datetime import datetime
from api.utils.test_base import RootTestCase
from api.models.users import User
from api.utils.token import generate_verification_token, confirm_verification_token


def set_users():
    pwd1  = 'f0oBarPasswd'
    user1 = User(email='foo.bar@nowhere.org', username='foobar',
                 password=User.generate_hash(pwd1),
                 isVerified=True)

    pwd2 = 'bar @sswOyyy'
    user2 = User(email='bar@anywhere.net', username='bar',
                 password=User.generate_hash(pwd2))
    return (user1, pwd1), (user2, pwd2)

def user_factory():
    (u1, _), (u2, _) = set_users()
    u1.create()
    u2.create()
    return


class TestUsers(RootTestCase):

    def setUp(self):
        super().setUp()
        user_factory()

    def tearDown(self):
       super().tearDown()

    def test_login_user(self):
        (full_user, pwd), _ = set_users()
        user = {
            "email": full_user.email,
            "password": pwd
        }

        resp = self.app.post('/api/users/login',
                             data=json.dumps(user),
                             content_type='application/json'
        )
        data = json.loads(resp.data)

        self.assertEqual(200, resp.status_code)
        self.assertTrue('access_token' in data)
        return

    def test_login_wrong_credentials(self):
        (full_user, _), _ = set_users()
        user = {
            "email": full_user.email,
            "password": 'wrong pwd!'
        }

        resp = self.app.post('/api/users/login',
                             data=json.dumps(user),
                             content_type='application/json'
        )
        data = json.loads(resp.data)

        self.assertEqual(401, resp.status_code)
        return

    def test_login_unverified_user(self):
        _, (full_user, pwd) = set_users()
        user = {
            "email": full_user.email,
            "password": pwd
        }
        resp = self.app.post('/api/users/login',
                             data=json.dumps(user),
                             content_type='application/json'
        )
        data = json.loads(resp.data)

        self.assertEqual(400, resp.status_code)
        return

    def test_create_user(self):
        user = {
          "username" : 'babar',
          "password" : 'hello world',
          "email" : 'babar@nowhere.net'
        }
        resp = self.app.post('/api/users/',
                             data=json.dumps(user),
                             content_type='application/json'
        )
        data = json.loads(resp.data)

        self.assertEqual(201, resp.status_code)
        self.assertTrue('created' in data['code'])
        return

    def test_create_user_without_username(self):
        user = {
            # NO username on purpose
            "password" : 'hello world',
            "email" : 'babar@nowhere.net'
        }
        resp = self.app.post('/api/users/',
                             data=json.dumps(user),
                             content_type='application/json'
        )
        data = json.loads(resp.data)

        self.assertEqual(422, resp.status_code)
        return
    
    def test_confirm_email_for_already_verified_user(self):
        (full_user, _), _ = set_users()
        token = generate_verification_token(full_user.email)
        resp = self.app.get('/api/users/confirm/' + token)
        data = json.loads(resp.data)
        
        self.assertEqual(422, resp.status_code)
        return

    def test_confirm_email_with_incorrect_email(self):
        # (full_user, _), _ = set_users()
        token = generate_verification_token('bachi@bouzouk.fr')
        resp = self.app.get('/api/users/confirm/' + token)
        data = json.loads(resp.data)
        
        self.assertEqual(404, resp.status_code)


if __name__ == '__main__':
    unittest.main()
