import datetime
from .singletons import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usertype = db.Column(db.Integer, default=0) # 0, 1, 2, 3, 4, 5  (0-quest, 5-super_admin)
    username = db.Column(db.String(30), unique=True, nullable=False)
    fullname = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(1024), nullable=False)
    image = db.Column(db.String(80), nullable=False, default="default_user_image.png")
    about_me = db.Column(db.String(2048), default="About this user", nullable=False)
    last_login = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    articles = db.relationship('Article', backref='user')
    comments = db.relationship('Comment', backref='user')
    sociallinks = db.relationship('SocialLink', backref='user')

    def __repr__(self):
        return '<User %r>' % self.username