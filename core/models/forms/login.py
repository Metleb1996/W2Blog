from wtforms import Form, BooleanField, PasswordField, EmailField, SubmitField, validators


class LoginForm(Form):
    email = EmailField('Email address', [validators.DataRequired(), validators.Length(min=8, max=35), validators.Email(message=(u'That\'s not a valid email address.'))], render_kw={"class":"form-control","maxlength":"35","minlength":"8"})
    password = PasswordField('Password', [validators.DataRequired(), validators.Length(min=10, max=35)], render_kw={"class":"form-control","maxlength":"35","minlength":"10"})
    rememberme = BooleanField(" Remember me ", render_kw={"class":"form-check-input","checked":"checked","value":"1"})
    submitbutton = SubmitField("Login")
