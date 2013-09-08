from flask import Flask

app = Flask(__name__)
app.secret_key = 'development key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'

from models import db
db.app = app 
db.init_app(app)

from models import Zone, User, Notes, Category, Snippets

#newuser = User('chas', 'chas@charlescorbett.com', 'calico!', True)