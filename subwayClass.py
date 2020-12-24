import folium
import webbrowser               #map파일 열떄
import time
import matplotlib.pyplot as plt
import pandas as pd

import mapSetting
from setupData import DATA
import os

geo_str = mapSetting.geo_str
loc_csv = pd.read_csv(os.path.abspath('seoul_subway_data') + '/' + 'Lat_Long.csv')

class subwayData:
    global geo_str,DATA
    
    """
     --------------------
    |    Map Function    |
     --------------------
    """ 

    def __init__(self,params,dataY : pd.DataFrame,ymd : str):      
        #font 설정
        plt.rcParams['font.family'] = 'AppleGothic'        
        
        self.dataY      = dataY            #data2019     dtypes : dataframe
        self.ymd         = ymd               #201910/20191001      dtypes : str
        self.dataYMD     = 'data' + ymd      #data201910/data20191001   dtypes : str

        self.params = params
        self.uid_y = params['user_input_date']['yy']
        self.uid_m = params['user_input_date']['mm']
        self.uid_st = params['user_input_date']['st']
        self.uid_ed = params['user_input_date']['ed']
        self.u_st = params['user_st_name']
        self.u_gu = params['user_gu_name']        
        
        if self.uid_st == '':
            self.map_title = self.uid_y + self.uid_m
        else:
            self.map_title = self.uid_y + self.uid_m + ' ' + self.uid_st + ' ~ ' + self.uid_ed
        
        try:
            self.dataY[self.dataYMD]
        except:
            print('__init__ : No data')
            return None
        
        #st~ed가 있을경우 -> self.st_edDF / 없을경우 처리 -> self.dataY[self.dataYMD]
        #self.st_edDF : st~ed까지의 평균 [구,승차총승객수,하차총승객수,유동인구수]
        #첫날과 끝날을 받을 경우 전체 합 / 날 수 만큼의 값으로 맵 그려주기 위한 데이터프레임 생성
        try:
            if self.uid_st == '':
                pass
            else:
                st_edDF_gu = pd.DataFrame()
                st_edDF_st = pd.DataFrame()
                t_sum_gu = []
                t_sum_st = []
                k = 0    
                for i in range(int(self.uid_st),int(self.uid_ed)+1):
                    i = str(i).zfill(2)
                    t_sum_gu.append(self.dataY['data' + self.uid_y + self.uid_m + i])
                    t_sum_st.append(self.dataY['data' + self.uid_y + self.uid_m + i])

                    t_sum_gu[k] = pd.DataFrame(t_sum_gu[k],columns = ['구','승차총승객수','하차총승객수','유동인구수'])
                    t_sum_st[k] = pd.DataFrame(t_sum_st[k],columns = ['역명','승차총승객수','하차총승객수','유동인구수'])                

                    t_sum_gu[k] = t_sum_gu[k].groupby('구').sum().rename_axis('구').reset_index()
                    t_sum_st[k] = t_sum_st[k].groupby('역명').sum().rename_axis('역명').reset_index()                

                    st_edDF_gu = pd.concat([st_edDF_gu,t_sum_gu[k]],axis = 0,ignore_index = True)
                    st_edDF_st = pd.concat([st_edDF_st,t_sum_st[k]],axis = 0,ignore_index = True)                
                    k += 1

                #신설역 혹은 신설 구가 데이터에 없을 경우가 있을수 있기 때문에 단순하게 k로 나누면 안됨
                tmp_gu_cnt = st_edDF_gu.groupby('구').count()
                tmp_st_cnt = st_edDF_st.groupby('역명').count()

                tmp_sum_gu = st_edDF_gu.groupby('구').sum()
                tmp_sum_st = st_edDF_st.groupby('역명').sum()

                st_edDF_gu = tmp_sum_gu.divide(tmp_gu_cnt)
                st_edDF_st = tmp_sum_st.divide(tmp_st_cnt)

                self.st_edDF_gu = st_edDF_gu.rename_axis('구').reset_index()
                st_edDF_st = st_edDF_st.rename_axis('역명').reset_index()
        except Exception as e:
            print('__init__ error : st~ed')
            return None
            
        #<----- MAP 초기화 & 그리기 ----->#
        #경위도 추가
        loc_csv = pd.read_csv('./seoul_subway_data/Lat_Long.csv')
        
        #for문 안돌리고 바로 '구'를 찾기 위해 stack처리
        tmp_loc = loc_csv.stack()        

        """
        - 구 입력값이 없을 경우
        - > 해당 일 혹은 월에 대한 전체 서울 맵 데이터 시각화
        - Map)
        - 서울시 전체 데이터
        - *** 그래프 ***
        - Subplot1 지역별 데이터 시각화(bargraph)
        """
        if self.u_gu == '':
            self.map=folium.Map(location=[37.5502, 126.982], zoom_start=11, min_zoom=11,max_zoom = 11,
                                tiles='stamentoner')
            self.location = [37.5502, 126.982]
            
            self.fig,self.ax = plt.subplots(nrows = 2,ncols = 1,figsize  = (len(self.dataY[self.dataYMD]['역명']),10))            
            
            self.DrawSeoulMap()
            
            """
            - 구 데이터만 받아올 경우
            - Map )
            - 해당 역의 해당 구로 줌 스타트
            - 구 내 circle을 통한 역간의 인구 파악
            -  *** 그래프 ***
            - subplot1을 통한 해당 구의 모든 역의 유동인구수 그래프 시각화 ( bar graph로 표현 )
            - subplot2를 통한 해당 구의 전후 약 3개월간의 인구 변화 시각화 ( line graph )            
            - 참고) 경위도 csv는 구글 스프레드 시트의 awesome table geo를 활용해서 얻음
            """
        elif self.u_st == '':
            try:            
                #구에 해당하는 역명들의 데이터 프레임 생성
                if self.uid_st == '':
                    st_pop = self.dataY[self.dataYMD][self.dataY[self.dataYMD]['구'] == self.u_gu][['구','역명','승차총승객수','하차총승객수','유동인구수']]
                    self.st_info = pd.merge(st_pop,loc_csv,how = 'inner',on = '역명')
                else:
                    st_pop = st_edDF_st[['역명','승차총승객수','하차총승객수','유동인구수']]                    
                    st_pop = pd.merge(st_pop,loc_csv,how='inner',on='역명')
                    st_pop = st_pop.dropna()
                    self.st_info = st_pop[st_pop['구'] == self.u_gu].reset_index(drop = True)

                self.fig,self.ax = plt.subplots(nrows = 2,ncols = 1,figsize  = (len(self.st_info['역명']),10))

                #구의 중심으로 loc 줌 확대
                lat = tmp_loc[tmp_loc[tmp_loc.values == self.u_gu].index[0][0]]['Latitude']
                long = tmp_loc[tmp_loc[tmp_loc.values == self.u_gu].index[0][0]]['Longitude']
                
                self.map=folium.Map(location=[lat,long], zoom_start=13, min_zoom=13,max_zoom =13, tiles='stamentoner')
                self.DrawSubMap()                
            except Exception as e:
                print(e)
                print('__init__ : 해당 시/군/구 가 없습니다')
                return None
        
        else:
            try:
                #구에 해당하는 역명들의 데이터 프레임 생성
                if self.uid_st == '':
                    st_pop = self.dataY[self.dataYMD][self.dataY[self.dataYMD]['구'] == self.u_gu][['역명','승차총승객수','하차총승객수','유동인구수']]
                    self.st_info = pd.merge(st_pop,loc_csv,how = 'inner',on = '역명')
                else:
                    st_pop = st_edDF_st[['역명','승차총승객수','하차총승객수','유동인구수']]
                    st_pop = pd.merge(st_pop,loc_csv,how='inner',on='역명')
                    st_pop = st_pop.dropna()
                    self.st_info = st_pop[st_pop['구'] == self.u_gu].reset_index(drop = True)

                self.fig,self.ax = plt.subplots(nrows = 2,ncols = 1,figsize  = (len(self.st_info['역명']),10))
                    
                #구의 중심으로 loc 줌 확대            
                lat = tmp_loc[tmp_loc[tmp_loc.values == self.u_gu].index[0][0]]['Latitude']
                long = tmp_loc[tmp_loc[tmp_loc.values == self.u_gu].index[0][0]]['Longitude']
                
                self.map=folium.Map(location=[lat,long], zoom_start=15, min_zoom=13,max_zoom =15, tiles='stamentoner')
                self.DrawSubMap()
            except Exception as e:
                print(e)
                print('__init__ : 해당 역명이 존재하지 않습니다')                
                return None

    #서울 유동인구 파악
    def DrawSeoulMap(self):
        #맵 그려주기
        try:
            if self.uid_st == '':
                folium.Choropleth(
                    geo_data=geo_str,
                    data=self.dataY[self.dataYMD], 
                    columns=['구','유동인구수'], 
                    key_on='feature.properties.name',
                    fill_color='PuRd',
                    legend_name='서울 지하철 유동인구 수'
                ).add_to(self.map)
            else:
                folium.Choropleth(
                    geo_data=geo_str,
                    data=self.st_edDF_gu, 
                    columns=['구','유동인구수'], 
                    key_on='feature.properties.name',
                    fill_color='PuRd',
                    legend_name='서울 지하철 유동인구 수'
                ).add_to(self.map)
        except Exception as e:
            print(e)
        self.SaveMap()    
    #지하철 역별 유동인구 파악
    #st_info = ['역명', '승차총승객수', '하차총승객수', '유동인구수', '구', 'Latitude', 'Longitude']
    def DrawSubMap(self):
        try:
            for n in self.st_info.values:
                folium.CircleMarker(
                    location = [n[5],n[6]],
                    radius = n[3]/1000,
                    fill_color='#3186cc',
                ).add_to(self.map)
        except Exception as e:
            print(e)
        self.SaveMap()

    
    #그린 맵 파일 확인 후 저장 (나중에 html파일을 웹에 올려야 되서 따로 저장이 필요하긴함)
    def SaveMap(self):
        #쥬피터에서 보여주면 한글 깨져서 동일 경로 map 디렉토리에 해당 맵을 만들어줌
        if os.path.exists('./map'):
            if os.path.exists('./map/{}.html'.format(self.map_title)):
                os.remove('./map/{}.html'.format(self.map_title))
        else:
            os.makedirs('./map')
        self.map.save('./map/{}.html'.format(self.map_title))    
        
    #파일 삭제
    def DelMap(self):
        if os.path.exists('./map/{}.html'.format(self.map_title)):
            os.remove('./map/{}.html'.format(self.map_title))        

    #파일 열기 
    def OpenMap(self):
        try:
            if os.path.exists('./map/{}.html'.format(self.map_title)):
                BASE_DIR = os.path.dirname(os.path.abspath('map/{}.html'.format(self.map_title)))
                webbrowser.open('file:' + os.path.join(BASE_DIR,'{}.html'.format(self.map_title)))
                #파일 삭제전에 잠시 텀을 줘서 저장한게 보이게끔 함
                #나중에 파일 삭제 관련해서 다시 다뤄야할 때를 대비 (이 코드 안에서 삭제를 없애야 될 수도 있음 / 그래야 html에서 가져올수 있으니까)
                time.sleep(1)
                self.DelMap()
            else:
                raise Exception('OpenMap : ',self.map_title + ' file is not exist')
        except Exception as e:
            print(e)
            return False
        
        
        """
         ----------------------
        |    Graph Function    |
         ----------------------
        """        
    def DrawGraph(self):
        self.DrawBarGraph()
        if not self.u_st == '':
            self.DrawLineGraph()
        
        
    def DrawBarGraph(self):
        #서울 전체에 대한 그래프 그려줄 때
        if self.u_gu == '':
            self.ax[0].bar(self.dataY[self.dataYMD]['구'],self.dataY[self.dataYMD]['유동인구수'])
            self.ax[0].set_xticklabels(labels = self.dataY[self.dataYMD]['구'],rotation = 45)
            self.ax[0].set_title("{}년 {}월 서울 유동인구 수".format(self.uid_y,self.uid_m))
        
        #시/군/구 단위로 그래프 그려줄 때
        elif self.u_st == '':
            self.ax[0].bar(self.st_info['역명'],self.st_info['유동인구수'])
            self.ax[0].set_xticklabels(labels = self.st_info['역명'],rotation = 45)
            self.ax[0].set_title('{}년 {}월 {} 유동인구 수'.format(self.uid_y,self.uid_m,self.u_gu))
        #역 단위는 승 하차 정보 표시
        else:
            bar = self.st_info[['승차총승객수','하차총승객수']]
            self.ax[0].bar()
            self.ax[0].set_title('{}역 승하차 정보'.format(self.st_info['역명']))

        
    def DrawLineGraph(self):
        ss = []
        p = []
        dd = pd.DataFrame()
        
        #구 단위로 그래프 그려줄 때
        #변수명은... 그냥... 임시로 쓴것도 많음
        #시작 / 끝 날짜가 없다면 월 을 기준으로 전후 3개월을 데이터를 비교
        if self.uid_st == '':
            for i in range(3,-4,-1):
                d = str(int(self.uid_m) - i).zfill(2)
                p.append(d)
                try:
                    self.dataY['data' + self.uid_y + d]
                except Exception as e:
                    print(e)
                    print('DraLineGraph : {} 데이터 없음'.format('data' + self.uid_y + d))
                    return False            
                    
            for k in range(len(p)):      
                #지하철 역 명을 받지 않을 경우 시/군/구 가 기준
                if self.u_st == '':
                    ss.append(self.dataY['data' + self.uid_y + p[k]][self.dataY['data' + self.uid_y + p[k]]['구'] == self.u_gu].sum()['유동인구수'])
                    ss[k] = pd.DataFrame(ss[k],columns = ['유동인구수'], index = [self.uid_y + p[k]])
                    dd = pd.concat([dd,ss[k]],axis = 0,ignore_index=True)
                else:
                    ss.append(self.dataY['data' + self.uid_y + p[k]][self.dataY['data' + self.uid_y + p[k]]['역명'] == self.u_st].sum()['유동인구수'])
                    ss[k] = pd.DataFrame(ss[k],columns = ['유동인구수'], index = [self.uid_y + p[k]])
                    dd = pd.concat([dd,ss[k]],axis = 0,ignore_index=True)


            if self.u_st == '':
                self.ax[1].set_title('{} 유동인구 수'.format(self.u_gu))
            else:
                if '역' == self.u_st[-1]:
                    self.ax[1].set_title('전후 3개월 {} 유동인구 수'.format(self.u_st))                    
                else:
                    self.ax[1].set_title('전후 3개월 {}역 유동인구 수'.format(self.u_st))                
            self.ax[1].plot(p,dd['유동인구수'])
            
                
        #시작 / 끝 날짜가 있다면 시작 일 부터 끝 일 까지 데이터를 비교                
        else:
            for i in range(int(self.uid_st),int(self.uid_ed)+1):
                d = str(i).zfill(2)
                p.append(d)
                try:
                    self.dataY['data' + self.uid_y + self.uid_m + d]
                except:
                    print('DraLineGraph : {} 데이터 없음'.format('data' + self.uid_y + self.uid_m  + d))
                    return False
                        
            for k in range(len(p)):           
                if self.u_st == '':     
                    ss.append(self.dataY['data' + self.uid_y + self.uid_m + p[k]][self.dataY['data' + self.uid_y + self.uid_m + p[k]]['구'] == self.u_gu].sum()['유동인구수'])
                    ss[k] = pd.DataFrame(ss[k],columns = ['유동인구수'], index = [self.uid_y + self.uid_m + p[k]])
                    dd = pd.concat([dd,ss[k]],axis = 0,ignore_index=True)
                else:
                    ss.append(self.dataY['data' + self.uid_y + self.uid_m + p[k]][self.dataY['data' + self.uid_y + self.uid_m + p[k]]['역명'] == self.u_st].sum()['유동인구수'])
                    ss[k] = pd.DataFrame(ss[k],columns = ['유동인구수'], index = [self.uid_y + self.uid_m + p[k]])
                    dd = pd.concat([dd,ss[k]],axis = 0,ignore_index=True)                    

            if self.u_st == '':
                self.ax[1].set_title('{}일 ~ {}일 까지 {} 유동인구 수'.format(self.uid_st, self.uid_ed, self.u_gu))
            else:
                if '역' == self.u_st[-1]:                    
                    self.ax[1].set_title('{}일 ~ {}일 까지 {} 유동인구 수'.format(self.uid_st, self.uid_ed, self.u_st))
                else:
                    self.ax[1].set_title('{}일 ~ {}일 까지 {} 유동인구 수'.format(self.uid_st, self.uid_ed, self.u_st))               
            self.ax[1].plot(p,dd['유동인구수'])                    
