import datetime
import time
import os
from werkzeug.utils import secure_filename
from flask import render_template, redirect, url_for, session, request, abort

from core.models.singletons import app, db, bcrypt
from core.models.article import Article
from core.models.category import Category
from core.models.sociallink import SocialLink
from core.models.user import User
from core.models.comment import Comment
from core.models.forms.registration import RegistrationForm
from core.models.forms.login import LoginForm
from core.models.forms.edit import EditForm

from core.helpers.csrf_text import csrf_text
from core.helpers.ext_cont import ext_cont
from core.helpers.form_checker import form_checker


from core.constants.default_article_image import DEFAULT_ARTICLE_IMAGE


w2b_context = {}


def show_message(msg:str):
    session.pop('article_id', None)
    w2b_context.clear()
    if "user_id" in session:
        user = User.query.filter_by(id=session['user_id']).first()
        w2b_context.update({"user":{"user_id":session['user_id'], "user":user}})
    else:
        w2b_context.update({"user":{"user_id":-1}})
    w2b_context.update({"message":msg}) 
    return render_template("message.html", cntxt=w2b_context)



@app.route("/")
@app.route("/category/<int:cat_id>")
def index(cat_id=None):
    w2b_context.clear()
    page = abs(request.args.get("p", 1, int))
    print(type(page), page)
    if "user_id" in session:
        user = User.query.filter_by(id=session['user_id']).first()
        w2b_context.update({"user":{"user_id":session['user_id'], "user":user}})
    else:
        w2b_context.update({"user":{"user_id":-1}}) 
    w2b_context.update({"categories":Category.query.all()})
    if cat_id == None :
        if (page-1)*10 < Article.query.filter(Article.verified>0).count():
            v_articles = Article.query.filter(Article.verified>0).paginate(page, 10, False)
        else:
            v_articles = Article.query.filter(Article.verified>0).paginate(1, 10, False)
        w2b_context.update({"articles":v_articles, "category":-1})
    else:
        articles = []
        if Category.query.filter_by(id=cat_id).count() > 0:
            category = Category.query.filter_by(id=cat_id).first()
            if (page-1)*10 < Article.query.filter(Article.verified>0).filter(Article.categories.contains(category)).count():
                v_articles = Article.query.filter(Article.verified>0).filter(Article.categories.contains(category)).order_by(Article.id).paginate(page, 10, False)
            else:
                v_articles = Article.query.filter(Article.verified>0).filter(Article.categories.contains(category)).order_by(Article.id).paginate(1, 10, False)
        w2b_context.update({"articles":v_articles, "category":cat_id})
    return render_template("index.html", cntxt=w2b_context)

@app.route("/post/<int:id>", methods=['GET', 'POST'])
def post(id=None):
    if id == None:
        return redirect(url_for('index'))
    article = Article.query.filter_by(id=id).first()
    if request.method == "POST" and  request.form['csrf_token'] == session["csrf_token"]:
        if "user_id" in session:
            user = User.query.filter_by(id=session['user_id']).first()
            if request.form['form_name'] == "delete_article":
                if user.usertype < 5 and article.user.id != user.id:
                    return show_message(msg="You are not allowed to do this.")
                for com in Comment.query.filter_by(article_id=id):
                    db.session.delete(com)
                if article.image != DEFAULT_ARTICLE_IMAGE:
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], article.image))
                db.session.delete(article)
                db.session.commit()
                return redirect(url_for('user'))
            if request.form['form_name'] == "verify_article":
                if user.usertype < 5:
                    return show_message(msg="You are not allowed to do this.")
                else:
                    if article.verified < 0:
                        article.verified = user.id 
                        db.session.commit()
                return redirect(url_for('user'))
        else:
            return show_message(msg="Login required!")
    if request.method == "GET":
        w2b_context.clear()
        if "user_id" in session:
            csrf_token = csrf_text()
            session["csrf_token"] = csrf_token
            user = User.query.filter_by(id=session['user_id']).first()
            w2b_context.update({"user":{"user_id":session['user_id'], "user":user}, 'csrf_token':csrf_token})
        else:
            w2b_context.update({"user":{"user_id":-1}}) 
        if article.verified < 0:
            return show_message(msg="This article no verified")
        w2b_context.update({"article":article})
        return render_template("post.html", cntxt=w2b_context)

@app.route('/comment/<int:p_id>', methods=['POST',])
def cmnt(p_id: int):
    if request.method == "POST" and  request.form['csrf_token'] == session["csrf_token"]:
        if "user_id" in session:
            user = User.query.filter_by(id=session['user_id']).first()
            article = Article.query.filter_by(id=p_id).first()
            if article:
                if "new_comment_body" in request.form and len(request.form['new_comment_body']) > 0:
                    comment = Comment(body=request.form['new_comment_body'])
                    article.comments.append(comment)
                    user.comments.append(comment)
                    db.session.add(comment)
                    db.session.commit()
                    return redirect(url_for('post', id=p_id))
            else:
                return show_message(msg="This article not exists!")
        else:
            return show_message(msg="Login required!")

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
                if bcrypt.check_password_hash(us.password.encode('utf-8'), user_pass):
                    session['user_id'] = us.id
                    us.last_login = datetime.datetime.utcnow()
                    db.session.commit()
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
                        user_pass = bcrypt.generate_password_hash(user_pass).decode("utf-8")
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
                if article.user.id == session['user_id']:
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
                if not os.path.exists(app.config['UPLOAD_FOLDER']):
                    os.mkdir(os.path.join(app.config['UPLOAD_FOLDER']))
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], file_name))
            session.pop('article_id', None)
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
            if user.usertype == 5 and Article.query.filter_by(verified=-1).count() > 0:
                w2b_context.update({"v_articles":Article.query.filter_by(verified=-1)})
            else:
                w2b_context.update({"v_articles":[]})
            return render_template("user.html", cntxt=w2b_context)
        if request.method == "POST" and  request.form['csrf_token'] == session["csrf_token"]:
            if "form_name" in request.form and len(request.form['form_name']) > 0:
                if request.form['form_name'] == 'change_picture':
                    image = request.files["new_avatar"]
                    if image.filename != '':
                        if image and ext_cont(image.filename):
                            file_name = secure_filename(image.filename)
                            file_name = "{}-{}".format(datetime.datetime.strftime(datetime.datetime.utcnow(), "%s"),file_name)
                            user.image = file_name
                            db.session.commit()
                            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                                os.mkdir(os.path.join(app.config['UPLOAD_FOLDER']))
                            image.save(os.path.join(app.config['UPLOAD_FOLDER'], file_name))
                        else:
                            return  show_message(msg="This file format is not supported.")
                    else:
                        return  show_message(msg="Filename cannot be empty!")
                if request.form['form_name'] == "change_about_me":
                    if "about_me" in request.form:
                        about_me = request.form['about_me']
                        user.about_me = about_me
                        db.session.commit()
                if request.form['form_name'] == "add_social":
                    if "form_name_desc" in request.form and len(request.form['form_name_desc']) > 0:
                        if "link_url" in request.form and len(request.form['link_url']) > 0:
                            sname = request.form['form_name_desc']
                            slink = request.form['link_url']
                            social = SocialLink(sname=sname, slink=slink)
                            user.sociallinks.append(social)
                            db.session.add(social)
                            db.session.commit()
                        else:
                            return  show_message(msg="Your social network address is wrong.")
                    else:
                        return  show_message(msg="Something went wrong. Try again.")
                if request.form['form_name'] == "add_category":
                    if "new_category" in request.form and len(request.form['new_category']) > 0:
                        new_name = request.form['new_category']
                        c = Category.query.filter_by(name=new_name).first() ;print(c)
                        if c:
                            return  show_message(msg="This category already exists.")
                        else:
                            category = Category(name=new_name) ;print(category)
                            db.session.add(category)
                            db.session.commit()
                if request.form['form_name'] == "delete_category" and user.usertype == 5:
                    if "form_name_desc" in request.form and len(request.form['form_name_desc']) > 0:
                        c_name = request.form['form_name_desc']
                        c = Category.query.filter_by(name=c_name).first() ;print(c)
                        if c:
                            for article in Article.query.all():
                                if c in article.categories:
                                    article.categories.remove(c)
                            db.session.delete(c)
                            db.session.commit()
                        else:
                            return  show_message(msg="This category not found.")
        return redirect(url_for('index'))
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