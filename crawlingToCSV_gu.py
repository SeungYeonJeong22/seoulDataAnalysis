# from selenium import webdriver
# import time
# import os, csv

# option = webdriver.ChromeOptions()
# option.add_argument('headless')

# # os.path.abspath('chromedriver')

# driver = webdriver.Chrome(os.path.abspath('chromedriver'),options=option)
# driver.get('https://gits.gg.go.kr/gtdb/web/trafficDb/railRoad/TransitSWPass.do')

# time.sleep(3)

# def setRadio():
#     driver.find_element_by_xpath('//*[@id="radio1"]').click()

# def setSelect1(sel1):
#     driver.find_element_by_xpath("//select[@name='select1']/option[text()='%s']" %sel1).click()
    
# def setSelect2(sel2):
#     driver.find_element_by_xpath("//select[@name='select2']/option[text()='%s']" %sel2).click()

# #soup로 고정된 html 값에서 radio1 버튼 찾아와서 클릭하기
# setRadio()

# #rad 버튼 클릭후 동적으로 변경된 웹페이지에서 select1아이디 값 가져오기
# select1 = driver.find_element_by_id('select1')
# t_sel1 = select1.text.split('\n')
# sel1 = []
# for i,t in enumerate(t_sel1):
#     if not t.strip() == '':
#         sel1.append(t.strip())

# #시 - 역명 넣을 csv파일 생상(기존에 있는건 삭제)
# if os.path.exists('./seoul_subway_data/구_역명.csv'):
#     os.remove('./seoul_subway_data/구_역명.csv')

#encoding 설정 안해주면 mac은 되는데 window는 안될 때 있음 (조심)
# with open('./seoul_subway_data/구_역명.csv','w',encoding = 'utf-8') as csvFile:
#     writer = csv.DictWriter(csvFile,fieldnames=['구','역명'])    
#     writer.writeheader()
    
# #sel1 값을 넣은 후 sel2값 넣고 검색 후 list값들을 가져온 다음 데이터 정리
# for i in sel1:
#     setSelect1(i)
    
#     sel2 = driver.find_element_by_id('select2')
#     t_sel2 = sel2.text.split('\n')
#     for a in range(len(t_sel2)):
#         t_sel2[a] = t_sel2[a].strip()
#         #전체 선택 혹은 비어있는 경우는 넘어가기 (행정 구역만 필요하니까)
#         if '전체선택' == t_sel2[a] or '' == t_sel2[a]:
#             continue
        
#         setSelect2(t_sel2[a])
#         driver.find_element_by_xpath('//*[@id = "search"]').click()
#         li_loc = (driver.find_element_by_id('selList')).text.split('\n')

#         for i in li_loc:
#             #가져온 list값은 매봉(1호선) 이런식으로 돼있으므로 ()를 기준으로 역이름과 호선명 나눠주기
#             st_idx = i.find('(') + 1
#             f_idx = i.find(')')
#             t_sel2[a] = t_sel2[a].replace('_','')
#             #csv파일에 바로 넣기
#             with open('./seoul_subway_data/구_역명.csv','a',encoding = 'utf-8') as csvFile:
#                 writer = csv.DictWriter(csvFile,fieldnames=['구','역명'])
#                 writer.writerow({'구':t_sel2[a],'역명':i[:st_idx-1]})
                
# driver.quit()