# ------------------------------------------------------
# ---------------------- main.py -----------------------
# ------------------------------------------------------
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
from PyQt5 import QtCore
from matplotlib.backends.backend_qt5agg import (NavigationToolbar2QT as NavigationToolbar)

import numpy as np
import random
import time
import threading

import requests
from bs4 import BeautifulSoup as bs


from selenium import webdriver
from bs4 import BeautifulSoup
from urllib.request import urlopen
import pandas as pd
import re

import pandas as pd
import matplotlib.pyplot as plt  # 그래프 시각화 패키지

class MatplotlibWidget(QMainWindow):

    def __init__(self):
        QMainWindow.__init__(self)
        loadUi("qt_designer.ui", self)
        self.setWindowTitle("PyQt5 & Matplotlib Example GUI")
        self.showMaximized()
        self.setWindowFlags(QtCore.Qt.Window |
                           QtCore.Qt.CustomizeWindowHint |
                           QtCore.Qt.WindowMinimizeButtonHint |
                           QtCore.Qt.WindowMaximizeButtonHint |
                           QtCore.Qt.WindowCloseButtonHint |
                           QtCore.Qt.WindowStaysOnTopHint
                           )
        self.pushButton_generate_random_signal.clicked.connect(self.plot_graph)

        exist_text = self.history_list.text() + " Plot Button Click and 30seconds Wait...." + "\n"
        self.history_list.setText(exist_text)

        self.addToolBar(NavigationToolbar(self.MplWidget.canvas, self))
        self.stock_name.setText("코오롱인더")
        self.stock_no.setText("120110")

    def plot_graph(self):
        self.today_stock()
        exist_text = self.history_list.text() + "\n" + self.stock_name.text() + "\n" + " OK." + "\n"
        self.history_list.setText(exist_text)

        # 검색주식 입력
        item_name = self.stock_no.text()
        item_name = self.stock_name.text()

        # 종목코드 검색
        code_df = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13', header=0)[
            0]

        # 종목코드가 6자리이기 때문에 6자리를 맞춰주기 위해 설정해줌
        code_df.종목코드 = code_df.종목코드.map('{:06d}'.format)

        # 우리가 필요한 것은 회사명과 종목코드이기 때문에 필요없는 column들은 제외해준다.
        code_df = code_df[['회사명', '종목코드']]

        # 한글로된 컬럼명을 영어로 바꿔준다.
        code_df = code_df.rename(columns={'회사명': 'name', '종목코드': 'code'})

        # 주식가격 검색
        def get_url(item_name, code_df):
            code = code_df.query("name=='{}'".format(item_name))['code'].to_string(index=False)
            url = 'http://finance.naver.com/item/sise_day.nhn?code={code}'.format(code=code)
            # print("요청 URL = {}".format(url))
            return url

            # item_name 일자데이터 url 가져오기

        url = get_url(item_name, code_df)

        self.stock_no.setText(url[-6:])

        # 일자 데이터를 담을 df라는 DataFrame 정의
        df = pd.DataFrame()

        # 1페이지에서 20페이지의 데이터만 가져오기
        for page in range(1, 29):
            pg_url = '{url}&page={page}'.format(url=url, page=page)
            df = df.append(pd.read_html(pg_url, header=0)[0], ignore_index=True)

            # df.dropna()를 이용해 결측값 있는 행 제거
        df = df.dropna()
        # 상위 5개 데이터 확인하기

        # 한글로 된 컬럼명을 영어로 바꿔줌
        df = df.rename(columns={'날짜': 'Date', '종가': 'Close', '전일비': 'Diff', '시가': 'Open', '고가': 'High', '저가': 'Low',
                                '거래량': 'Volume'})
        # 데이터의 타입을 int형으로 바꿔줌
        df[['Close', 'Diff', 'Open', 'High', 'Low', 'Volume']] \
            = df[['Close', 'Diff', 'Open', 'High', 'Low', 'Volume']].astype(int)
        # 컬럼명 'date'의 타입을 date로 바꿔줌
        df['Date'] = pd.to_datetime(df['Date'])
        # 일자(date)를 기준으로 오름차순 정렬
        df = df.sort_values(by=['Date'], ascending=True)
        # 상위 5개 데이터 확인
        df = df.set_index("Date")
        stock = df

        # Moving average
        ma5 = stock['Close'].rolling(window=5).mean()
        ma20 = stock['Close'].rolling(window=20).mean()
        ma60 = stock['Close'].rolling(window=60).mean()

        # Insert columns
        stock.insert(len(stock.columns), "MA5", ma5)
        stock.insert(len(stock.columns), "MA20", ma20)
        stock.insert(len(stock.columns), "MA60", ma60)

        # 골든크로스 찾기
        stock_tail = len(stock)

        stock1 = stock['MA20'] - stock['MA5'] < 0

        stock["gold"] = 0
        for i in range(0, stock_tail - 1):
            if stock1[i] == stock1[i + 1]:
                stock.iloc[i, 9] = 0
            else:
                stock.iloc[i, 9] = 1

        # Plot
        self.MplWidget.canvas.axes.clear()


        for i in range(0, stock_tail):
            if stock.iloc[i, 9] == 1:
               self.MplWidget.canvas.axes.plot(stock.index[i], stock.iloc[i, 6], c='red', marker="o", ms=6)
        self.MplWidget.canvas.axes.plot(stock.index, stock['Close'], color='black', linestyle='--', label='Adj Close')
        self.MplWidget.canvas.axes.plot(stock.index, stock['MA5'], color='red', label='MA5')
        self.MplWidget.canvas.axes.plot(stock.index, stock['MA20'], color='blue', label='MA20')
        self.MplWidget.canvas.axes.plot(stock.index, stock['MA60'], color='green', linestyle='--', label='MA60')
        self.MplWidget.canvas.axes.legend(loc='upper left')
        self.MplWidget.canvas.draw()

    def today_stock(self):
        # print(self.stock_no.text())
        html = requests.get('https://finance.naver.com/item/sise.nhn?code=' + str(self.stock_no.text()))
        soup = bs(html.text, 'html.parser')

        # 주가
        item_raw = soup.find(id="_nowVal")
        self.stock_price_now.setText(item_raw.get_text())

        # 상승율
        item_raw_2 = soup.find(id="_rate")
        signal = item_raw_2.get_text().strip()

        # 변동금액
        #item_raw_1 = soup.find(class_="tah p11 red01")

        if signal[0:1] == "-" :
           item_raw_1 = soup.find(class_="tah p11 nv01")
           self.stock_price_diff.setText("-"+ item_raw_1.get_text().strip())
        else:
            item_raw_1 = soup.find(class_="tah p11 red01")
            self.stock_price_diff.setText("+" + item_raw_1.get_text().strip())
        #print('+' + item_raw_1.get_text().strip())
        self.stock_price_diff_rate.setText(signal)

        threading.Timer(5, self.today_stock).start()

app = QApplication([])
window = MatplotlibWidget()
window.show()
app.exec_()


