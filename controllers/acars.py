import os
import sys
import logging
import time

from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.api import users as google_users
from google.appengine.ext.webapp import template

from models.users import Users
from models.acars import *

def check_XAcars_version(DATA1):
    if (DATA1 == 'XACARS|1.0' or DATA1 == 'XACARS|1.1' or DATA1 == 'XACARS|2.0' or
        DATA1 == 'XACARS|2.5' or DATA1 == 'XACARS|3.0'):
        return ACARS_XACARS
    elif( DATA1 == 'XACARS_MSFS|1.0' or DATA1 == 'XACARS_MSFS|1.1' or 
        DATA1 == 'XACARS_MSFS|2.0' or DATA1 == 'XACARS_MSFS|2.5' or 
        DATA1 == 'XACARS_MSFS|3.0'):
        return ACARS_XACARS_MSFS
    else:
        return ACARS_UNKNOWN

def lbs2kg( lbs ):
    return  lbs / 2.204622915

def lat_degdecmin_2_decdeg(data):
    
    if data is None:
        return 0
    
    i = 0
    j = data.find(' ', 0)
    k = max(data.find('.', j), j+1)
    
    dec = data[1:j+1]
    dec += data[j+1:k-j+2] / 60
    
    if data[0] == 'S':
        dec = -dec;
        
    return round(dec,4)

def lon_degdecmin_2_decdeg(data):
    
    if data is None:
        return 0
    
    i = 0;
    j = data.find(' ', 0)
    k = max( data.find('.', j), j+1)
    
    dec = data[1:j+1]
    dec += data[j+1:k-j+2] / 60
    
    if data[0] == 'W':
        dec = -dec
    
    return round(dec,4)


class LiveAcarsController(webapp.RequestHandler):
    def post(self):
        self.get()
        
    def get(self):

        data1 = self.request.get('DATA1')
        data2 = self.request.get('DATA2')
        data3 = self.request.get('DATA3')
        data4 = self.request.get('DATA4')
             
        if data1 == '':
            self.response.out.write('0|Invalid Data1')
            return
 
        if data2 == '':
            self.response.out.write('0|Invalid Data2')
            return
        
        version = check_XAcars_version(data1)
        if version == ACARS_UNKNOWN:
            self.response.out.write('0|Invalid XAcars Version')
            return
        
        logging.debug('?DATA1='+data1+'&DATA2='+data2+'&DATA3='+data3+'&DATA4='+data4)

        data2 = data2.replace("\'", "''")
        
        if data3 != '':
            data3 = data3.replace("\'", "''")
        if data4 != '':
            data4 = data4.replace("\'", "''")

        commands = ({'TEST': self.test_cmd, 'BEGINFLIGHT': self.beginflight_cmd, 
                    'MESSAGE': self.message_cmd, 'PAUSEFLIGHT': self.pauseflight_cmd, 
                    'ENDFLIGH': self.endflight_cmd })
        
        commands.get(data2, self.unknown_cmd)(version, data3, data4)
        
    def test_cmd(self, version, data3, data4):
        if Users.test_pilot_id(data3) > 0:
            self.response.out.write('1')
        else:
            self.response.out.write('0|Unknown PilotID '+data3)
    
    def beginflight_cmd(self, version, data3, data4):
        ''' Begin Flight logging on ACARS '''
        data = data3.split("|")
        
        if len(data) < 16:
            self.response.out.write('0|Invalid login data ('+ str(len(data)) +')')
            return
        
        uid = Users.test_user_login(data[0], data[17]);
        if uid is None:
            self.response.out.write('0|Login failed')
            return
        
        acars_flight = AcarsFlight();
        acars_flight.flight_id = str(time.time()).replace('.', '')
        acars_flight.user_id = uid;
        acars_flight.acars_id  = version;

        # *** Origin and Destination Airports
        if len(data[5]) != 0:
            plan = data[5].split('~')
            acars_flight.departure = plan[0].upper()
            if len(plan) > 1:
                acars_flight.destination = plan[-1].upper()
        
        acars_flight.aircraft_type = data[3]  #AircraftRegistration
        acars_flight.flight_type = data[15] #flightType
        acars_flight.flight_plan = plan  #flightPlan
        acars_flight.flight_number = data[2]  #FlightNumber

        db.put(acars_flight)

        self.response.out.write('1|'+acars_flight.flight_id)
    
    def message_cmd(self, version, data3, data4):
        pass
    
    def pauseflight_cmd(self, version, data3, data4):
        self.response.out.write('1|');
    
    def endflight_cmd(self, version, data3, data4):
        pass
    
    def unknown_cmd(self, version, data3, data4):
        self.response.out.write('0|Wrong Function')
        
