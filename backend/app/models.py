from .extensions import db
from datetime import datetime
from passlib.hash import pbkdf2_sha256
import json

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    stories = db.relationship('Story', backref='author', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = pbkdf2_sha256.hash(password)

    def check_password(self, password):
        return pbkdf2_sha256.verify(password, self.password_hash)

class Story(db.Model):
    __tablename__ = 'stories'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=True)
    user_input = db.Column(db.Text, nullable=False)
    country_theme = db.Column(db.String(100), default='India')
    status = db.Column(db.String(50), default='gathering_info')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    pages = db.relationship('StoryPage', backref='story', lazy=True, cascade='all, delete-orphan', order_by='StoryPage.page_no')

    def set_user_input(self, messages):
        self.user_input = json.dumps(messages)

    def get_user_input(self):
        return json.loads(self.user_input) if self.user_input else []

    def to_dict(self, include_pages=False):
        result = {
            'id': self.id, 'title': self.title, 'country_theme': self.country_theme,
            'status': self.status, 'created_at': self.created_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'user_input': self.get_user_input(), 'author': self.author.username
        }
        if include_pages:
            result['pages'] = [page.to_dict() for page in self.pages]
        return result

class StoryPage(db.Model):
    __tablename__ = 'story_pages'
    id = db.Column(db.Integer, primary_key=True)
    story_id = db.Column(db.Integer, db.ForeignKey('stories.id'), nullable=False)
    page_no = db.Column(db.Integer, nullable=False)
    text = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id, 'page_no': self.page_no, 'text': self.text,
            'image_url': self.image_url, 'created_at': self.created_at.isoformat()
        }