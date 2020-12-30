# -*- coding: utf-8 -*- 
from setupData import DATA
from subwayClass import subwayData

from socket import *
from select import *
from ast import literal_eval    #클라이언트와 통신할 때 (str->dict) 하기 위한 함수 / eval 보다 보안이 좋으나 제약이 심함
from queue import Queue

import json
import threading

HOST = ''
PORT = 10000
BUFSIZE = 1024
ADDR = (HOST,PORT)

def Send(group,send_queue):
    print('Thread Send Start')
    while True:
        try:
            #스레드 recv에서 받아온 값으로 판별
            recv = send_queue.get()
            if recv == 'Group Changed':
                print('Group Changed')
                break
            
            for c_sock in group:
                user_params = setSubwayData(recv[0])

                user_params = json.dumps(user_params.__str__(),indent=2).encode('utf-8')
                if recv[1] == c_sock:
                    c_sock.send(user_params)
                else:
                    pass
        except:
            pass

def Recv(c_sock,cnt,send_queue):
    print("Thread Recv" + str(cnt) + "Start")
    while True:
        data = literal_eval(c_sock.recv(1024).decode('utf-8'))
        send_queue.put([data,c_sock,cnt])

def setSubwayData(params):
    global DATA
    dataY = DATA['data{}'.format(params['user_input_date']['yy'])]

    
    ymd = params['user_input_date']['yy'] + params['user_input_date']['mm']
    
    mySub_data = subwayData(params,dataY,ymd)
    return mySub_data


send_queue = Queue()
serverSocket = socket(AF_INET,SOCK_STREAM)
serverSocket.bind(ADDR)
serverSocket.listen(10) #파라미터는 접속 수를 의미

cnt = 0
group = []  #연결된 클라이언트의 소캣정보를 리스트로 묶기 위함

while True:
    try:
        c_sock, addr_info = serverSocket.accept()
        group.append(c_sock)
        cnt += 1
        print('Connect Success' + str(addr_info))
    except Exception as e:
        print('Connect False' + str(addr_info))
        exit(0)    

    #클라이언트가 여러명이 접속 할 경우 리스트에 담아가면서 시작
    if cnt > 1:
        send_queue.put('Group Changed')
        thread1 = threading.Thread(target=Send,args=(group,send_queue))
        thread1.start()
    else : 
        thread1 = threading.Thread(target=Send,args=(group,send_queue))
        thread1.start()

    #각 스레드의 클라이언트로부터 recv 얻어올 때까지 while문 진행x
    thread2 = threading.Thread(target=Recv, args=(c_sock,cnt,send_queue))
    thread2.start()

    # try:
    #     params = clientSocket.recv(65535)
    #     params = params.decode(encoding='utf-8')
    #     params = literal_eval(params)

    #     print('recieve data : {}'.format(params))

    #     user_params = setSubwayData(params)

    #     user_params = user_params.__str__()
    #     user_params = json.dumps(user_params,indent=2).encode('utf-8')
    #     clientSocket.send(user_params)

    # except Exception as e:
    #     print(e)
    #     # exit(0)
c_sock.close()
serverSocket.close()