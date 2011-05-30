import uuid

from google.appengine.ext import db

class Users(db.Model):
    user_id = db.StringProperty()
    email = db.StringProperty()
    token = db.StringProperty()
    
    def generate_token(cls, token_length):
        u = uuid.uuid4()
        return u.bytes.encode("base64")[:token_length]
    generate_token = classmethod(generate_token) 