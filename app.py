import datetime
import time
import string
import re
import random
import os
from werkzeug.utils import secure_filename
from flask import Flask, render_template, redirect, url_for, session, request, abort
from flask_sqlalchemy import SQLAlchemy
from wtforms import Form, BooleanField, StringField, PasswordField, EmailField, SubmitField, TextAreaField, validators
from flask_wtf.file import FileField, FileRequired

M_EXTENTIONS = set(['jpg','png', 'jpeg', 'gif', 'bmp'])
M_UPLOAD_FOLDER = "{}/static/media".format(os.getcwd())

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vt.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['UPLOAD_FOLDER'] = M_UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024 #uploaded file max size
app.secret_key = b'HbfGMYwEOnP3oVEbbnPuoYxx1FHPdLSoNKku3qmKfWUjt6tsLdm3USo5k7JRWmXNiGIjpyXtm7DZ1DbAYAzn0g8LmerBW1DsaeSf'
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
    image = db.Column(db.String(180), nullable=False, default="default_article_image.png")
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

class SocialLink(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sname = db.Column(db.String(25), nullable=False)
    slink = db.Column(db.String(150), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<SocialLink %r>' % self.sname


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Integer, default=0) # 0, 1, 2, 3, 4, 5  (0-quest, 5-super_admin)
    verified = db.Column(db.Integer, default=-1) # approved by {admin.id}
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

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(1024), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'))


class RegistrationForm(Form):
    fullname = StringField('Full Name', [validators.DataRequired(), validators.Length(min=5, max=35)], render_kw={"class":"form-control","maxlength":"35","minlength":"6"})
    username = StringField('User Name', [validators.DataRequired(), validators.Length(min=4, max=25)], render_kw={"class":"form-control","maxlength":"25","minlength":"4"})
    email = EmailField('Email address', [validators.DataRequired(), validators.Length(min=8, max=35), validators.Email(message=(u'That\'s not a valid email address.'))], render_kw={"class":"form-control","maxlength":"35","minlength":"8"})
    password = PasswordField('Password', [validators.DataRequired(), validators.Length(min=10, max=35), validators.EqualTo('confirm', message='Passwords must match')], render_kw={"class":"form-control","maxlength":"35","minlength":"10"})
    confirm = PasswordField('Repeat Password', [validators.DataRequired()], render_kw={"class":"form-control"})
    iagree = BooleanField(" I have read and agree to the terms ", render_kw={"class":"form-check-input","checked":"checked","value":"1"})
    submitbutton = SubmitField("Register")

class LoginForm(Form):
    email = EmailField('Email address', [validators.DataRequired(), validators.Length(min=8, max=35), validators.Email(message=(u'That\'s not a valid email address.'))], render_kw={"class":"form-control","maxlength":"35","minlength":"8"})
    password = PasswordField('Password', [validators.DataRequired(), validators.Length(min=10, max=35)], render_kw={"class":"form-control","maxlength":"35","minlength":"10"})
    rememberme = BooleanField(" Remember me ", render_kw={"class":"form-check-input","checked":"checked","value":"1"})
    submitbutton = SubmitField("Login")


class EditForm(Form): 
    title = StringField("Title", [validators.DataRequired(), validators.Length(min=5, max=80)], render_kw={"class":"form-control","maxlength":"80","minlength":"5"})
    subtitle = StringField("Subtitle", [validators.DataRequired(), validators.Length(min=5, max=80)], render_kw={"class":"form-control","maxlength":"80","minlength":"5"})
    body = TextAreaField("Article Text", [validators.DataRequired(), validators.Length(min=3, max=536870912)], render_kw={"class":"form-control","maxlength":"536870912","minlength":"3", "rows":10})
    image = FileField("Hero Image", validators=[FileRequired()], render_kw={"class":"form-control", "style":"opacity: 0.2;  z-index: -1;"})
    submitbutton = SubmitField("Publish")

def ext_cont(file_name):
   return '.' in file_name and \
   file_name.rsplit('.', 1)[1].lower() in M_EXTENTIONS

def csrf_text(size=32, chars=string.ascii_uppercase + string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def is_email(email):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if re.fullmatch(regex, email):
        return True
    return False

def show_message(msg:str):
    w2b_context.clear()
    if "user_id" in session:
        user = User.query.filter_by(id=session['user_id']).first()
        w2b_context.update({"user":{"user_id":session['user_id'], "user":user}})
    else:
        w2b_context.update({"user":{"user_id":-1}})
    w2b_context.update({"message":msg}) 
    return render_template("message.html", cntxt=w2b_context)

def form_checker(form, rules:dict):
    keys = rules.keys()
    for key in keys:
        if not key in form:
            return False, "{} required!".format(rules[key])
        if len(form[key]) > rules[key]['max']:
            return False, "{} is to long!".format(rules[key])
        if len(form[key]) < rules[key]['min']:
            return False, "{} is to short!".format(rules[key])
        if rules[key]['type'] == "email":
            if not is_email(form[key]):
                return False, "{} not email!".format(form[key])
    return True, None

@app.route("/")
@app.route("/category/<int:cat_id>")
def index(cat_id=None):
    w2b_context.clear()
    if "user_id" in session:
        user = User.query.filter_by(id=session['user_id']).first()
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
        user = User.query.filter_by(id=session['user_id']).first()
        w2b_context.update({"user":{"user_id":session['user_id'], "user":user}})
    else:
        w2b_context.update({"user":{"user_id":-1}}) 
    if id == None:
        return redirect(url_for('index'))
    article = Article.query.filter_by(id=id).first()
    w2b_context.update({"article":article})
    return render_template("post.html", cntxt=w2b_context)

@app.route("/lr")
def lr():
    w2b_context.clear()
    if "user_id" in session:
        session.pop('user_id', None) 
    rform = RegistrationForm()
    lform = LoginForm()
    csrf_token = csrf_text()
    session["csrf_token"] = csrf_token
    w2b_context.update({"user":{"user_id":-1}, "csrf_token":csrf_token, "lform":lform, "rform":rform})
    return render_template("lr.html", cntxt=w2b_context)

@app.route("/lor/<lr>", methods=['POST',])
def lor(lr=None):
    if request.method == "POST" and  request.form['csrf_token'] == session["csrf_token"]:
        if lr == "l":
            rules = {"email":{"min":8,"max":35,"type":"email"}, \
                    "password":{"min":10,"max":35,"type":"text"},}
            success, msg = form_checker(request.form, rules)
            if not success:
                return show_message(msg=msg) 
            user_email = request.form['email']
            user_pass = request.form['password']
            if User.query.filter_by(email=user_email).count()>0:
                us = User.query.filter_by(email=user_email).first()
                if us.password == user_pass:
                    session['user_id'] = us.id
                    return redirect(url_for('index'))
                else:
                    return show_message(msg="Passwords do not match!") 
            else:
                return show_message(msg="This email is wrong!")
        elif lr == "r":
            rules = {"username":{"min":4,"max":25,"type":"text"}, \
                    "fullname":{"min":5,"max":35,"type":"text"}, \
                    "email":{"min":8,"max":35,"type":"email"}, \
                    "password":{"min":10,"max":35,"type":"text"}, \
                    "confirm":{"min":10,"max":35,"type":"text"}}
            success, msg = form_checker(request.form, rules)
            if not success:
                return show_message(msg=msg) 
            user_name = request.form['username']
            full_name = request.form['fullname']
            user_email = request.form['email']
            user_pass = request.form['password']
            user_confirm = request.form['confirm']
            if not(User.query.filter_by(email=user_email).count()>0):
                if not(User.query.filter_by(username=user_name).count()>0):
                    if user_pass == user_confirm:
                        new_user = User(username=user_name, fullname=full_name, email=user_email, password=user_pass)
                        db.session.add(new_user)
                        db.session.commit()
                        session['user_id'] = new_user.id
                        return redirect(url_for('index'))
                    else:
                        return show_message(msg="Passwords do not match!")
                else:
                    return show_message(msg="This username is used!")
            else:
                return show_message(msg="This email is being used!")
        else:
            return show_message(msg="Bad request")
    else:
        return abort(404)

@app.route("/logout")
def logout():
	session.pop('user_id', None)
	return redirect(url_for('index'))

@app.route("/forgotpassword")
def fpass():
    w2b_context.clear()
    if "user_id" in session:
        session.pop('user_id', None)
    w2b_context.update({"user":{"user_id":-1}}) 
    return abort(404)

@app.route("/edit", methods=['POST','GET'])
@app.route("/edit/<int:id>")
def edit(id=None):
    w2b_context.clear()
    if "user_id" in session:
        user = User.query.filter_by(id=session['user_id']).first()
        eform = EditForm()
        if request.method == "GET":
            csrf_token = csrf_text()
            session["csrf_token"] = csrf_token
            w2b_context.update({"user":{"user_id":session['user_id'], "user":user}, "csrf_token":csrf_token, "eform":eform, "categories":Category.query.all()})
            if id!=None and Article.query.filter_by(id=id).count()>0:
                article = Article.query.filter_by(id=id).first()
                if article.user_id == session['user_id']:
                    session['article_id'] = article.id
                    eform.title.data=article.title
                    eform.subtitle.data=article.subtitle
                    eform.body.data=article.body
                    eform.image.validators=[]
            return render_template("edit.html", cntxt=w2b_context)
        if request.method == "POST" and  request.form['csrf_token'] == session["csrf_token"]:
            if "image" not in request.files:
                return show_message(msg="Image file not found!")
            rules = {"title":{"min":5,"max":80,"type":"text"}, \
                    "subtitle":{"min":5,"max":80,"type":"text"}, \
                    "body":{"min":3,"max":536870912,"type":"text"}}
            success, msg = form_checker(request.form, rules)
            if not success:
                return show_message(msg=msg) 
            image = request.files["image"]
            if image.filename == '' and 'article_id' not in session:
                return show_message(msg="Image file not named!")
            if image and ext_cont(image.filename):
                file_name = secure_filename(image.filename)
                file_name = "{}-{}".format(datetime.datetime.strftime(datetime.datetime.utcnow(), "%s"),file_name)
            elif 'article_id' not in session:
                return show_message(msg="Disallowed file extension!")
            else:
                filename = None
            us = User.query.filter_by(id=session["user_id"]).first()
            title = request.form["title"]
            subtitle = request.form['subtitle']
            body = request.form['body']
            cur_time = str(time.time())
            if 'article_id' in session:
                new_article = Article.query.filter_by(id=int(session['article_id'])).first()
                new_article.categories.clear()
                new_article.title=title
                new_article.subtitle=subtitle
                new_article.body=body
                if file_name!=None:
                    new_article.image=file_name
            else:
                new_article = Article(title=title, subtitle=subtitle ,body=body, image=file_name)
            for category in Category.query.all():
                if 'category'+str(category.id) in request.form:
                    if str(request.form['category'+str(category.id)]) == str(category.id):
                        new_article.categories.append(category)
            us.articles.append(new_article)
            if 'article_id' not in session:
                db.session.add(new_article)
            db.session.commit()
            if file_name!=None:
                if not os.path.exists(M_UPLOAD_FOLDER):
                    os.mkdir(os.path.join("{}/static".format(os.getcwd()), "media"))
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], file_name))
            return redirect(url_for('index'))    
    return redirect(url_for('lr'))

@app.route("/user", methods=['POST','GET'])
def user():
    w2b_context.clear()
    if "user_id" in session:
        user = User.query.filter_by(id=session['user_id']).first()
        if request.method == 'GET':
            csrf_token = csrf_text()
            all_socials = {'facebook': None, 'instagram': None, 'twitter': None, 'github': None, 'google': None, 'whatsapp': None, 'linkedin': None}
            session["csrf_token"] = csrf_token
            w2b_context.update({"user":{"user_id":session['user_id'], "user":user}, "csrf_token":csrf_token})
            for social in user.sociallinks:
                all_socials.update({social.sname:social.slink})
            w2b_context.update({"categories":Category.query.all(), "socials":all_socials})
            return render_template("user.html", cntxt=w2b_context)
        if request.method == "POST" and  request.form['csrf_token'] == session["csrf_token"]:
            pass
    return redirect(url_for('lr'))

@app.route("/gallery")
def gallery():
    w2b_context.clear()
    if "user_id" in session:
        user = User.query.filter_by(id=session['user_id']).first()
        w2b_context.update({"user":{"user_id":session['user_id'], "user":user}})
    else:
        w2b_context.update({"user":{"user_id":-1}}) 
    w2b_context.update({"articles":Article.query.all()})
    return render_template("gallery.html", cntxt=w2b_context)

if __name__ == "__main__":
    app.run(debug=True)