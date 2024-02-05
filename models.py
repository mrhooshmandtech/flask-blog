from flask_sqlalchemy import SQLAlchemy
from database import db

class User(db.Model):
    userID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userName = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    profilePicture = db.Column(db.String(255))
    role = db.Column(db.String(255))
    creationDate = db.Column(db.String(255))
    creationTime = db.Column(db.String(255))
    isVerfied = db.Column(db.String(255))

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=False)
    tags = db.Column(db.String(255))
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(255), nullable=False)
    date = db.Column(db.String(255), nullable=False)
    time = db.Column(db.String(255), nullable=False)
    views = db.Column(db.Integer, nullable=False)
    lastEditDate = db.Column(db.String(255))
    lastEditTime = db.Column(db.String(255))


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    post = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=False)
    user = db.Column(db.String(255), nullable=False)
    date = db.Column(db.String(255), nullable=False)
    time = db.Column(db.String(255), nullable=False)
