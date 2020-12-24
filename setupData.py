# -*- coding: utf-8 -*-     #이거 있어야 cmd에서 주석도 한글 처리 됨 (없으면 한글주석 에러)
import pandas as pd
import numpy as np
import os
import timeit, time
from tqdm import tqdm   #로딩바 확인을 위한 모듈
 
start_time = timeit.default_timer() # 시작 시간 체크

min_dataV = 0
max_dataV = [0,0,0]

#19년 20년 월별 데이터 생성
data2019 = {}
data2020 = {}
seoul_subway_dataF = os.path.abspath('seoul_subway_data') + '/'

def csv_to_dataFrame(year,dataY):
    global min_dataV,max_dataV
    year = str(year)
    
    for csvF in os.listdir(seoul_subway_dataF + '{}'.format(year)):
        #19년도 데이터 안에 이미 데이터가 있으면 넘어가고 없으면 기본값으로 추가
        if not 'data' + csvF[-10:-4] in dataY.keys():
            dataY.setdefault('data' + csvF[-10:-4])
        else:
            continue

        try:
            data = pd.read_csv(seoul_subway_dataF + year + '/' + csvF,encoding = 'UTF-8',index_col=False)
        except:
            data = pd.read_csv(seoul_subway_dataF + year + '/' + csvF,encoding = 'EUC-KR',index_col=False)
        dataY['data' + csvF[-10:-4]] = data
        
        
    c_dataY = dataY.copy()
    
    #로딩 바 (진행상황 확인)
    c_dataY_keys_list = tqdm(c_dataY.keys(),desc = year + 'data : ')

    #데이터에서 불필요한 데이터 조정
    for dataYM in c_dataY_keys_list:   
        t_dataY = pd.DataFrame()
        if '역ID' in dataY[dataYM].columns:
            dataY[dataYM].drop('등록일자',axis=1,inplace = True)
            dataY[dataYM].rename(columns = {'하차총승객수' : '등록일자'},inplace = True)
            dataY[dataYM].rename(columns = {'승차총승객수' : '하차총승객수'},inplace = True)
            dataY[dataYM].rename(columns = {'역명' : '승차총승객수'},inplace = True)
            dataY[dataYM].rename(columns = {'역ID' : '역명'},inplace = True)
            
        dataY[dataYM]['유동인구수'] = dataY[dataYM]['승차총승객수'] + dataY[dataYM]['하차총승객수']
        
        
        newData_min = {'사용일자':'', '승차총승객수':min_dataV, '하차총승객수':min_dataV, '유동인구수':min_dataV}

        #20190101 20190102 ...20190131
        dateKeys = dataY[dataYM].groupby('사용일자').indices.keys()
        
        #일별 데이터프레임 생성
        for i in dateKeys:
            globals()['dataY[data{}]'.format(i)] = pd.DataFrame()
            
        #일별 데이터 프레임에 값 대입 dataY[data20190101 .. ]
        for i in dateKeys:
            #사용일자 datatype(float -> str)으로 변환
            dataY[dataYM] = dataY[dataYM].astype({'사용일자':str})
            #노선명 역명 사용일자를 기준으로 멀티 인덱싱 하면서 나머지 승하차 유동인구 수 합하기
            tmp_grouped_dataF = dataY[dataYM].groupby(['노선명','역명','사용일자']).sum()
            tmp_grouped_dataF = tmp_grouped_dataF.sort_index()
            MulTdataF = tmp_grouped_dataF.unstack()
            """
            MulTdataF 데이터프레임 형태
                                                    승차총승객수 ...           |          하차총승객수              | 유동인구수
            
                                사용일자     20191201 20191202 ...         | 사용일자 20191201 20191202 ...
            --------------------------------------------------------------------------------------------------------
            노선명  3호선 | 역명        |가능
                                    |회기
                                    |...
            --------------------------------------------------------------------------------------------------------
                2호선 | 역명        |가능
                                    |회기
                                    |...
            """
            
            #각 컬럼에 해당하는 사용일자 컬럼에 해당하는 값들을 넣음
            tmp_getOn = MulTdataF['승차총승객수']['{}'.format(i)]
            tmp_getOff = MulTdataF['하차총승객수']['{}'.format(i)]
            tmp_float_Pop = MulTdataF['유동인구수']['{}'.format(i)]
            tmp_getOn = tmp_getOn.to_frame()
            tmp_getOff = tmp_getOff.to_frame()
            tmp_float_Pop = tmp_float_Pop.to_frame()

            dataY['data{}'.format(i)] = pd.concat([tmp_getOn,tmp_getOff,tmp_float_Pop],axis = 1,ignore_index=True).rename(columns = {0:'승차총승객수',1:'하차총승객수',2:'유동인구수'})
            
            dataY['data{}'.format(i)] = dataY['data{}'.format(i)].reset_index()
            dataY['data{}'.format(i)]['사용일자'] = i
            #인구수는 최저 0으로 고정 최대는 데이터마다 다름
            #근데 이게 지금 작동이 안되네...
            dataY['data{}'.format(i)] = dataY['data{}'.format(i)].append(newData_min,ignore_index=True)
            
#             print(dataY['data{}'.format(i)])
            
            #같은 노선 갯수 구해서 전체 합에서 노선 갯수만큼 나눠주기
            b_c = dataY['data{}'.format(i)].groupby('역명').count()[['승차총승객수','하차총승객수','유동인구수']]
            b   = dataY['data{}'.format(i)].groupby('역명').sum()[['승차총승객수','하차총승객수','유동인구수']]
            #DataframeGroupby 객체에서 sum을 하던 divide를 하던 뭔 짓을 한번 더 하면 dataframe으로 변환됨
            #이때 b_c와b의 groupby기준이 역명으로 인덱싱 되어있으니까 인덱스 이름을 '역명'으로 꺼내고 reset_index
            k   = b.divide(b_c).rename_axis('역명').reset_index()
            k['사용일자'] = dataY['data{}'.format(i)]['사용일자']
            
            dataY['data{}'.format(i)] = k
            
            t_dataY = pd.concat([t_dataY,dataY['data{}'.format(i)]],axis = 0,ignore_index=True)
            
        dataY[dataYM] = t_dataY.groupby('역명').sum().rename_axis('역명').reset_index()
        dataY[dataYM]['사용일자'] = dataYM[4:]
                
#지도를 어떻게 표현할지에 대해 필요있을 수 있는 코드
#(모든 월별 지도의 최대 레전드 값을 고정을 시켜놓으면 전체적으로 볼때는 알아보기 쉬우나 특정 몇몇 지역들이 지나치게 흐려짐)
#(월별로 지도의 최대 레전드 값을 다르게 하면 색은 눈에 띄게 표현 가능하나 전체적인 지도를 볼 때는 계속해서 레전드의 최댓값을 확인할 필요가 잇음)
#         if max_dataV[0] < dataF[dataY]['승차총승객수'].max():
#             max_dataV[0] = dataF[dataY]['승차총승객수'].max()
        
#         if max_dataV[1] < dataF[dataY]['하차총승객수'].max():
#             max_dataV[1] = dataF[dataY]['하차총승객수'].max()
            
#         if max_dataV[2] < dataF[dataY]['유동인구수'].max():
#             max_dataV[2] = dataF[dataY]['유동인구수'].max()           

csv_to_dataFrame(2019,data2019)
csv_to_dataFrame(2020,data2020)

terminate_time = timeit.default_timer() # 종료 시간 체크  

gu_sta_name = pd.read_csv(seoul_subway_dataF + 'Gu_StationNM.csv',encoding='utf-8')

def insert_gu(dataY):
    #데이터에 구 추가

    dataY_keys_list = tqdm(dataY.keys(),desc = '잔여 데이터 처리 : ')

    for dataYMD in dataY_keys_list:
        if not '구' in dataY[dataYMD].columns:    
            dataY[dataYMD] = pd.merge(dataY[dataYMD],gu_sta_name,on='역명',how = 'inner')

            if True in dataY[dataYMD].duplicated():
                dataY[dataYMD] = dataY[dataYMD].drop_duplicates()
                dataY[dataYMD].reset_index(inplace=True,drop = True)

        dataY[dataYMD] = dataY[dataYMD].sort_values(['사용일자','역명'],ascending = True).reset_index(drop = True)             
    
insert_gu(data2019)
insert_gu(data2020)

DATA = {}
if not 'data2019' in DATA.keys():
    DATA['data2019'] = data2019
if not 'data2020' in DATA.keys():
    DATA['data2020'] = data2020

print("%f초 걸렸습니다." % (terminate_time - start_time))