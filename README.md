PyPad-MDR
=========

Python-Flask based Micro Documentation Repository

This is not meant to be an open-access webapp, this is meant to be used in a confined network amongst peers
or colleages (such as an internal repo or wiki). I have not hardened it nearly enough for wide-spread use,
and I do not feel like writing adanced user controls yet either (signup/bot blocking/etc).

I might do this in the future, but not right now.

=============================================
== Set Up | Dependencies

Starter database should be moved to /tmp/test.db for the time being.
virtualenvironment with python 2.7.*

pip installations:

*Flask (0.10.1)
*Flask-SQLAlchemy (1.0)
*Flask-WTF (0.9.1)
*SQLAlchemy (0.8.2)
*WTForms (1.0.4)


Included dependencies(non-python):
*Jquery/Jquery-ui
*prettify (https://code.google.com/p/google-code-prettify/)
*TinyMCE
=============================================
== Initial Run (if new user, and not me)

I would recommend deleting test.db initially
I do not have a back-end db control script just yet, getting around to it.
For now, do this from command line:

python

import db_cmd

from models import db, User

new = User('username', 'email', 'password', admin=True, issecret=True) # issecret=False if you can't use g-auth

 #Collect the secret auth key (if you opted for it) and enter it into your g-auth app
 
db.session.add(new)

db.sessin.commit()

exit()

 #This should get you started enough to start the app and log in to generate new content

=============================================
== Huge TODO list

* Password reset / auth reset / account recovery (might leave out since it should be done by the admin)
* captcha-secured signup (might leave this out, see top of file)
* IP logging (stores IP that posted content, if not admin account, rate-limits)
* Improve admin interface / add user profiles
* maybe do embedded or locally-stored images in notes
* HowTos
* ToDo list
* Make even more pretty!
* decide if I am keeping the pretty input textarea boxes
* Clean up static/
* clean up main.css
* split up main.css?
* play with mysql vs. sqlite3
* sort lists of notes/snippets by category/date/author (might take awhile)



