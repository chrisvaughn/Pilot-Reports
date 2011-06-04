import os

from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.api import users as google_users
from google.appengine.ext.webapp import template

from model.users import Users
from model.acars import AcarsPosition

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


def lat_degdecmin_2_decdeg(dat):
    
    if dat == '':
        return 0
    
    i = 0
    j = dat.find(' ', 0)
    k = max(dat.find('.', j), j+1)
    
    dec = dat[1:j+1]
    dec += dat[j+1:k-j+2] / 60
    
    if dat[0] == 'S':
        dec = -dec;
        
    return round(dec,4)


def lon_degdecmin_2_decdeg(dat):
    
    if dat == '':
        return 0
    
    i = 0;
    j = dat.find(' ', 0)
    k = max( dat.find('.', j), j+1)
    
    dec = dat[1:j+1]
    dec += dat[j+1:k-j+2] / 60
    
    if dat[0] == 'W':
        dec = -dec
    
    return round(dec,4)



class LiveAcarsController(webapp.RequestHandler):
    def get(self):
        pass