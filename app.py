import datetime
import string
import re
import random
from flask import Flask, render_template, redirect, url_for, session, request, abort
from flask_sqlalchemy import SQLAlchemy
from wtforms import Form, BooleanField, StringField, PasswordField, EmailField, SubmitField, validators
from flask_wtf.file import FileField, FileRequired


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vt.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

w2b_context = {}

article_categories = db.Table(
    "article_categories",
    db.Column("article_id", db.Integer, db.ForeignKey("article.id")),
    db.Column("category_id", db.Integer, db.ForeignKey("category.id")),
)

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    subtitle = db.Column(db.String(80), nullable=False)
    image = db.Column(db.String(80), nullable=False, default="default_article_image.png")
    body = db.Column(db.Text, nullable=False)
    pub_date = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    categories = db.relationship("Category", secondary=article_categories, back_populates="articles")
    comments = db.relationship('Comment', backref='article')

    def get_date(self):
        return datetime.datetime.fromisoformat(str(self.pub_date)).strftime("%A %d. %b %Y")

    def __repr__(self):
        return '<Article %r>' % self.title

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25), nullable=False)
    articles = db.relationship("Article", secondary=article_categories, back_populates="categories")

    def __repr__(self):
        return '<Category %r>' % self.name

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Integer, default=0) # 0, 1, 2, 3, 4, 5  (0-quest, 5-super_admin)
    username = db.Column(db.String(30), unique=True, nullable=False)
    fullname = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(1024), nullable=False)
    image = db.Column(db.String(80), nullable=False, default="default_user_image.png")
    about_me = db.Column(db.String(2048), default="About this user", nullable=False)
    last_login = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    articles = db.relationship('Article', backref='user')
    comments = db.relationship('Comment', backref='user')

    def __repr__(self):
        return '<User %r>' % self.username

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(1024), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'))


class RegistrationForm(Form):
    username = StringField('User Name', [validators.DataRequired(), validators.Length(min=4, max=25)], render_kw={"class":"form-control","maxlength":"25","minlength":"4"})
    email = EmailField('Email address', [validators.DataRequired(), validators.Length(min=8, max=35), validators.Email(message=(u'That\'s not a valid email address.'))], render_kw={"class":"form-control","maxlength":"35","minlength":"8"})
    password = PasswordField('Password', [validators.DataRequired(), validators.Length(min=10, max=35), validators.EqualTo('confirm', message='Passwords must match')], render_kw={"class":"form-control","maxlength":"35","minlength":"10"})
    confirm = PasswordField('Repeat Password', [validators.DataRequired()], render_kw={"class":"form-control"})
    submitbutton = SubmitField("Register")

class LoginForm(Form):
    email = EmailField('Email address', [validators.DataRequired(), validators.Length(min=8, max=35), validators.Email(message=(u'That\'s not a valid email address.'))], render_kw={"class":"form-control","maxlength":"35","minlength":"8"})
    password = PasswordField('Password', [validators.DataRequired(), validators.Length(min=10, max=35)], render_kw={"class":"form-control","maxlength":"35","minlength":"10"})
    submitbutton = SubmitField("Login")

def csrf_text(size=32, chars=string.ascii_uppercase + string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def is_email(email):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if re.fullmatch(regex, email):
        return True
    return False

@app.route("/")
@app.route("/category/<int:cat_id>")
def index(cat_id=None):
    w2b_context.clear()
    if "user_id" in session:
        user = User.query.filter_by(id=session['user_id'])
        w2b_context.update({"user":{"user_id":session['user_id'], "user":user}})
    else:
        w2b_context.update({"user":{"user_id":-1}}) 
    w2b_context.update({"categories":Category.query.all()})
    if cat_id == None :
        w2b_context.update({"articles":Article.query.all(), "category":-1})
    else:
        articles = []
        if Category.query.filter_by(id=cat_id).count() > 0:
            category = Category.query.filter_by(id=cat_id).first()
            for article in Article.query.all():
                if category in article.categories:
                    articles.append(article)
        w2b_context.update({"articles":articles, "category":cat_id})
    return render_template("index.html", cntxt=w2b_context)

@app.route("/post/<int:id>")
def post(id=None):
    w2b_context.clear()
    if "user_id" in session:
        user = User.query.filter_by(id=session['user_id'])
        w2b_context.update({"user":{"user_id":session['user_id'], "user":user}})
    else:
        w2b_context.update({"user":{"user_id":-1}}) 
    if id == None:
        return redirect(url_for('index'))
    article = Article.query.filter_by(id=id).first()
    w2b_context.update({"article":article})
    return render_template("post.html", cntxt=w2b_context)

@app.route("/lr", methods=['POST', 'GET'])
def lr():
    if request.method == "POST":
        # TODO
        return redirect(url_for('index'))
    w2b_context.clear()
    if "user_id" in session:
        session.pop('user_id', None) 
    rform = RegistrationForm()
    lform = LoginForm()
    csrf_token = csrf_text()
    session["csrf_token"] = csrf_token
    w2b_context.update({"user":{"user_id":-1}, "csrf_token":csrf_token, "lform":lform, "rform":rform})
    return render_template("lr.html", cntxt=w2b_context)

@app.route("/logout")
def logout():
	session.pop('user_id', None)
	return redirect(url_for('index'))

@app.route("/edit")
def edit():
    w2b_context.clear()
    if "user_id" in session:
        user = User.query.filter_by(id=session['user_id'])
        w2b_context.update({"user":{"user_id":session['user_id'], "user":user}})
    else:
        w2b_context.update({"user":{"user_id":-1}}) 
    return render_template("edit.html", cntxt=w2b_context)

@app.route("/about")
def about():
    w2b_context.clear()
    if "user_id" in session:
        user = User.query.filter_by(id=session['user_id'])
        w2b_context.update({"user":{"user_id":session['user_id'], "user":user}})
    else:
        w2b_context.update({"user":{"user_id":-1}}) 
    return abort(404)

@app.route("/projects")
def projects():
    w2b_context.clear()
    if "user_id" in session:
        user = User.query.filter_by(id=session['user_id'])
        w2b_context.update({"user":{"user_id":session['user_id'], "user":user}})
    else:
        w2b_context.update({"user":{"user_id":-1}}) 
    return abort(404)

@app.route("/gallery")
def gallery():
    w2b_context.clear()
    if "user_id" in session:
        user = User.query.filter_by(id=session['user_id'])
        w2b_context.update({"user":{"user_id":session['user_id'], "user":user}})
    else:
        w2b_context.update({"user":{"user_id":-1}}) 
    return abort(404)

if __name__ == "__main__":
    app.run(debug=True)