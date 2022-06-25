from .singletons import db

class SocialLink(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sname = db.Column(db.String(25), nullable=False)
    slink = db.Column(db.String(150), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<SocialLink %r>' % self.sname
