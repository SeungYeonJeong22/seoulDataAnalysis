import socket
import threading

def Send(client_sock):
    while True:
        send_data = bytes(input().encode()) #사용자입력
        client_sock.send(send_data)

def Recv(client_sock):
    while True:
        recv_data = client_sock.recv(1024).decode()
        print(recv_data)

#TCP Client
if __name__ == '__main__':
    client_sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM) #TCP Socket
    Host = 'localhost'
    Port = 9000
    client_sock.connect((Host,Port)) #서버로 연결시도 / tuple로 넘겨준다는것에 유의
    print('Connecting to ',Host,Port)

    thread1 = threading.Thread(target=Send,args = (client_sock))
    thread1.start()

    thread2 = threading.Thread(target=Recv,args = (client_sock))
    thread2.start()