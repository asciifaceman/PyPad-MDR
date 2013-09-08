from pypad import app
from flask import Flask, render_template, request, flash, redirect, url_for, session
from forms import AddNoteForm, AddUserForm, LoginForm, AddSnippetForm
from models import db, User, Notes, Category, Snippets

import base64, hashlib, hmac, os, time, struct

appName = "PyPAD MDR"

def getQRLink(name, secret):
    return "http://chart.apis.google.com/chart?chs=200x200&chld=M|0&cht=qr&chl=otpauth://totp/{0}%20-%20{1}%3Fsecret%3D{2}".format(name, appName, secret)


@app.route('/')
def home():
    totalsnip = Snippets.query.count()
    totalnote = Notes.query.count()
    totaluser = User.query.count()

    return render_template('home.html', totalsnip=totalsnip, totalnote=totalnote, totaluser=totaluser)

@app.route('/adduser', methods=['GET', 'POST'])
def adduser():
    form = AddUserForm()

    if request.method == 'POST':
        if form.validate() == False:
            return render_template('addUser.html', form=form)
        else:
            #newuser = User('chas', 'chas@charlescorbett.com', 'calico!', admin, secret)
            newuser = User(form.username.data, form.email.data, form.password.data, form.admin.data, form.secret.data)
            db.session.add(newuser)
            db.session.commit()
            flash("User has been added.")
            return redirect(url_for('listusers'))

    elif request.method == 'GET':
        return render_template('addUser.html', form=form)

@app.route('/listusers')
def listusers():
    allusers = User.query.all()

    return render_template('listUsers.html', allusers=allusers)

@app.route('/moduser/<function>/<username>', methods=['POST', 'GET'])
def moduser(function, username):
    if request.method == 'POST':
        return redirect(url_for('listusers'))

    elif request.method == 'GET':
        if function == 'delete':
            flashmessage = "User %s deleted." % username
            flash(flashmessage)
            userID = User.query.filter_by(username = username.lower()).first()
            db.session.delete(userID)
            db.session.commit()
            return redirect(url_for('listusers'))

        elif function == 'admin':
            userID = User.query.filter_by(username = username.lower()).first()
            if userID.id == 1:
                flash("This user cannot be demoted.")
            else:
                if userID.admin is False:
                    userID.admin = True
                elif userID.admin is True:
                    userID.admin = False
                db.session.commit()
                flash("User's admin status has been toggled.")
            return redirect(url_for('listusers'))

        elif function == 'getqr':
            userID = User.query.filter_by(username = username.lower()).first()
            qrMessage = getQRLink(userID.username, userID.secret)
            return redirect(qrMessage)

        elif function == 'gauth':
            flash("G-auth login cannot be toggled at this time.")
            return redirect(url_for('listusers'))

@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()

    if request.method == 'POST':
        if form.validate() == False:
            return render_template('login.html', form=form)
        else:
            session['email'] = form.email.data.lower()
            session['username'] = User.query.filter_by(email = form.email.data.lower()).first().username
            return redirect(url_for('home'))

    elif request.method == 'GET':
        return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    if 'email' not in session:
        return redirect(url_for('signin'))

    session.pop('email', None)
    return redirect(url_for('home'))

@app.route('/testdb')
def testdb():
    if db.session.query("1").from_statement("SELECT 1").all():
        flash("Databasing connect worked. Redirecting...")
        return redirect(url_for('home'))
    else:
        flash("Databasing connect DID NOT WORK. Redirecting...")
        return redirect(url_for('home'))


@app.route('/newsnip', methods=['GET', 'POST'])
def newsnip():
    form = AddSnippetForm()

    if request.method == 'POST':
        if form.validate() == False:
            return render_template('newSnippet.html', form=form)
        else:
            newSnip = Snippets(form.title.data, form.snippet.data, form.desc.data, session['username'], form.category.data, form.language.data)
            db.session.add(newSnip)
            db.session.commit()
            flashmessage = "Note %s added by %s" % (form.title.data, session['username'])
            return redirect(url_for('snippets'))

    elif request.method == 'GET':
        return render_template('newSnippet.html', form=form)


@app.route('/snippets')
def snippets():
    snippets = Snippets.query.all()

    return render_template('snippets.html', snippets=snippets)
 

@app.route('/viewsnip/<int:snip_id>', methods=['POST', 'GET'])
def viewsnip(snip_id):
    snip = Snippets.query.filter_by(id = snip_id).first()
    snipdate = str(snip.pub_date).split(" ")[0]



    return render_template('viewsnip.html', snip=snip, snipdate=snipdate)


@app.route('/modsnip/<function>/<int:snip_id>', methods=['POST', 'GET'])
def modsnip(function, snip_id):
    if request.method == 'POST':
        return redirect(url_for('snippets'))

    elif request.method == 'GET':
        if function == 'delete':
            snip_object = Snippets.query.filter_by(id = snip_id).first()
            flashmessage = "Snippet %s deleted" % snip_object.title
            db.session.delete(snip_object)
            db.session.commit()
            flash(flashmessage)

        return redirect(url_for('snippets'))

@app.route('/editsnip', defaults={'snip_id': None}, methods=['GET', 'POST'])
@app.route('/editsnip/<int:snip_id>', methods=['POST', 'GET'])
def editsnip(snip_id):
    form = AddSnippetForm()
    snip = Snippets.query.filter_by(id = snip_id).first()

    if not snip_id:
        flash("Misdirected to editnote")
        redirect( url_for('snippets'))

    return render_template('editSnippet.html', form=form, snip=snip)

@app.route('/updatesnip', methods=['POST', 'GET'])
def updatesnip():
    form = AddSnippetForm()
    print "Snippet ID: %s" % form.snipid.data
    snip = Snippets.query.filter_by(id = form.snipid.data).first()

    if request.method == 'POST':
        if form.validate() == False:
            return render_template('editsnip.html', form=form, snip=snip)
        else:
            snip.title = form.title.data
            snip.description = form.desc.data
            snip.snippet = form.snippet.data
            snip.category = form.category.data
            snip.lanugage = form.language.data
            flashmessage = "Snippet %s modified by %s" % (snip.title, session['username'])
            db.session.commit()
            return redirect(url_for('snippets'))

    elif request.method == 'GET':
        return redirect(url_for('snippets'))


@app.route('/newnote', methods=['GET', 'POST'])
def newnote():
    form = AddNoteForm()
    
    if request.method == 'POST':
        if form.validate() == False:
            return render_template('newNote.html', form=form)
        else:
            #curuser = session['username']
            
            newNote = Notes(form.title.data, form.description.data, session['username'], form.category.data)
            db.session.add(newNote)
            db.session.commit()
            flashmessage = "Note added by %s" % session['username']
            flash(flashmessage)
            return redirect(url_for('notes'))

    elif request.method == 'GET':
        return render_template('newNote.html', form=form)


@app.route('/editnote', defaults={'post_id': None}, methods=['GET', 'POST'])
@app.route('/editnote/<int:post_id>', methods=['POST', 'GET'])
def editnote(post_id):
    form = AddNoteForm()
    note = Notes.query.filter_by(id = post_id).first()

    if not post_id:
        flash("Misdirected to editnote")
        redirect( url_for('notes'))

    return render_template('editnote.html', form=form, note=note)

@app.route('/updatenote', methods=['POST', 'GET'])
def updatenote():
    form = AddNoteForm()
    print "Note ID: %s" % form.noteid.data
    note = Notes.query.filter_by(id = form.noteid.data).first()
    print note

    if request.method == 'POST':
        if form.validate() == False:
            return render_template('editnote.html', form=form, note=note)
        else:
            note.title = form.title.data
            note.description = form.description.data
            note.category = form.category.data
            flashmessage = "Note %s modified by %s" % (note.title, session['username'])
            db.session.commit()
            return redirect(url_for('notes'))

    elif request.method == 'GET':
        return redirect(url_for('notes'))

@app.route('/viewnote/<int:post_id>', methods=['POST', 'GET'])
def viewnote(post_id):
    note = Notes.query.filter_by(id = post_id).first()
    
    return render_template('viewnote.html', note=note)


@app.route('/modnote/<function>/<int:post_id>', methods=['POST', 'GET'])
def modnote(function, post_id):
    if request.method == 'POST':
        flash("Post request")
        return redirect(url_for('notes'))
    elif request.method == 'GET':
        if function == 'delete':
            note_object = Notes.query.filter_by(id = post_id).first()
            flashmessage = "Note %s: %s deleted" % (post_id, note_object.title)
            db.session.delete(note_object)
            db.session.commit()
            flash(flashmessage)

        return redirect(url_for('notes'))

    return redirect('notes')

@app.route('/notes')
def notes():
    allnotes = Notes.query.all()

    return render_template('notes.html', allnotes=allnotes)
    
if __name__ == '__main__':
    app.run(debug=True)


