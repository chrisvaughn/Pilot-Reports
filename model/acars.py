import os
import logging

from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.api import users as google_users
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template

ACARS_UNKNOWN = -1
ACARS_XACARS = 3
ACARS_XACARS_MSFS = 4
    
FLIGHTSTATUS_BOARDING = 1
FLIGHTSTATUS_TAXIOUT = 2
FLIGHTSTATUS_DEPARTURE = 3
FLIGHTSTATUS_CLIMB = 4
FLIGHTSTATUS_CRUISE = 5
FLIGHTSTATUS_DESC = 6
FLIGHTSTATUS_APPROACH = 7
FLIGHTSTATUS_LANDED = 8
FLIGHTSTATUS_TAXIIN = 9
FLIGHTSTATUS_IN = 10
FLIGHTSTATUS_END = 10
FLIGHTSTATUS_UNKNOWN = 0
FLIGHTSTATUS_CRASH = 99

VSPEED_CRZ = 0
VSPEED_GND = 0
VSPEED_CLB = +1
VSPEED_DES = -1


class AcarsPosition(db.Model):
    flight_id = db.StringProperty()
    message_id = db.StringProperty()
    system_time = db.DateTimeProperty(auto_now_add=True)
    remote_time = db.DateTimeProperty()
    message_type = db.StringProperty()
    flight_status = db.IntegerProperty()
    lat_lon = db.GeoPtProperty()
    heading = db.IntegerProperty()
    altitude = db.FloatProperty()
    vs = db.FloatProperty()
    gs = db.FloatProperty()
    ias = db.FloatProperty()
    tas = db.FloatProperty()
    fob = db.FloatProperty()
    wnd = db.StringProperty()
    oat = db.FloatProperty()
    tat = db.FloatProperty()
    distance_from_dept = db.FloatProperty()
    distance_total = db.FloatProperty()
    pause_mode = db.IntegerProperty()
    message = db.TextProperty()

    def add_position(self):
        db.put(self)
        af = db.Query(AcarsFlight).filter('flight_id =', self.flight_id).get()
        af.currentPositionKey = self.key()
        db.put(af)


class AcarsFlight(db.Model):
    flight_id = db.StringProperty()
    user_id = db.StringProperty()
    acars_id = db.StringProperty()
    aircraft_type = db.StringProperty()
    flight_number = db.StringProperty()
    flight_type = db.StringProperty()
    flight_plan = db.StringListProperty()
    departure = db.StringProperty()
    destination = db.StringProperty()
    currentPositionKey = db.ReferenceProperty(AcarsPosition)
    
    def add_flight(self):
        db.put(self)
