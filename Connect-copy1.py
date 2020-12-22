from setupData import DATA
from subwayClass import subwayData

from socket import *
from select import *

HOST = ''
PORT = 10000
BUFSIZE = 1024
ADDR = (HOST,PORT)

serverSocket = socket(AF_INET,SOCK_STREAM)
serverSocket.bind(ADDR)
serverSocket.listen(100)

def setSubwayData(params):
    global DATA
    dataY = DATA['data{}'.format(params['user_input_date']['yy'])]

    
    ymd = params['user_input_date']['yy'] + params['user_input_date']['mm']
    
    mySub_data = subwayData(params,dataY,ymd)
    return mySub_data


try:
    clientSocket, addr_info = serverSocket.accept()
    print('Connect Success')
except Exception as e:
    print(e)
    print('Connect False')
    exit(0)
params = clientSocket.recv(65535)
print('recieve data : {}'.format(params))

setSubwayData(params)

clientSocket.close()
serverSocket.close()    