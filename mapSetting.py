# -*- coding: utf-8 -*- 
import json
import os

os.path.abspath('map')

geo_path = os.path.abspath('map') + '/skorea-municipalities-2018-geo.json'
geo_str = json.load(open(geo_path, encoding='utf-8'))

#json 데이터 안다듬어주면 전국단위로 난리남
print('json 처리 전 지역 수 : ',len(geo_str['features']))
min_len_geoStr = False
k = [-1,-2]
#서울 지역 코드 값 = 1로 시작
#왜인지는 모르겠는데 한번에 처리가 안되서 이전 카운트 개수하고 현재 카운트 개수에 차이가 없을 때 break
while min_len_geoStr == False:
    if k[0] == k[1]:
        min_len_geoStr = True
    k[0] = len(geo_str['features'])
    for i,t in enumerate(geo_str['features']):
        if not t['properties']['code'][0] == '1':
            del geo_str['features'][i]
    k[1] = len(geo_str['features'])

print('json 처리 후 지역 수 : ',len(geo_str['features']))