from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import string
import random

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, onupdate=datetime.now())
    bookmarks = db.relationship('Bookmark', backref="user")

    def __repr__(self):
        return super().__repr__()

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email
            # don’t include password!
        }

class Bookmark(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=True)
    url = db.Column(db.Text, nullable=False)
    short_url = db.Column(db.String(3), nullable=True)
    visits = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, onupdate=datetime.now())

    def generate_short_url(self):
        chars = string.digits + string.ascii_letters  # 0-9 + a-Z

        # convert array of chosen chars to one string
        chosen_chars = ''.join(random.choices(chars, k=3))  # key is how many i want to pick

        # return bookmark for short_url
        link = self.query.filter_by(short_url=chosen_chars).first()

        if link:
            self.generate_short_url()
        else:
            return chosen_chars

    def __init__(self, **kwargs):  # override constructor
        super().__init__(**kwargs)
        self.short_url = self.generate_short_url()

    def __repr__(self):
        return super().__repr__()

    def to_dict(self):
        return {
            "id": self.id,
            "url": self.url,
            "body": self.body,
            "short_url": self.short_url,
            "visits": self.visits,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "user_id": self.user_id
        }

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
