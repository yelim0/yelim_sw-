from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False) 
    password = db.Column(db.String(200), nullable=False)
    nickname = db.Column(db.String(80), nullable=False)  
    is_admin = db.Column(db.Boolean, default=False) 
    is_suspended = db.Column(db.Boolean, default=False) 

    diaries = db.relationship('Diary', backref='user', lazy=True)
    posts = db.relationship('CommunityPost', backref='author', lazy=True)
    comments = db.relationship('Comment', backref='user', lazy=True)


class Diary(db.Model):
    __tablename__ = 'diaries'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    content = db.Column(db.Text, nullable=False)
    weather = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    advantages = db.relationship('Advantage', backref='diary', lazy=True)


class Advantage(db.Model):
    __tablename__ = 'advantages'
    id = db.Column(db.Integer, primary_key=True)
    keyword = db.Column(db.String(50), nullable=False)

    diary_id = db.Column(db.Integer, db.ForeignKey('diaries.id'), nullable=False)


class CommunityPost(db.Model):
    __tablename__ = 'community_posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    like_count = db.Column(db.Integer, default=0)  
    
    comments = db.relationship('Comment', backref='post', lazy=True)

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    post_id = db.Column(db.Integer, db.ForeignKey('community_posts.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    
class Report(db.Model):
    __tablename__ = 'reports'
    id = db.Column(db.Integer, primary_key=True)
    report_type = db.Column(db.String(20), nullable=False)  
    target_id = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

