from app import *

db.create_all()

c1 = Category(name="C1")
c2 = Category(name="C2")
c3 = Category(name="C3")

a1 = Article(title="A1", subtitle="A1 sub", body="A1 body")
a2 = Article(title="A2", subtitle="A2 sub", body="A2 body")
a3 = Article(title="A3", subtitle="A3 sub", body="A3 body")
a4 = Article(title="A4", subtitle="A4 sub", body="A4 body")
a5 = Article(title="A5", subtitle="A5 sub", body="A5 body")
a6 = Article(title="A6", subtitle="A6 sub", body="A6 body")

u0 = User(username="admin", fullname="Metleb Rustemov (admin)", email="admin@w2blog.com", password="1234567890", usertype=5)
u1 = User(username="metleb", fullname="Metleb Rustemov", email="metleb@w2blog.com", password="1234567890")
u2 = User(username="ali", fullname="Ali Mammadov", email="ali@w2blog.com", password="1234567890")

s1 = SocialLink(sname="facebook", slink="https://facebook.com")
s2 = SocialLink(sname="twitter", slink="https://twitter.com")
s3 = SocialLink(sname="linkedin", slink="https://linkedin.com")
s4 = SocialLink(sname="instagram", slink="https://instagram.com")
s5 = SocialLink(sname="github", slink="https://github.com")

com1 = Comment(body="COM-1")
com2 = Comment(body="COM-2")
com3 = Comment(body="COM-3")
com4 = Comment(body="COM-4")
com5 = Comment(body="COM-5")
com6 = Comment(body="COM-6")
com7 = Comment(body="COM-7")
com8 = Comment(body="COM-8")
com9 = Comment(body="COM-9")
com10 = Comment(body="COM-10")

a1.categories.append(c1)
a1.categories.append(c2)
a1.categories.append(c3)
a2.categories.append(c2)
a3.categories.append(c3)
a4.categories.append(c1)
a5.categories.append(c2)
a6.categories.append(c3)

a1.comments.append(com1)
a2.comments.append(com2)
a2.comments.append(com3)
a3.comments.append(com4)
a4.comments.append(com5)
a4.comments.append(com6)
a4.comments.append(com7)
a5.comments.append(com8)
a6.comments.append(com9)
a6.comments.append(com10)

u1.articles.append(a1)
u1.articles.append(a2)
u2.articles.append(a3)
u1.articles.append(a4)
u1.articles.append(a5)
u2.articles.append(a6)

u1.comments.append(com1)
u2.comments.append(com2)
u1.comments.append(com3)
u2.comments.append(com4)
u1.comments.append(com5)
u2.comments.append(com6)
u1.comments.append(com7)
u2.comments.append(com8)
u1.comments.append(com9)
u2.comments.append(com10)

u0.sociallinks.append(s1)
u1.sociallinks.append(s2)
u1.sociallinks.append(s3)
u2.sociallinks.append(s4)
u2.sociallinks.append(s5)

db.session.add(c1)
db.session.add(c2)
db.session.add(c3)
db.session.add(a1)
db.session.add(a2)
db.session.add(a3)
db.session.add(a4)
db.session.add(a5)
db.session.add(a6)
db.session.add(u0)
db.session.add(u1)
db.session.add(u2)
db.session.add(s1)
db.session.add(s2)
db.session.add(s3)
db.session.add(s4)
db.session.add(s5)

for i in range(100):
    arct = Article(title="Article - {}".format(i), subtitle="Subtitle - {}".format(i), body="Article - {} body text".format(i), verified=2)
    u0.articles.append(arct)
    if i % 2 == 0:
        arct.categories.append(c1)
    if i % 3 == 0:
        arct.categories.append(c2)
    if i % 5 == 0:
        arct.categories.append(c3)
    db.session.add(arct)


db.session.commit()