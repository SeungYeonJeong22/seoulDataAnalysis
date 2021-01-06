from queue import Queue
from threading import Thread

q = Queue()

def a(q):
    q.put(1)
    q.put(2)
    q.put(3)


def b(q):
    recv = q.get()
    print(recv)
    recv = q.get()
    print(recv)
    recv = q.get()
    print(recv)




if __name__ == '__main__':
    c = Thread(target=a,args = (q,))
    c.start()

    d =Thread(target=b,args=(q,))
    d.start()

