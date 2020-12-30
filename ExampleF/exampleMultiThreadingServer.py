import socket
import threading
from queue import Queue

def Send(group,send_queue):
    print('Thread Send Start')
    while True:
        try:
            #새롭게 추가된 클라이언트가 있을 경우 Send 쓰레드를 새롭게 만들기 위해 루프를 빠져나감
            recv = send_queue.get()
            if recv == 'Group Changed':
                print('Group Changed')
                break

            #for문을 돌면서 모든 클라이언트에게 동일한 메시지를 보냄
            for conn in group:
                msg = 'Client' + str(recv[2]) + ' >> ' + str(recv[0])
                if recv[1] != conn : #client본인이 보낸 메시지는 받을 필요가 없기 때문에 제외시킴
                    conn.send(bytes(msg.encode()))
                else:
                    pass
        except:
            pass

def Recv(conn,count,send_queue):
    print('Thread Recv' + str(count) + ' Start')
    while True:
        data = conn.recv(1024).decode()
        send_queue.put([data,conn,count])

#TCP Echo Server
if __name__ == '__main__':
    send_queue = Queue()
    Host = ''
    PORT = 9000
    server_sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM) #TCP socket
    server_sock.bind()
    server_sock.listen(10)  #파라미터는 접속수를 의미
    count = 0
    group = []  #연결된 클라이언트의 소켓정보를 리스트로 묶기 위함
    while True:
        count = count + 1
        conn, addr = server_sock.accept()
        group.append(conn)  #연결된 클라이언트의 소켓정보
        print('Connected '  + str(addr))

        if count > 1:
            send_queue.put('Group Changed')
            thread1 = threading.Thread(target=Send, args=(group,send_queue))
            thread1.start()

        else:
            thread1 = threading.Thread(target=Send, args=(group,send_queue))
            thread1.start()
        
        #소켓에 연결된 각각의 클라이언트의 메시지를 받을 쓰레드
        thread2 = threading.Thread(target=Recv,args=(conn,count,send_queue))
        thread2.start()