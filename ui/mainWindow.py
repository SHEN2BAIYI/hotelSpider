# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainWindow.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class SpiderWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(740, 552)
        MainWindow.setMinimumSize(QtCore.QSize(740, 552))
        MainWindow.setMaximumSize(QtCore.QSize(740, 552))
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setEnabled(True)
        self.centralwidget.setObjectName("centralwidget")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(0, 0, 741, 301))
        self.tabWidget.setTabPosition(QtWidgets.QTabWidget.West)
        self.tabWidget.setTabShape(QtWidgets.QTabWidget.Rounded)
        self.tabWidget.setElideMode(QtCore.Qt.ElideNone)
        self.tabWidget.setMovable(False)
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.platformBox = QtWidgets.QComboBox(self.tab)
        self.platformBox.setGeometry(QtCore.QRect(120, 20, 51, 22))
        self.platformBox.setObjectName("platformBox")
        self.platformBox.addItem("")
        self.platformBox.addItem("")
        self.platformBox.addItem("")
        self.platformBox.addItem("")
        self.label_2 = QtWidgets.QLabel(self.tab)
        self.label_2.setGeometry(QtCore.QRect(85, 20, 31, 21))
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(self.tab)
        self.label_3.setGeometry(QtCore.QRect(60, 120, 51, 21))
        self.label_3.setObjectName("label_3")
        self.label_5 = QtWidgets.QLabel(self.tab)
        self.label_5.setGeometry(QtCore.QRect(60, 170, 51, 21))
        self.label_5.setObjectName("label_5")
        self.inMonthBox = QtWidgets.QComboBox(self.tab)
        self.inMonthBox.setGeometry(QtCore.QRect(200, 120, 41, 22))
        self.inMonthBox.setObjectName("inMonthBox")
        self.inMonthBox.addItem("")
        self.inMonthBox.addItem("")
        self.inMonthBox.addItem("")
        self.inMonthBox.addItem("")
        self.inMonthBox.addItem("")
        self.inMonthBox.addItem("")
        self.inMonthBox.addItem("")
        self.inMonthBox.addItem("")
        self.inMonthBox.addItem("")
        self.inMonthBox.addItem("")
        self.inMonthBox.addItem("")
        self.inMonthBox.addItem("")
        self.label_6 = QtWidgets.QLabel(self.tab)
        self.label_6.setGeometry(QtCore.QRect(250, 120, 16, 21))
        self.label_6.setObjectName("label_6")
        self.inDayBox = QtWidgets.QComboBox(self.tab)
        self.inDayBox.setGeometry(QtCore.QRect(270, 120, 41, 22))
        self.inDayBox.setObjectName("inDayBox")
        self.label_7 = QtWidgets.QLabel(self.tab)
        self.label_7.setGeometry(QtCore.QRect(320, 120, 16, 21))
        self.label_7.setObjectName("label_7")
        self.label_8 = QtWidgets.QLabel(self.tab)
        self.label_8.setGeometry(QtCore.QRect(320, 170, 16, 21))
        self.label_8.setObjectName("label_8")
        self.outMonthBox = QtWidgets.QComboBox(self.tab)
        self.outMonthBox.setGeometry(QtCore.QRect(200, 170, 41, 22))
        self.outMonthBox.setObjectName("outMonthBox")
        self.outMonthBox.addItem("")
        self.outMonthBox.addItem("")
        self.outMonthBox.addItem("")
        self.outMonthBox.addItem("")
        self.outMonthBox.addItem("")
        self.outMonthBox.addItem("")
        self.outMonthBox.addItem("")
        self.outMonthBox.addItem("")
        self.outMonthBox.addItem("")
        self.outMonthBox.addItem("")
        self.outMonthBox.addItem("")
        self.outMonthBox.addItem("")
        self.label_9 = QtWidgets.QLabel(self.tab)
        self.label_9.setGeometry(QtCore.QRect(250, 170, 16, 21))
        self.label_9.setObjectName("label_9")
        self.outDayBox = QtWidgets.QComboBox(self.tab)
        self.outDayBox.setGeometry(QtCore.QRect(270, 170, 41, 22))
        self.outDayBox.setObjectName("outDayBox")
        self.label_10 = QtWidgets.QLabel(self.tab)
        self.label_10.setGeometry(QtCore.QRect(70, 70, 41, 21))
        self.label_10.setObjectName("label_10")
        self.destinationLine = QtWidgets.QLineEdit(self.tab)
        self.destinationLine.setGeometry(QtCore.QRect(120, 70, 211, 20))
        self.destinationLine.setObjectName("destinationLine")
        self.searchButton = QtWidgets.QPushButton(self.tab)
        self.searchButton.setGeometry(QtCore.QRect(110, 220, 71, 41))
        self.searchButton.setObjectName("searchButton")
        self.clearButton = QtWidgets.QPushButton(self.tab)
        self.clearButton.setGeometry(QtCore.QRect(240, 220, 71, 41))
        self.clearButton.setObjectName("clearButton")
        self.label_12 = QtWidgets.QLabel(self.tab)
        self.label_12.setGeometry(QtCore.QRect(180, 120, 16, 21))
        self.label_12.setObjectName("label_12")
        self.label_13 = QtWidgets.QLabel(self.tab)
        self.label_13.setGeometry(QtCore.QRect(180, 170, 16, 21))
        self.label_13.setObjectName("label_13")
        self.inYearBox = QtWidgets.QComboBox(self.tab)
        self.inYearBox.setGeometry(QtCore.QRect(120, 120, 51, 22))
        self.inYearBox.setObjectName("inYearBox")
        self.outYearBox = QtWidgets.QComboBox(self.tab)
        self.outYearBox.setGeometry(QtCore.QRect(120, 170, 51, 22))
        self.outYearBox.setObjectName("outYearBox")
        self.imgView = QtWidgets.QLabel(self.tab)
        self.imgView.setGeometry(QtCore.QRect(430, 120, 191, 151))
        self.imgView.setText("")
        self.imgView.setObjectName("imgView")
        self.label_16 = QtWidgets.QLabel(self.tab)
        self.label_16.setGeometry(QtCore.QRect(380, 20, 51, 21))
        self.label_16.setObjectName("label_16")
        self.platformLine = QtWidgets.QLineEdit(self.tab)
        self.platformLine.setGeometry(QtCore.QRect(440, 20, 211, 20))
        self.platformLine.setReadOnly(True)
        self.platformLine.setObjectName("platformLine")
        self.label_17 = QtWidgets.QLabel(self.tab)
        self.label_17.setGeometry(QtCore.QRect(250, 20, 41, 21))
        self.label_17.setObjectName("label_17")
        self.maxHotelLine = QtWidgets.QLineEdit(self.tab)
        self.maxHotelLine.setGeometry(QtCore.QRect(290, 20, 41, 20))
        self.maxHotelLine.setObjectName("maxHotelLine")
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.tabWidget_2 = QtWidgets.QTabWidget(self.tab_2)
        self.tabWidget_2.setGeometry(QtCore.QRect(0, 0, 721, 301))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tabWidget_2.sizePolicy().hasHeightForWidth())
        self.tabWidget_2.setSizePolicy(sizePolicy)
        self.tabWidget_2.setAutoFillBackground(False)
        self.tabWidget_2.setObjectName("tabWidget_2")
        self.tab_3 = QtWidgets.QWidget()
        self.tab_3.setObjectName("tab_3")
        self.label = QtWidgets.QLabel(self.tab_3)
        self.label.setGeometry(QtCore.QRect(102, 100, 71, 21))
        self.label.setObjectName("label")
        self.driverPathLine = QtWidgets.QLineEdit(self.tab_3)
        self.driverPathLine.setGeometry(QtCore.QRect(180, 100, 331, 21))
        self.driverPathLine.setReadOnly(True)
        self.driverPathLine.setObjectName("driverPathLine")
        self.driverChooseButton = QtWidgets.QToolButton(self.tab_3)
        self.driverChooseButton.setGeometry(QtCore.QRect(530, 100, 51, 21))
        self.driverChooseButton.setObjectName("driverChooseButton")
        self.storeButton = QtWidgets.QPushButton(self.tab_3)
        self.storeButton.setGeometry(QtCore.QRect(610, 210, 61, 41))
        self.storeButton.setObjectName("storeButton")
        self.label_11 = QtWidgets.QLabel(self.tab_3)
        self.label_11.setGeometry(QtCore.QRect(90, 140, 71, 21))
        self.label_11.setObjectName("label_11")
        self.outPathLine = QtWidgets.QLineEdit(self.tab_3)
        self.outPathLine.setGeometry(QtCore.QRect(180, 140, 331, 21))
        self.outPathLine.setReadOnly(True)
        self.outPathLine.setObjectName("outPathLine")
        self.outChooseButton = QtWidgets.QToolButton(self.tab_3)
        self.outChooseButton.setGeometry(QtCore.QRect(530, 140, 51, 21))
        self.outChooseButton.setObjectName("outChooseButton")
        self.label_4 = QtWidgets.QLabel(self.tab_3)
        self.label_4.setGeometry(QtCore.QRect(100, 60, 71, 21))
        self.label_4.setObjectName("label_4")
        self.webPathLine = QtWidgets.QLineEdit(self.tab_3)
        self.webPathLine.setGeometry(QtCore.QRect(180, 60, 331, 21))
        self.webPathLine.setReadOnly(True)
        self.webPathLine.setObjectName("webPathLine")
        self.webChooseButton = QtWidgets.QToolButton(self.tab_3)
        self.webChooseButton.setGeometry(QtCore.QRect(530, 60, 51, 21))
        self.webChooseButton.setObjectName("webChooseButton")
        self.label_14 = QtWidgets.QLabel(self.tab_3)
        self.label_14.setGeometry(QtCore.QRect(110, 20, 51, 21))
        self.label_14.setObjectName("label_14")
        self.portLine = QtWidgets.QLineEdit(self.tab_3)
        self.portLine.setGeometry(QtCore.QRect(180, 20, 41, 21))
        self.portLine.setReadOnly(True)
        self.portLine.setObjectName("portLine")
        self.label_15 = QtWidgets.QLabel(self.tab_3)
        self.label_15.setGeometry(QtCore.QRect(390, 20, 51, 21))
        self.label_15.setObjectName("label_15")
        self.threadBox = QtWidgets.QComboBox(self.tab_3)
        self.threadBox.setGeometry(QtCore.QRect(460, 20, 51, 22))
        self.threadBox.setObjectName("threadBox")
        self.threadBox.addItem("")
        self.threadBox.addItem("")
        self.threadBox.addItem("")
        self.threadBox.addItem("")
        self.threadBox.addItem("")
        self.threadBox.addItem("")
        self.threadBox.addItem("")
        self.threadBox.addItem("")
        self.tabWidget_2.addTab(self.tab_3, "")
        self.tab_4 = QtWidgets.QWidget()
        self.tab_4.setObjectName("tab_4")
        self.tabWidget_2.addTab(self.tab_4, "")
        self.tab_5 = QtWidgets.QWidget()
        self.tab_5.setObjectName("tab_5")
        self.tabWidget_2.addTab(self.tab_5, "")
        self.tabWidget.addTab(self.tab_2, "")
        self.textBrowser = QtWidgets.QTextBrowser(self.centralwidget)
        self.textBrowser.setGeometry(QtCore.QRect(0, 300, 741, 211))
        self.textBrowser.setObjectName("textBrowser")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 740, 23))
        self.menubar.setObjectName("menubar")
        self.menu = QtWidgets.QMenu(self.menubar)
        self.menu.setObjectName("menu")
        MainWindow.setMenuBar(self.menubar)
        self.actionLog = QtWidgets.QAction(MainWindow)
        self.actionLog.setObjectName("actionLog")
        self.menu.addAction(self.actionLog)
        self.menubar.addAction(self.menu.menuAction())

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        self.tabWidget_2.setCurrentIndex(0)
        self.threadBox.setCurrentIndex(3)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "HotelSpider"))
        self.platformBox.setItemText(0, _translate("MainWindow", "全体"))
        self.platformBox.setItemText(1, _translate("MainWindow", "携程"))
        self.platformBox.setItemText(2, _translate("MainWindow", "去哪儿"))
        self.platformBox.setItemText(3, _translate("MainWindow", "美团"))
        self.label_2.setText(_translate("MainWindow", "平台"))
        self.label_3.setText(_translate("MainWindow", "入住时间"))
        self.label_5.setText(_translate("MainWindow", "退房时间"))
        self.inMonthBox.setItemText(0, _translate("MainWindow", "1"))
        self.inMonthBox.setItemText(1, _translate("MainWindow", "2"))
        self.inMonthBox.setItemText(2, _translate("MainWindow", "3"))
        self.inMonthBox.setItemText(3, _translate("MainWindow", "4"))
        self.inMonthBox.setItemText(4, _translate("MainWindow", "5"))
        self.inMonthBox.setItemText(5, _translate("MainWindow", "6"))
        self.inMonthBox.setItemText(6, _translate("MainWindow", "7"))
        self.inMonthBox.setItemText(7, _translate("MainWindow", "8"))
        self.inMonthBox.setItemText(8, _translate("MainWindow", "9"))
        self.inMonthBox.setItemText(9, _translate("MainWindow", "10"))
        self.inMonthBox.setItemText(10, _translate("MainWindow", "11"))
        self.inMonthBox.setItemText(11, _translate("MainWindow", "12"))
        self.label_6.setText(_translate("MainWindow", "月"))
        self.label_7.setText(_translate("MainWindow", "日"))
        self.label_8.setText(_translate("MainWindow", "日"))
        self.outMonthBox.setItemText(0, _translate("MainWindow", "1"))
        self.outMonthBox.setItemText(1, _translate("MainWindow", "2"))
        self.outMonthBox.setItemText(2, _translate("MainWindow", "3"))
        self.outMonthBox.setItemText(3, _translate("MainWindow", "4"))
        self.outMonthBox.setItemText(4, _translate("MainWindow", "5"))
        self.outMonthBox.setItemText(5, _translate("MainWindow", "6"))
        self.outMonthBox.setItemText(6, _translate("MainWindow", "7"))
        self.outMonthBox.setItemText(7, _translate("MainWindow", "8"))
        self.outMonthBox.setItemText(8, _translate("MainWindow", "9"))
        self.outMonthBox.setItemText(9, _translate("MainWindow", "10"))
        self.outMonthBox.setItemText(10, _translate("MainWindow", "11"))
        self.outMonthBox.setItemText(11, _translate("MainWindow", "12"))
        self.label_9.setText(_translate("MainWindow", "月"))
        self.label_10.setText(_translate("MainWindow", "目的地"))
        self.searchButton.setText(_translate("MainWindow", "查询"))
        self.clearButton.setText(_translate("MainWindow", "清除"))
        self.label_12.setText(_translate("MainWindow", "年"))
        self.label_13.setText(_translate("MainWindow", "年"))
        self.label_16.setText(_translate("MainWindow", "当前平台"))
        self.label_17.setText(_translate("MainWindow", "酒店数"))
        self.maxHotelLine.setText(_translate("MainWindow", "50"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("MainWindow", "主页面"))
        self.label.setText(_translate("MainWindow", "控制器路径"))
        self.driverChooseButton.setText(_translate("MainWindow", "..."))
        self.storeButton.setText(_translate("MainWindow", "保存设置"))
        self.label_11.setText(_translate("MainWindow", "文件输出路径"))
        self.outChooseButton.setText(_translate("MainWindow", "..."))
        self.label_4.setText(_translate("MainWindow", "浏览器路径"))
        self.webChooseButton.setText(_translate("MainWindow", "..."))
        self.label_14.setText(_translate("MainWindow", "开放端口"))
        self.portLine.setText(_translate("MainWindow", "8080"))
        self.label_15.setText(_translate("MainWindow", "线程数量"))
        self.threadBox.setItemText(0, _translate("MainWindow", "1"))
        self.threadBox.setItemText(1, _translate("MainWindow", "2"))
        self.threadBox.setItemText(2, _translate("MainWindow", "3"))
        self.threadBox.setItemText(3, _translate("MainWindow", "4"))
        self.threadBox.setItemText(4, _translate("MainWindow", "5"))
        self.threadBox.setItemText(5, _translate("MainWindow", "6"))
        self.threadBox.setItemText(6, _translate("MainWindow", "7"))
        self.threadBox.setItemText(7, _translate("MainWindow", "8"))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_3), _translate("MainWindow", "基础设置"))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_4), _translate("MainWindow", "携程设置"))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_5), _translate("MainWindow", "其他设置"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("MainWindow", "设置"))
        self.menu.setTitle(_translate("MainWindow", "菜单"))
        self.actionLog.setText(_translate("MainWindow", "Log"))
