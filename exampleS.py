from socket import *
from select import *

HOST = ''
PORT = 10000
BUFSIZE = 1024
ADDR = (HOST,PORT)

serverSocket = socket(AF_INET,SOCK_STREAM)

serverSocket.bind(ADDR)
print('Bind')

serverSocket.listen(100)
print('listen')

clientSocket, addr_info = serverSocket.accept()
print('accept')
print('--client information--')
print(clientSocket)

data = clientSocket.recv(65535)
print('recieve data : ',data.decode())

clientSocket.close()
serverSocket.close()
print('close')