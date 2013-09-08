from flask.ext.sqlalchemy import SQLAlchemy
from werkzeug import generate_password_hash, check_password_hash
from datetime import datetime,tzinfo,timedelta
import base64, os

from flask import Flask
app = Flask(__name__)
app.secret_key = 'development key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'

db = SQLAlchemy()

db.app = app
db.init_app(app)

class Zone(tzinfo):
    def __init__(self,offset,isdst,name):
        self.offset = offset
        self.isdst = isdst
        self.name = name
    def utcoffset(self, dt):
        return timedelta(hours=self.offset) + self.dst(dt)
    def dst(self, dt):
            return timedelta(hours=1) if self.isdst else timedelta(0)
    def tzname(self,dt):
         return self.name

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)
    admin = db.Column(db.Boolean(), unique=False, default=False)
    secret = db.Column(db.Integer(16), unique=True)
    pwdhash = db.Column(db.String(54))

    def __init__(self, username, email, password, admin=False, issecret=False):
        self.username = username.title().lower()
        self.email = email.lower()
        self.set_password(password)
        if admin is True:
            self.admin = True
        else:
            self.admin = False
        if issecret is True:
            self.new_secret()
        else:
            self.secret = None

        print "Console Secret log: %s" % self.secret 

    def set_password(self, password):
        self.pwdhash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.pwdhash, password)

    def new_secret(self):
        self.secret = base64.b32encode(os.urandom(10))

    def __repr__(self):
        return '<User %r>' % self.username

class Snippets(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    snippet = db.Column(db.UnicodeText())
    description = db.Column(db.UnicodeText())
    pub_date = db.Column(db.DateTime)
    author = db.Column(db.String(80))
    category = db.Column(db.String(80))
    language = db.Column(db.String(80))

    def __init__(self, title, snippet, description, author, category, language, pub_date=None):
        self.title = title
        self.snippet = snippet
        self.description = description
        self.author = author
        if pub_date is None:
            EST = Zone(-5,False,'EST')
            pub_date = datetime.now(EST)
        self.pub_date = pub_date
        self.category = category
        self.language = language

    def __repr__(self):
        return '<Snippet: %r>' % self.title

class Notes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    description = db.Column(db.UnicodeText())
    pub_date = db.Column(db.DateTime)
    author = db.Column(db.String(80))

    category = db.Column(db.String(80))

    def __init__(self, title, description, author, category, pub_date=None):
        self.title = title
        self.description = description
        if pub_date is None:
            EST = Zone(-5,False,'EST')
            pub_date = datetime.now(EST)
        self.author = author
        self.pub_date = pub_date
        self.category = category

    def __repr__(self):
        return '<Post %r>' % self.title

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Category %r>' % self.name

class ToDo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    description = db.Column(db.UnicodeText())
    priority = db.Column(db.String(20))

    def __init__(self, name, description, priority):
        self.name = name
        self.description = description
        self.priority = priority

    def __repr__(self):
        return '<ToDo: %r>' % self.name









