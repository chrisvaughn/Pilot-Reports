import os

from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.api import users as google_users
from google.appengine.ext.webapp import template

from model.users import Users
from model.acars import AcarsPosition

TOKEN_LENGTH = 10

class HomeController(webapp.RequestHandler):
    def get(self):
        """ this handler supports http get """
        data = {}
        if google_users.get_current_user():
            google_user = google_users.get_current_user()
            user = db.Query(Users).filter('user_id =', google_user.user_id()).get()
            if user is None:
                token = Users.generate_token(TOKEN_LENGTH)
                user = Users(user_id = google_user.user_id(), email = google_user.email(), token = token)
                db.put(user)

            data['url'] = google_users.create_logout_url(self.request.uri)
            data['user'] = google_users.get_current_user()
            data['user_token'] = user.token
        else:
            data['url'] = google_users.create_login_url(self.request.uri)
        
        path = os.path.join(os.path.dirname(__file__), '../view/home.html')
        self.response.out.write(template.render(path, data))
