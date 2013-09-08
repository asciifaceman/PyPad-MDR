from flask_wtf import Form
from wtforms import  TextField, TextAreaField, SubmitField, SelectField, PasswordField, BooleanField, validators, ValidationError
from wtforms import HiddenField
from models import db, User
import base64, hashlib, hmac, os, time, struct
from secret_auth import auth_secret

class AddNoteForm(Form):
    title = TextField("Title", [validators.Required("Please enter a title.")])
    description = TextAreaField("Description", [validators.Required("Please enter the note content")])
    category = SelectField('Category', choices=[('Linux', 'Linux'), ('Windows', 'Windows'), ('Uncategorized', 'Uncategorized')])
    noteid = TextField('Note ID') #for note editing
    submit = SubmitField("Create")

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

    def validate(self):
        if not Form.validate(self):
            return False

class AddSnippetForm(Form):
    title = TextField("Title", [validators.Required("Please enter a title")])
    desc = TextAreaField("Description")
    snippet = TextAreaField("Snippet", [validators.Required("Please enter the snippet")])
    category = SelectField('Category', choices=[('Misc', 'Misc')])
    language = SelectField('Language', choices=[('Python', 'Python'), ('Bash', 'Bash'), ('Perl', 'Perl'), ('Ruby', 'Ruby'), ('Powershell', 'Powershell'), ('HTML', 'HTML'), ('CSS', 'CSS'), ('JS', 'JS'), ('PHP', 'PHP')])
    snipid = TextField('Snippet ID') #for snippet editing
    submit = SubmitField("Create")

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

    def validate(self):
        if not Form.validate(self):
            return False

class AddUserForm(Form):
    username = TextField("Username", [validators.Required("Please enter the desired username")])
    email = TextField("Email", [validators.Required("Please enter users email"), validators.Email("Please enter your email address.")])
    password = PasswordField("Password", [validators.Required("Please enter a password")])
    admin = BooleanField("Admin")
    secret = BooleanField("G-auth secret")
    submit = SubmitField("Create Account")

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

    def validate(self):
        if not Form.validate(self):
            return False

        mailadd = User.query.filter_by(email = self.email.data.lower()).first()
        user = User.query.filter_by(username = self.username.data.lower()).first()
        if mailadd:
            self.email.errors.append("This email is already taken.")
            return False
        elif user:
            self.username.errors.append("This username is already taken.")
            return False
        else:
            return True

class LoginForm(Form):
    email = TextField('Email', [validators.Required("Please enter your email"), validators.Email("Please enter your email correctly")])
    password = PasswordField("Password", [validators.Required("Please enter your password")])
    auth = TextField('Auth Token')
    submit = SubmitField("Login")

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

    def validate(self):
        if not Form.validate(self):     
            return False

        user = User.query.filter_by(email = self.email.data.lower()).first()
        # Check password against database
        if user and user.check_password(self.password.data):
            # continue logic
            if user.secret is None:
                return True
            else:
                if auth_secret(user.secret, self.auth.data):
                    return True
                else:
                    self.auth.errors.append("Invalid auth token!")
                    return False


        else:
            self.email.errors.append("Invalid email or password")
            return False








