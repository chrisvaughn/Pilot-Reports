""" models module contains the App Engine DataStore models """
from google.appengine.ext import db

class Users(db.Model):
    user_id = db.StringProperty()
    email = db.StringProperty()
    token = db.StringProperty()
