from wtforms import Form, StringField, SubmitField, TextAreaField, validators
from flask_wtf.file import FileField, FileRequired


class EditForm(Form): 
    title = StringField("Title", [validators.DataRequired(), validators.Length(min=5, max=80)], render_kw={"class":"form-control","maxlength":"80","minlength":"5"})
    subtitle = StringField("Subtitle", [validators.DataRequired(), validators.Length(min=5, max=80)], render_kw={"class":"form-control","maxlength":"80","minlength":"5"})
    body = TextAreaField("Article Text", [validators.DataRequired(), validators.Length(min=3, max=536870912)], render_kw={"class":"form-control","maxlength":"536870912","minlength":"3", "rows":10})
    image = FileField("Hero Image", validators=[FileRequired()], render_kw={"class":"form-control", "style":"opacity: 0.2;  z-index: -1;"})
    submitbutton = SubmitField("Publish")