from api.utils.database import db
from passlib.hash import pbkdf2_sha512 as sha512
from marshmallow_sqlalchemy import ModelSchema
from marshmallow import fields

## User Model
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(512), unique=True, nullable=False)
    password = db.Column(db.String(512), nullable=False)

    def create(self):
        "Persits into DB"
        db.session.add(self)
        db.session.commit()
        return self

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    @staticmethod
    def generate_hash(password):
        return sha512.hash(password)

    @staticmethod
    def verify_hash(password, hash):
        return sha512.verify(password, hash)


## User Serialization
class UserSchema(ModelSchema):
    class Meta(ModelSchema.Meta):
        model = User
        sqla_session = db.session

    id = fields.Number(dump_only=True)
    username = fields.String(required=True)
