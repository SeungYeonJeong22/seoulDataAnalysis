from socket import *
from select import *
import sys
from time import ctime

exit_flag = 0

HOST = '127.0.0.1'
PORT = 10000
BUFSIZE = 1024
ADDR = (HOST,PORT)

clientSocket = socket(AF_INET,SOCK_STREAM)
try:
    clientSocket.connect(ADDR)
except Exception as e:
    print(e)
    print('<------------------------------------------------>')
    print('Connect False')
    exit(0)

print('Connect Success')
while exit_flag == 0:
    #######################입력 란        #######################
    #나중엔 js에서 인풋값으로 사용자한테 받아와야 함
    try:
        a = input('Input yyyy mm | yyyy mm start_date end_date (ex:2020 01 | 2020 01 01 31) : ')
        b = a.split(' ')
        user_input_date = {
            'yy' : '',
            'mm' : '',
            'st' : '',
            'ed' : ''
        }
        for i,t in enumerate(b):
            user_input_date[list(user_input_date.keys())[i]] = t
        
        user_gu_name = input('input gu name : ')
        user_st_name = input('input station name : ')            

        params = {
            'user_input_date' : user_input_date,
            'user_gu_name' : user_gu_name,
            'user_st_name' : user_st_name
        }
    except Exception as e:
        print(e)
        
    #######################          실행 란        #######################
    try:
        #일 값을 받을 경우 추가
        if not user_input_date['st'] == '' and not user_input_date['ed'] == '':                
            st_ym = user_input_date['yy'] + user_input_date['mm'] + user_input_date['st']
            ed_ym = user_input_date['yy'] + user_input_date['mm'] + user_input_date['ed']            
        
        clientSocket.send(params)    
        #유저로부터 받은 연도가 DATA.keys()에 없으면 다음 확인


        #임시
        dataYear = ['data2019','data2020']


        for datayear in dataYear:
            if not user_input_date['yy'] in datayear:
                raise Exception('__main__ : {} data is not exist'.format(user_input_date['yy']))
                continue
            #유저로부터 st, ed 둘다 받았을 때만 확인
            if not user_input_date['st'] == '' and not user_input_date['ed'] == '':
                my_subway_data = clientSocket.recv(65535)
                
                #맵을 잘 받아왔으면 bar그래프와 line그래프 그리기
                if not my_subway_data.OpenMap() == False:
                    my_subway_data.DrawGraph()
                    exit_flag = 1
                    break
            #시작날 혹은 끝날 만 있을 경우 처리
            elif bool(user_input_date['st'] == '') ^ bool(user_input_date['ed'] == ''):
                print('start date and end date must be together')
                continue
            else:
                clientSocket.send(params)

                #map이 열리면 break
                #맵을 잘 받아왔으면 bar그래프와 line그래프 그리기                    
                if not my_subway_data.OpenMap() == False:
                    my_subway_data.DrawGraph()
                    exit_flag = 1                        
                    break
    except Exception as e:
        print(e)
 