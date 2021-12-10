import datetime
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy


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
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(1024), nullable=False)
    image = db.Column(db.String(80), nullable=False, default="default_user_image.png")
    last_login = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    articles = db.relationship('Article', backref='user')

    def __repr__(self):
        return '<User %r>' % self.username



@app.route("/")
@app.route("/category/<int:cat_id>")
def index(cat_id=None):
    w2b_context.update({"user":{"user_id":-1}}) #! Add user controll system
    w2b_context.update({"categories":Category.query.all()})
    if cat_id == None :
        w2b_context.update({"articles":Article.query.all()})
    else:
        articles = []
        if Category.query.filter_by(id=cat_id).count() > 0:
            category = Category.query.filter_by(id=cat_id).first()
            for article in Article.query.all():
                if category in article.categories:
                    articles.append(article)
        w2b_context.update({"articles":articles})
        w2b_context.update({"category":cat_id})
    #print(w2b_context)
    return render_template("index.html", cntxt=w2b_context)

@app.route("/post/<id>")
def post(id):
    return render_template("post.html", cntxt=w2b_context)

@app.route("/lr")
def lr():
    return render_template("lr.html", cntxt=w2b_context)

@app.route("/edit")
def edit():
    return render_template("edit.html", cntxt=w2b_context)

if __name__ == "__main__":
    app.run(debug=True)