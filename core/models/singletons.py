from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

app = Flask(__name__, template_folder="../../templates", static_folder="../../static")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vt.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['UPLOAD_FOLDER'] = "{}/static/media".format(app.root_path)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024 #uploaded file max size
app.secret_key = b'HbfGMYwEOnP3oVEbbnPuoYxx1FHPdLSoNKku3qmKfWUjt6tsLdm3USo5k7JRWmXNiGIjpyXtm7DZ1DbAYAzn0g8LmerBW1DsaeSf'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)