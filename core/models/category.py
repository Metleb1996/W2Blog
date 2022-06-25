from .singletons import db
from .article_categories import article_categories

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25), unique=True, nullable=False)
    articles = db.relationship("Article", secondary=article_categories, back_populates="categories")

    def __repr__(self):
        return '<Category %r>' % self.name
