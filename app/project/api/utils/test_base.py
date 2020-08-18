import unittest
import tempfile

from project import create_app
from project.api.utils.database import db
from project.api.config.config import TestingConfig

class RootTestCase(unittest.TestCase):
    "A base test case"

    def setUp(self):
        app = create_app() # will select TestingConfig
        self.test_db_file = tempfile.mkstemp()[1]

        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + self.test_db_file
        db.init_app(app)
        with app.app_context():
            db.create_all()

        app.app_context().push()
        self.app = app.test_client()

    def tearDown(self):
        # db.session.rollback()
        db.close_all_sessions()
        db.drop_all()
