import webapp2

from controllers.home import *
from controllers.acars import *

app = webapp2.WSGIApplication([('/', HomeController),
							   ('/flight_db', FlightDatabaseController),
                               ('/liveacars', LiveAcarsController),
                               ('/pirep', PirepController),
                               ('/flightdata', FlightDataController)],
								debug=True)