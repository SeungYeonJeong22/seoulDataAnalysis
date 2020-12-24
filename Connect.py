# -*- coding: utf-8 -*- 
from setupData import DATA
from subwayClass import subwayData

from socket import *
from select import *

HOST = ''
PORT = 10000
BUFSIZE = 1024
ADDR = (HOST,PORT)

def setSubwayData(params):
    global DATA
    dataY = DATA['data{}'.format(params['user_input_date']['yy'])]

    
    ymd = params['user_input_date']['yy'] + params['user_input_date']['mm']
    
    mySub_data = subwayData(params,dataY,ymd)
    return mySub_data