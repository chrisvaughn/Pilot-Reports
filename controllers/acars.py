import os
import sys
import logging
import time
import datetime

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
    return  float(lbs) / 2.204622915

#N52 23.1890 
def lat_degdecmin_2_decdeg(p1, p2):
    
    if p1 is None:
        return 0
    
    dec = float(p1[1:])
    dec += float(p2) / 60
    
    if p1[0] == 'S':
        dec = -dec;
        
    return round(dec,4)

#E13 31.0944
def lon_degdecmin_2_decdeg(p1, p2):
    
    if p1 is None:
        return 0
        
    dec = float(p1[1:])
    dec += float(p2) / 60
    
    if p1[0] == 'W':
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

        acars_position = AcarsPosition();
        acars_position.flight_id = acars_flight.flight_id
        acars_position.message_type = 'PR'
        
        if data[6] != '':
            #N52 23.1890 E13 31.0944
            parts = data[6].split(' ');

            posLat = lat_degdecmin_2_decdeg(parts[0].strip(), parts[1].strip())
            posLon = lon_degdecmin_2_decdeg(parts[2].strip(), parts[3].strip())
            
            acars_position.lat_lon = db.GeoPt(posLat, posLon)
        
        acars_position.flight_status = FLIGHTSTATUS_BOARDING;
        acars_position.waypoint = acars_flight.departure;
        acars_position.hdg = int(data[12])
        acars_position.alt = int(data[7])
        acars_position.wnd = data[13]
        acars_position.oat = int(data[14])
        acars_position.tat = int(data[14])
        acars_position.fob = lbs2kg(data[11])
        acars_position.distance_total = int(data[16])
        acars_position.message = db.Text(data3)
        
        db.put(acars_position)
        acars_position.add_position()
        
        self.response.out.write('1|'+acars_flight.flight_id)
    
    def message_cmd(self, version, data3, data4):
        acars_position = AcarsPosition()

        acars_position.flight_id = data3
        acars_position.message = db.Text(data4)
        
        #Decode the message
        #Messagetype: PR=Position Report, AR=Alitude Report, WX=Weather,
        #           QA=OUT, QB=OFF, QC=ON, QD=IN, QM=Flight Statistics, CM=User Message
        j = data4.find('Msg Label: ', 0)
        if j != -1:
            j = j + len('Msg Label: ')
            acars_position.message_type = data4[j:j+2]
        else:
            self.response.out.write('ERROR - Wrong Message format: Msg Label is missing')
            return
        
        #Remote Timestamp auslesen  01/17/2006 06:58Z
        time = datetime.datetime.strptime(data4[1:18], "%m/%d/%Y %H:%MZ")
        acars_position.remote_time = time
        
        j = data4.find('Message:', 0)
         
        if j == -1:
            self.response.out.write('ERROR - Wrong Message format: Messagebody is missing')
            return
        
        j = j + len('Message:')
        data = data4[j:].split('/')
        
        for cmd_str in data:
            k = cmd_str.find(' ')
            cmd = cmd_str[0:k].upper()
            cnt = cmd_str[k:].strip()

            if cmd == 'POS':
                parts = cnt.split(' ');
                posLat = lat_degdecmin_2_decdeg(parts[0].strip(), parts[1].strip())
                posLon = lon_degdecmin_2_decdeg(parts[2].strip(), parts[3].strip())
                acars_position.lat_lon = db.GeoPt(posLat, posLon)
                i = cnt.find('[')
                if i != -1:
                    acars_position.waypoint = cnt[i+1:-1]

            if cmd == 'HDG':
                acars_position.hdg = int(cnt)
            
            if cmd == 'ALT':
                i = cnt.find(' ')
                if i == -1:
                    acars_position.alt = int(cnt)
                else:
                    acars_position.alt = int(cnt[0:i])
                    if cnt.find('CLIMB') != -1:
                        acars_position.vs = VSPEED_CLB
                    elif cnt.find('DESC' ) != -1:
                        acars_position.vs = VSPEED_DES
                    elif cnt.find('LEVEL') != -1:
                        acars_position.vs = VSPEED_CRZ

            if cmd == 'IAS':
                acars_position.ias = int(cnt)
            
            if cmd == 'TAS':
                acars_position.tas = int(cnt)
                
            if cmd == 'OAT':
                acars_position.oat = int(cnt)
                
            if cmd == 'TAT':
                acars_position.tat = int(cnt)
            
            if cmd == 'FOB':
                acars_position.fob = lbs2kg(cnt)
                
            if cmd == 'WND':
                acars_position.wnd = cnt
            
            if cmd == 'DST':
                i = cnt.find('-')
                acars_position.distance_from_dept = int(cnt[0:i-1])
                acars_position.distance_total = int(cnt[i+2:])
            
            if cmd == 'AP':
                acars_position.airport = cnt
        ''' end of for loop '''
            
        if acars_position.message_type == 'QA':
            acars_position.waypoint = acars_position.airport
            acars_position.flight_status = FLIGHTSTATUS_TAXIOUT
            acars_position.vs = VSPEED_GND
        
        if acars_position.message_type == 'QB':
            result = (db.Query(AcarsPosition).filter("flight_id=", acars_position.flight_id)
                        .filter("message_type=", "QA").get())
            if result is not None:
                acars_position.waypoint = result.waypoint
            acars_position.flight_status = FLIGHTSTATUS_DEPARTURE
            acars_position.vs = VSPEED_CLB
            
        if acars_position.message_type == 'QC':
            acars_position.waypoint = acars_position.airport
            acars_position.flightstatus = FLIGHTSTATUS_LANDED
            acars_position.vs = VSPEED_GND
        
        if acars_position.message_type == 'QD':
            acars_position.flight_status = FLIGHTSTATUS_IN
            acars_position.vs = VSPEED_GND
        
        if acars_position.message_type == 'PR':
            '''do nothing extra'''
            pass

        if acars_position.message_type == 'AR':
            if acars_position.vs == VSPEED_CRZ:
                acars_position.flight_status = FLIGHTSTATUS_CRUISE
            elif acars_position.vs == VSPEED_CLB:
                if acars_position.distance_from_dept > 30:
                    '''Inflight Climb (more then 30nm from departure - insert what you want)'''
                    acars_position.flight_status = FLIGHTSTATUS_CRUISE
                else:
                    '''Initial Climb'''
                    acars_position.flight_status = FLIGHTSTATUS_CLIMB
                    
            elif acars_position.vs == VSPEED_DES:
                if (acars_position.distance_total - acars_position.distance_from_dept) > 100:
                    '''Inflight Descend (more then 100Nm to destination - insert what you want)'''
                    acars_position.flight_status = FLIGHTSTATUS_CRUISE
                else:
                    '''Initial Descend'''
                    acars_position.flight_status = FLIGHTSTATUS_DESC

        db.put(acars_position)
        acars_position.add_position()    
        self.response.out.write('1|')
    
    def pauseflight_cmd(self, version, data3, data4):
        self.response.out.write('1|');
    
    def endflight_cmd(self, version, data3, data4):
        acars_position = AcarsPosition()
        acars_position.flight_id = data3
        acars_position.flight_status = FLIGHTSTATUS_END
        acars_position.message_type = 'ZZ'
        
        db.put(acars_position)
        acars_position.add_position()    
        self.response.out.write('1|')
    
    def unknown_cmd(self, version, data3, data4):
        self.response.out.write('0|Wrong Function')
        
