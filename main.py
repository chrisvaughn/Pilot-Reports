from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

from controllers.home import HomeController
from controllers.acars import LiveAcarsController

def main():
    application = webapp.WSGIApplication([('/', HomeController), ('/liveacars', LiveAcarsController)],
                                         debug=True)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()
