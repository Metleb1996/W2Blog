from .singletons import db

article_categories = db.Table(
    "article_categories",
    db.Column("article_id", db.Integer, db.ForeignKey("article.id")),
    db.Column("category_id", db.Integer, db.ForeignKey("category.id")),
)