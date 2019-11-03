# ------------------------------------------------------
# ---------------------- main.py -----------------------
# ------------------------------------------------------
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
from PyQt5 import QtCore
from matplotlib.backends.backend_qt5agg import (NavigationToolbar2QT as NavigationToolbar)
import matplotlib.pyplot as plt  # 그래프 시각화 패키지

# numpy를 이용하기 위하여 mumpy 모듈을 읽어들인다.
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

class MatplotlibWidget(QMainWindow):

    def __init__(self):
        QMainWindow.__init__(self)
        loadUi("qt_regress.ui", self)
        self.setWindowTitle("PyQt5 : Data Regression")
        self.showMaximized()
        self.setWindowFlags(QtCore.Qt.Window |
                           QtCore.Qt.CustomizeWindowHint |
                           QtCore.Qt.WindowMinimizeButtonHint |
                           QtCore.Qt.WindowMaximizeButtonHint |
                           QtCore.Qt.WindowCloseButtonHint |
                           QtCore.Qt.WindowStaysOnTopHint
                           )
        self.file_load_button.clicked.connect(self.getCSV)
        self.regression_button.clicked.connect(self.regress)
        self.plot_button.clicked.connect(self.plot_graph)

        self.radio_button_1.clicked.connect(self.radioButtonClicked)
        self.radio_button_1.setChecked(True)
        self.radio_button_2.clicked.connect(self.radioButtonClicked)
        self.radio_button_3.clicked.connect(self.radioButtonClicked)
        # Matplotlib 네비게이션 위젯 생성
        self.addToolBar(NavigationToolbar(self.MplWidget.canvas, self))
        #Status Bar 위젯 생성
        self.statusBar = QStatusBar(self)
        self.setStatusBar(self.statusBar)

    def radioButtonClicked(self):
        poly_d = 1
        if self.radio_button_1.isChecked():
            poly_d = 1
        elif self.radio_button_2.isChecked():
            poly_d = 2
        elif self.radio_button_3.isChecked():
            poly_d = 3

        self.coeff.setText(str(poly_d))

        self.statusBar.showMessage('다항식 차수 : ' + str(poly_d) + ' 차항')

    def getCSV(self) :
        fname = QFileDialog.getOpenFileName(self)
        self.data_train = pd.read_csv(fname[0], encoding='EUC-KR')

        self.statusBar.showMessage('Load / ' + 'File Name : ' + str(fname[0]))

    def regress(self):

        # REGRESS 파일 읽기
        fname_1 = QFileDialog.getOpenFileName(self)
        self.data_raw = pd.read_csv(fname_1[0], encoding='EUC-KR')

        # 최소값 미만 삭제하기
        self.data_train_1 = self.data_train[self.data_train.x > float(self.x_min.text())]

        # DATAFRAME에서 X와 Y값 추출하기
        x = self.data_train_1['x']
        y = self.data_train_1['y']

        # REGRESS 함수 계산하기
        poly_d = float(self.coeff.text())
        fp1 = np.polyfit(x, y, poly_d)
        f1 = np.poly1d(fp1)

        # REGRESS 함수에서 선택된 1차항,2차항,3차항일 경우 회귀계산하기
        if poly_d == 1:
            self.data_raw['y1'] = f1[1] *self.data_raw['x'] + f1[0] *self.data_raw['x'] ** 0
        elif poly_d == 2:
            self.data_raw['y1'] = f1[2] * self.data_raw['x'] ** 2 + f1[1] * self.data_raw['x'] ** 1 + f1[0] * self.data_raw['x'] ** 0
        elif poly_d == 3:
            self.data_raw['y1'] = f1[3] * self.data_raw['x'] ** 3 + f1[2] * self.data_raw['x'] ** 2 + f1[1] * self.data_raw['x'] ** 1 + f1[
                0] * self.data_raw['x'] ** 0

        # 회구분석된 DATAFRAME 저장하기
        self.data_raw.to_csv(fname_1[0], index=False)

        # 회귀분석된 DATA 순서에 따라 LINE PLOT하기

        # X,Y,Y1등 회귀분석된 자료 추출하기
        x = self.data_raw['no']
        y = self.data_raw['y']
        y1 = self.data_raw['y1']

        # 캔버스 기존 그래프 지우기
        self.MplWidget.canvas.axes.clear()

        # 캔버스에 그래프 그리기
        self.MplWidget.canvas.axes.plot( x, y, label='Raw Data', color='b')
        self.MplWidget.canvas.axes.plot(x,y1, label='Regress Data', color='r')

        # 캔버스에 그래프 LEGEND등 치장하기
        self.MplWidget.canvas.axes.legend(loc='upper left')
        self.MplWidget.canvas.axes.grid()
        self.MplWidget.canvas.draw()

        # 기술통계 값 나타내기
        self.df_describe_note.setText(str(self.data_raw.describe().iloc[0:8,2:4]))

        # 상태바 나타내기
        self.statusBar.showMessage('Regress / ' + 'File Name : ' + str(fname_1[0]))

    def plot_graph(self) :

        # 최소값 미만 삭제하기
        self.data_train_1=self.data_train[self.data_train.x > float(self.x_min.text())]

        # DATAFRAME에서 X와 Y값 추출하기
        x = self.data_train_1['x']
        y = self.data_train_1['y']

        # REGRESS 함수 계산하기
        poly_d = float(self.coeff.text())
        fp1 = np.polyfit(x, y, poly_d)
        f1 = np.poly1d(fp1)

        # 캔버스 기존 그래프 지우기
        self.MplWidget.canvas.axes.clear()

        # 캔버스에 그래프 그리기
        self.MplWidget.canvas.axes.scatter(x, y, label='Raw Data', color='r')
        self.MplWidget.canvas.axes.plot(x, f1(x), label='Fitting Line', color='b')

        # 캔버스에 그래프 LEGEND등 치장하기
        self.MplWidget.canvas.axes.legend(loc='upper left')
        self.MplWidget.canvas.axes.grid()
        self.MplWidget.canvas.draw()

        # REGRESS 함수에서 선택된 1차항,2차항,3차항일 경우 회귀계산하기
        if poly_d == 1:
            formula = str(f1[1]) + " * X + " + str(f1[0])
        elif poly_d == 2:
            formula = str(f1[2]) + " * X^2 + " + str(f1[1]) + " * X + " + str(f1[0])
        elif poly_d == 3:
            formula = str(f1[3]) + " * X^3 + " + str(f1[2]) + " * X^2 + " + str(f1[1]) + " * X + " + str(f1[0])

        # 회귀분석된 회귀계수 나타내기
        self.graphic_formula.setText(formula)

        # 회귀분석된 Y,Y1의 기술통계값 계산하기
        self.df_describe_note.setText(str(self.data_train.describe()))

        # 상태바 나타내기
        self.statusBar.showMessage('Plot / ' + 'Tranining Data Plot : ' + str(poly_d) + ' 차항' )

app = QApplication([])
window = MatplotlibWidget()
window.show()
app.exec_()
