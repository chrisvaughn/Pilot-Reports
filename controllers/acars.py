import os
import sys
import logging

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

        if check_XAcars_version(data1) == ACARS_UNKNOWN:
            self.response.out.write('0|Invalid XAcars Version')
            return
        
        logging.debug('?DATA1='+data1+'&DATA2='+data2+'&DATA3='+data3+'&DATA4='+data4)

        data2 = data2.replace("\'", "''")
        
        if data3 != '':
            data3 = data3.replace("\'", "''")
        if data4 != '':
            data4 = data4.replace("\'", "''")
         
        self.response.out.write(data1+"<br>")
        self.response.out.write(data2+"<br>")
        self.response.out.write(data3+"<br>")
        self.response.out.write(data4+"<br>")

