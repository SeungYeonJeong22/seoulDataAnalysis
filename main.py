from bs4 import BeautifulSoup
from selenium import webdriver
import matplotlib.pyplot as plt
import pandas as pd
import folium

options = webdriver.ChromeOptions()
options.add_argument('headless')

driver = webdriver.Chrome('/Users/sanengr/Downloads/chromedriver',chrome_options=options)
driver.get('https://golmok.seoul.go.kr/fixedAreaAnalysis.do')
html = driver.page_source
soup = BeautifulSoup(html,'html.parser')

#상권 카테고리
cate_data = soup.find_all(attrs = {"id":"induM"})

#구 데이터
loc_gu_data = soup.find_all(attrs = {"id":"gu-select2"})

