from wtforms import Form, BooleanField, StringField, PasswordField, EmailField, SubmitField, validators


class RegistrationForm(Form):
    fullname = StringField('Full Name', [validators.DataRequired(), validators.Length(min=5, max=35)], render_kw={"class":"form-control","maxlength":"35","minlength":"6"})
    username = StringField('User Name', [validators.DataRequired(), validators.Length(min=4, max=25)], render_kw={"class":"form-control","maxlength":"25","minlength":"4"})
    email = EmailField('Email address', [validators.DataRequired(), validators.Length(min=8, max=35), validators.Email(message=(u'That\'s not a valid email address.'))], render_kw={"class":"form-control","maxlength":"35","minlength":"8"})
    password = PasswordField('Password', [validators.DataRequired(), validators.Length(min=10, max=35), validators.EqualTo('confirm', message='Passwords must match')], render_kw={"class":"form-control","maxlength":"35","minlength":"10"})
    confirm = PasswordField('Repeat Password', [validators.DataRequired()], render_kw={"class":"form-control"})
    iagree = BooleanField(" I have read and agree to the terms ", render_kw={"class":"form-check-input","checked":"checked","value":"1"})
    submitbutton = SubmitField("Register")
