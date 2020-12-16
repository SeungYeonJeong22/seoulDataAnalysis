import folium
import webbrowser
import time
import matplotlib.pyplot as plt
import pandas as pd
import mapSetting
from setupData import DATA
import os

geo_str = mapSetting.geo_str

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
        self.ymd         = ymd               #201910
        self.dataYMD     = 'data' + ymd      #data201910   dtypes : str
        self.params = params
        
        try:
            self.dataY[self.dataYMD]
        except:
            print('__init__ : No data')
            return None
        loc_csv = pd.read_csv(os.path.abspath('Project/seoul_subway_data') + '/' + '구_역명_경위도.csv')
        #for문 안돌리고 바로 '구'를 찾기 위해 stack처리
        tmp_loc = loc_csv.stack()

        #그 구에 해당하는 역에 대한 리스트 생성
        st_pop = self.dataY[self.dataYMD][self.dataY[self.dataYMD]['구'] == params['user_gu_name']][['구','역명','유동인구수']]         
        st_pop[['구','역명','유동인구수']].reset_index(drop = True)
        self.st_info = pd.merge(st_pop,loc_csv,how = 'inner',on = ['구','역명'])        
        self.fig,self.ax = plt.subplots(nrows = 2,ncols = 1,figsize  = (len(self.st_info['구']),10))
        """
        - 구 입력값이 없을 경우
        - > 해당 일 혹은 월에 대한 전체 서울 맵 데이터 시각화
        - Map)
        - 서울시 전체 데이터
        - *** 그래프 ***
        - Subplot1 지역별 데이터 시각화(bargraph)
        """
        if params['user_gu_name'] == '':
            self.map=folium.Map(location=[37.5502, 126.982], zoom_start=11, min_zoom=11,max_zoom = 11,
                                tiles='stamentoner')
            self.location = [37.5502, 126.982]
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
        elif params['user_st_name'] == '':
        #그 구의 중심으로 loc 줌 확대
        #구에 해당하는 loc으로 줌 확대
            try:
                lat = tmp_loc[tmp_loc[tmp_loc.values == params['user_gu_name']].index[0][0]]['Latitude']
                long = tmp_loc[tmp_loc[tmp_loc.values == params['user_gu_name']].index[0][0]]['Longitude']
                
                
                self.map=folium.Map(location=[lat,long], zoom_start=13, min_zoom=13,max_zoom =13,
                                    tiles='stamentoner')            
                self.DrawSubMap()    
            except Exception as e:
                print(e)
                print('__init__ : 해당 시/군/구 가 없습니다')
                return None
        
        else:
            try:
                lat = tmp_loc[tmp_loc[tmp_loc.values == params['user_st_name']].index[0][0]]['Latitude']
                long = tmp_loc[tmp_loc[tmp_loc.values == params['user_st_name']].index[0][0]]['Longitude']
                
                self.map=folium.Map(location=[lat,long], zoom_start=15, min_zoom=13,max_zoom =15,
                                    tiles='stamentoner')            
                self.DrawSubMap()    
            except Exception as e:
                print(e)
                print('__init__ : 해당 역명이 존재하지 않습니다')                
                return None

    #서울 유동인구 파악
    def DrawSeoulMap(self):
        #맵 그려주기
        folium.Choropleth(
            geo_data=geo_str,
            data=self.dataY[self.dataYMD], 
            columns=['구','유동인구수'], 
            key_on='feature.properties.name',
            fill_color='PuRd',
            legend_name='서울 지하철 유동인구 수'
        ).add_to(self.map)
        self.SaveMap()
    
    #지하철 역별 유동인구 파악
    def DrawSubMap(self):
        #맵 그려주기
        for n in self.st_info.values:
            folium.CircleMarker(
                location = [n[3],n[4]],
                radius = n[2]/1000,
                fill_color='#3186cc',
            ).add_to(self.map)
        self.SaveMap()
    
    #그린 맵 파일 확인 후 저장 (나중에 html파일을 웹에 올려야 되서 따로 저장이 필요하긴함)
    def SaveMap(self):
        #쥬피터에서 보여주면 한글 깨져서 동일 경로 map 디렉토리에 해당 맵을 만들어줌
        if os.path.exists('./map'):
            if os.path.exists('./map/{}.html'.format(self.ymd)):
                os.remove('./map/{}.html'.format(self.ymd))
        else:
            os.makedirs('./map')
        self.map.save('./map/{}.html'.format(self.ymd))    
        
    #파일 삭제
    def DelMap(self):
        if os.path.exists('./map/{}.html'.format(self.ymd)):
            os.remove('./map/{}.html'.format(self.ymd))        

    #파일 열기 
    def OpenMap(self):
        try:
            if os.path.exists('./map/{}.html'.format(self.ymd)):
                BASE_DIR = os.path.dirname(os.path.abspath('map/{}.html'.format(self.ymd)))
                webbrowser.open('file:' + os.path.join(BASE_DIR,'{}.html'.format(self.ymd)))
                #파일 삭제전에 잠시 텀을 줘서 저장한게 보이게끔 함
                #나중에 파일 삭제 관련해서 다시 다뤄야할 때를 대비 (이 코드 안에서 삭제를 없애야 될 수도 있음 / 그래야 html에서 가져올수 있으니까)
                time.sleep(1)
                self.DelMap()
            else:
                raise Exception('OpenMap : ',self.ymd + ' file is not exist')
        except Exception as e:
            print(e)
            return False
        
        """
         ----------------------
        |    Graph Function    |
         ----------------------
        """        
    def DrawBarGraph(self):
        #구 단위로 그래프 그려줄 때
        if self.params['user_st_name'] == '':
            self.ax[0].bar(self.st_info['역명'],self.st_info['유동인구수'])
            self.ax[0].set_xticklabels(labels = self.st_info['역명'],rotation = 45)
            self.ax[0].set_title('{}월 {} 유동인구 수'.format(self.params['user_input_date']['mm'],self.params['user_gu_name']))                       
        else:
            self.ax[0].bar(self.st_info['역명'],self.st_info['유동인구수'])
            self.ax[0].set_xticklabels(labels = self.st_info['역명'],rotation = 45)
            #유저 인풋값 자체에 역이 있을경우
            if '역' == self.params['user_st_name'][-1]:
                self.ax[0].set_title('{}월 {} 유동인구 수'.format(self.params['user_input_date']['mm'],self.params['user_st_name']))                                   
            #유저 인풋값 자체에 역이 없을경우
            else:
                self.ax[0].set_title('{}월 {}역 유동인구 수'.format(self.params['user_input_date']['mm'],self.params['user_st_name']))
        
    def DrawLineGraph(self):
        ss = []
        k = 0
        p = []
        dd = pd.DataFrame()
        
        #구 단위로 그래프 그려줄 때
        #변수명은... 그냥...
        #시작 / 끝 날짜가 없다면 월 을 기준으로 전후 3개월을 데이터를 비교
        #지하철 역 명을 받지 않을 경우 시/군/구 가 기준
        if self.params['user_input_date']['st'] == '':
            if self.params['user_st_name'] == '':
                for i in range(3,-4,-1):
                    d = str(int(self.params['user_input_date']['mm']) - i).zfill(2)
                    p.append(d)
                    try:
                        self.dataY['data' + self.params['user_input_date']['yy'] + d]
                    except:
                        print('DraLineGraph : {} 데이터 없음'.format('data' + self.params['user_input_date']['yy'] + d))
                        break
                    ss[k] = self.dataY['data' + self.params['user_input_date']['yy'] + d][self.dataY['data' + self.params['user_input_date']['yy'] + d]['구'] == self.params['user_gu_name']].sum()['유동인구수']
                    ss[k] = pd.DataFrame(ss[k],columns = ['유동인구수'], index = [self.params['user_input_date']['yy'] + d])
                    dd = pd.concat([dd,ss[k]],axis = 0,ignore_index=True)
                    k += 1

                self.ax[1].plot(p,dd['유동인구수'])
                self.ax[1].set_xticklabels(labels = p)
                self.ax[1].set_title('{} 유동인구 수'.format(self.params['user_gu_name']))
        #시작 / 끝 날짜가 있다면 시작 일 부터 끝 일 까지 데이터를 비교                
        else:
            if self.params['user_st_name'] == '':
                for i in range(int(self.params['user_input_date']['st']),int(self.params['user_input_date']['ed'])+1):
                    d = str(int(self.params['user_input_date']['st']) + k).zfill(2)
                    p.append(d)
                    try:
                        self.dataY['data' + self.params['user_input_date']['yy'] + self.params['user_input_date']['mm'] + d]
                    except:
                        print('DraLineGraph : {} 데이터 없음'.format('data' + self.params['user_input_date']['yy'] + self.params['user_input_date']['mm']  + d))
                        break
                    ss.append(self.dataY['data' + self.params['user_input_date']['yy'] + self.params['user_input_date']['mm'] + d][self.dataY['data' + self.params['user_input_date']['yy'] + self.params['user_input_date']['mm'] + d]['구'] == self.params['user_gu_name']].sum()['유동인구수'])
                    ss[k] = pd.DataFrame(ss[k],columns = ['유동인구수'], index = [self.params['user_input_date']['yy'] + d])
                    dd = pd.concat([dd,ss[k]],axis = 0,ignore_index=True)
                    k += 1

                self.ax[1].plot(p,dd['유동인구수'])
                self.ax[1].set_xticklabels(labels = p)
                self.ax[1].set_title('{} 유동인구 수'.format(self.params['user_gu_name']))                
                


def setSubwayData(params):
    global DATA
    dataY = DATA['data{}'.format(params['user_input_date']['yy'])]
    
    if not params['user_input_date']['st'] == '' and not params['user_input_date']['ed'] == '':
        ymd = params['user_input_date']['yy'] + params['user_input_date']['mm'] + params['user_input_date']['st']        
        st_sub_data = subwayData(params,dataY,ymd)
        
        ymd = params['user_input_date']['yy'] + params['user_input_date']['mm'] + params['user_input_date']['ed']                
        ed_sub_data = subwayData(params,dataY,ymd)        
        return st_sub_data,ed_sub_data
    
    else:
        ymd = params['user_input_date']['yy'] + params['user_input_date']['mm']
        mySub_data = subwayData(params,dataY,ymd)
        return mySub_data