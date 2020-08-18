import datetime

from passlib.hash import pbkdf2_sha512 as sha512
from marshmallow_sqlalchemy import ModelSchema
from marshmallow import fields

from project.api.utils.database import db

## User Model
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(512), unique=True, nullable=False)
    password = db.Column(db.String(512), nullable=False)
    isVerified = db.Column(db.Boolean, nullable=False, default=False)
    email = db.Column(db.String(256), unique=True, nullable=False)    # enforce it at the DB level
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now())
    
    def create(self):
        "Persist into DB"
        dtnow = datetime.datetime.utcnow()
        self.created_at = dtnow
        self.updated_at = dtnow        
        db.session.add(self)
        db.session.commit()
        return self

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter_by(email=email).first()
    
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
    email = fields.String(required=True)
    updated_at = fields.DateTime()
