import datetime
from .singletons import db
from .article_categories import article_categories

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    verified = db.Column(db.Integer, default=-1) # approved by {admin.id}
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