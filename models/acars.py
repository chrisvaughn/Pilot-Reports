import logging
import webapp2

from google.appengine.ext import db

from google.appengine.api import users as google_users

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

ONLINE_VATSIM = 1
ONLINE_IVAO = 2
ONLINE_FPI = 3
ONLINE_OTHER = 0


class AcarsPosition(db.Model):
    flight_id = db.StringProperty()
    message_id = db.StringProperty()
    system_time = db.DateTimeProperty(auto_now_add=True)
    remote_time = db.DateTimeProperty()
    message_type = db.StringProperty()
    flight_status = db.IntegerProperty()
    waypoint = db.StringProperty()
    lat_lon = db.GeoPtProperty()
    hdg = db.IntegerProperty()
    alt = db.IntegerProperty()
    vs = db.IntegerProperty()
    gs = db.IntegerProperty()
    ias = db.IntegerProperty()
    tas = db.IntegerProperty()
    fob = db.IntegerProperty()
    wnd = db.StringProperty()
    oat = db.IntegerProperty()
    tat = db.IntegerProperty()
    distance_from_dept = db.IntegerProperty()
    distance_total = db.IntegerProperty()
    pause_mode = db.IntegerProperty()
    airport = db.StringProperty()
    message = db.TextProperty()

    def add_position(self):
        db.put_async(self)


class AcarsFlight(db.Model):
    flight_id = db.StringProperty()
    user_id = db.StringProperty()
    acars_id = db.IntegerProperty()
    aircraft_type = db.StringProperty()
    flight_number = db.StringProperty()
    flight_type = db.StringProperty()
    flight_plan = db.StringListProperty()
    departure = db.StringProperty()
    destination = db.StringProperty()
    
    def add_flight(self):
        db.put_async(self)

    def active_flights_for_user(self, user_id, limit=20, offset=0):
        flights = db.Query(AcarsFlight).filter("user_id =", user_id).fetch(limit, offset)
        active_flights = []
        for flight in flights:
            position = db.Query(AcarsPosition).filter("flight_id =", flight.flight_id).filter("message_type = ", 'ZZ').get()
            if position is None:
                active_flights.append(flight)
        return active_flights
    active_flights_for_user = classmethod(active_flights_for_user)


class AcarsPirep(db.Model):
    time_report = db.DateTimeProperty(auto_now_add=True)
    acars_id = db.IntegerProperty()
    user_id = db.StringProperty()
    flight_number = db.StringProperty()
    ac_icao = db.StringProperty()
    cruise_alt = db.IntegerProperty()
    flight_type = db.StringProperty()
    departure = db.StringProperty()
    destination = db.StringProperty()
    alternate = db.StringProperty()
    dep_time = db.DateTimeProperty()
    block_time = db.IntegerProperty()
    block_fuel = db.IntegerProperty()
    flight_time = db.IntegerProperty()
    flight_fuel = db.IntegerProperty()
    pax = db.IntegerProperty()
    cargo = db.IntegerProperty()
    online = db.IntegerProperty()
    engine_start_ts = db.IntegerProperty()
    takeoff_ts = db.IntegerProperty()
    landing_ts = db.IntegerProperty()
    engine_stop_ts = db.IntegerProperty()
    zero_fuel_weight = db.IntegerProperty()
    take_off_weight = db.IntegerProperty()
    landing_weight = db.IntegerProperty()
    out_geo = db.GeoPtProperty()
    out_altitude = db.IntegerProperty()
    in_geo = db.GeoPtProperty()
    in_altitude = db.IntegerProperty()
    max_climb_rate = db.IntegerProperty()
    max_descend_rate = db.IntegerProperty()
    max_ias = db.IntegerProperty()
    max_gs = db.IntegerProperty()

    def add_pirep(self):
        db.put_async(self)

    def flights_for_user(self, user_id, limit=20, offset=0):
        return db.Query(AcarsPirep).filter("user_id =", user_id).fetch(limit, offset)
    flights_for_user = classmethod(flights_for_user)

class AcarsFlightData(db.Model):
    flight_number = db.StringProperty()
    aircraft = db.StringProperty()
    departure = db.StringProperty()
    destination = db.StringProperty()
    alternate = db.StringProperty()
    route = db.StringProperty()
    altitude = db.StringProperty()
    pax = db.StringProperty()
    cargo = db.StringProperty()
    rules = db.StringProperty()

    def add_flight_data(self):
        db.put_async(self)
