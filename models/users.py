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
    
    def test_pilot_id(cls, id):
        user = db.Query(Users).filter("email =", id).get()
        if user is None:
            return -1
        else:
            return user.user_id
    test_pilot_id = classmethod(test_pilot_id)

    def test_user_login(cls, id, pw):
        user = db.Query(Users).filter("email =", id).filter("token =", pw).get()
        if user is None:
            return None
        else:
            return user.user_id
    test_user_login = classmethod(test_user_login)
