import logging
import webapp2

from google.appengine.ext.ndb import model

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


class AcarsPosition(model.Model):
    flight_id = model.StringProperty()
    message_id = model.StringProperty()
    system_time = model.DateTimeProperty(auto_now_add=True)
    remote_time = model.DateTimeProperty()
    message_type = model.StringProperty()
    flight_status = model.IntegerProperty()
    waypoint = model.StringProperty()
    lat_lon = model.GeoPtProperty()
    hdg = model.IntegerProperty()
    alt = model.IntegerProperty()
    vs = model.IntegerProperty()
    gs = model.IntegerProperty()
    ias = model.IntegerProperty()
    tas = model.IntegerProperty()
    fob = model.IntegerProperty()
    wnd = model.StringProperty()
    oat = model.IntegerProperty()
    tat = model.IntegerProperty()
    distance_from_dept = model.IntegerProperty()
    distance_total = model.IntegerProperty()
    pause_mode = model.IntegerProperty()
    airport = model.StringProperty()
    message = model.TextProperty()

    def add_position(self):
        self.put_async()
        if self.lat_lon:
            acars_flight = AcarsFlight.query(AcarsFlight.flight_id == self.flight_id).get()
            flight_position = FlightPosition(lat_lon = self.lat_lon, altitude = self.alt)
            acars_flight.flight_path.append(flight_position)
            acars_flight.put_async()



class FlightPosition(model.Model):
    lat_lon = model.GeoPtProperty()
    altitude = model.IntegerProperty()

class AcarsFlight(model.Model):
    flight_id = model.StringProperty()
    user_id = model.StringProperty()
    acars_id = model.IntegerProperty()
    aircraft_type = model.StringProperty()
    flight_number = model.StringProperty()
    flight_type = model.StringProperty()
    flight_plan = model.StringProperty(repeated=True)
    departure = model.StringProperty()
    destination = model.StringProperty()
    flight_path = model.LocalStructuredProperty(FlightPosition, repeated=True)
    
    def add_flight(self):
        self.put()

    def active_flights_for_user(self, user_id, limit=20, offset=0):
        flights = AcarsFlight.query(AcarsFlight.user_id == user_id).fetch(limit, offset=offset)
        active_flights = []
        for flight in flights:
            position = AcarsPosition.query(AcarsPosition.flight_id == flight.flight_id, AcarsPosition.message_type == 'ZZ').get()
            if position is None:
                active_flights.append(flight)
        return active_flights
    active_flights_for_user = classmethod(active_flights_for_user)



class AcarsPirep(model.Model):
    time_report = model.DateTimeProperty(auto_now_add=True)
    acars_id = model.IntegerProperty()
    user_id = model.StringProperty()
    flight_number = model.StringProperty()
    ac_icao = model.StringProperty()
    cruise_alt = model.IntegerProperty()
    flight_type = model.StringProperty()
    departure = model.StringProperty()
    destination = model.StringProperty()
    alternate = model.StringProperty()
    dep_time = model.DateTimeProperty()
    block_time = model.IntegerProperty()
    block_fuel = model.IntegerProperty()
    flight_time = model.IntegerProperty()
    flight_fuel = model.IntegerProperty()
    pax = model.IntegerProperty()
    cargo = model.IntegerProperty()
    online = model.IntegerProperty()
    engine_start_ts = model.IntegerProperty()
    takeoff_ts = model.IntegerProperty()
    landing_ts = model.IntegerProperty()
    engine_stop_ts = model.IntegerProperty()
    zero_fuel_weight = model.IntegerProperty()
    take_off_weight = model.IntegerProperty()
    landing_weight = model.IntegerProperty()
    out_geo = model.GeoPtProperty()
    out_altitude = model.IntegerProperty()
    in_geo = model.GeoPtProperty()
    in_altitude = model.IntegerProperty()
    max_climb_rate = model.IntegerProperty()
    max_descend_rate = model.IntegerProperty()
    max_ias = model.IntegerProperty()
    max_gs = model.IntegerProperty()

    def add_pirep(self):
        self.put_async()

    def flights_for_user(self, user_id, limit=20, offset=0):
        return AcarsPirep.query(AcarsPirep.user_id == user_id).fetch(limit, offset=offset)
    flights_for_user = classmethod(flights_for_user)

class AcarsFlightData(model.Model):
    flight_number = model.StringProperty()
    aircraft = model.StringProperty()
    departure = model.StringProperty()
    destination = model.StringProperty()
    alternate = model.StringProperty()
    route = model.StringProperty()
    altitude = model.StringProperty()
    pax = model.StringProperty()
    cargo = model.StringProperty()
    rules = model.StringProperty()

    def add_flight_data(self):
        self.put_async()
