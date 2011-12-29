import os
import webapp2
import jinja2

from google.appengine.ext import db
from google.appengine.api import users as google_users

from models.users import Users
from models.acars import AcarsFlightData

TOKEN_LENGTH = 10
jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), '../views')))

class HomeController(webapp2.RequestHandler):
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
            data['user'] = user
        else:
            data['url'] = google_users.create_login_url(self.request.uri)
        
        template = jinja_environment.get_template('home.html')
        self.response.out.write(template.render(data))

class FlightDatabaseController(webapp2.RequestHandler):


    def get(self):
        flight_data = AcarsFlightData()
        flight_data.flight_number = 'EA1492'
        flight_data.aircraft = 'B737'
        flight_data.departure = 'PANC'
        flight_data.destination = 'PAKT'
        flight_data.alternate = 'PJNU'
        flight_data.route = 'ANC4 JOH J501 YAK J541 SSR J502 DOOZI'
        flight_data.altitude = 'FL30'
        flight_data.pax = '15'
        flight_data.cargo = '2000'
        flight_data.rules = 'IFR'

        flight_data.add_flight_data()
