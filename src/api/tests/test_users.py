import json
import unittest

from datetime import datetime
from api.utils.test_base import RootTestCase
from api.models.users import User
from api.utils.token import generate_verification_token, confirm_verification_token


def user_factory():
    user1 = User(email='foo.bar@nowhere.org', username='foobar',
                 password=User.generate_hash('f0oBarPasswd'),
                 isVerified=True).create()
    
    user2 = User(email='bar@anywhere.net', username='bar',
                 password=User.generate_hash('bar @sswOyyy')).create()
    return


class TestUsers(RootTestCase):

    def setUp(self):
        super().setUp()
        user_factory()

    def test_login_user(self):
        user = {
            "email": "foo.bar@nowhere.org",
            "password": "f0oBarPasswd"
        }
        
        resp = self.app.post('/api/users/login',
                             data=json.dumps(user),
                             content_type='application/json'
        )
        data = json.loads(resp.data)

        self.assertEqual(200, resp.status_code)
        self.assertTrue('access_token' in data)
        return

if __name__ == '__main__':
    unittest.main()
