import multiprocessing as mp
import time

st = time.time() #start time

def count(name):
    for i in range(1,50001):
        print(name," : ",i)

num_list = ['p1','p2','p3','p4']

if __name__ == '__main__':
    pool = mp.Pool(processes=2) #현재 시스템에서 사용할 프로세스 개수
    pool.map(count,num_list)    #map메소드 활용 / 실행할 count메소드와 num_list전달
    pool.close()                #리소스 낭비 방지를 위한 close호출 및 작업 완료 대기 위해 join호출
    pool.join()

print("--- %s seconds ---"%(time.time() - st))

