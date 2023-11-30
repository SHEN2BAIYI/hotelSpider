import logging
import sys
import os
import datetime
import calendar
import threading
import time
import re
import socket

from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QFileDialog
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QPixmap
from PyQt5.QtCore import QThread, pyqtSignal, QThreadPool, QObject, Qt
from PIL import Image, ImageQt

from ui.mainWindow import *
from ui.log import *
from task import *
from utils.config import save_config, read_config
from utils.utils import info_format, logger


class Stream(QObject):
    log_info = pyqtSignal(str)

    def write(self, text):
        self.log_info.emit(text)


class Log(QMainWindow, LogWindow):
    def __init__(self):
        super(Log, self).__init__()
        self.setupUi(self)

        # 初始化窗口
        self._init_window()

        # 自定义输出
        self._connect_logger()

    def _init_window(self):
        # 一行四列
        self.model = QStandardItemModel(0, 2)

        # 设置表头
        self.model.setHorizontalHeaderLabels(['时间', '信息'])
        self.tableView.horizontalHeader().setStretchLastSection(True)
        self.tableView.setModel(self.model)

    def _on_update_text(self, text):

        text = text.split('$$')
        # self.tableView
        date = QStandardItem(text[0])
        info = QStandardItem(text[1].strip())

        self.model.insertRow(self.model.rowCount(), [date, info])
        self.tableView.scrollToBottom()

    def _connect_logger(self):
        formatter = logging.Formatter('%(asctime)-15s$$%(message)s')
        stream_handler = logging.StreamHandler(Stream(log_info=self._on_update_text))
        stream_handler.setLevel(logging.INFO)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)


class MyWindow(QMainWindow, SpiderWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        self.setupUi(self)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

        # 日志窗口
        self.log_window = Log()

        # 多线程任务监测
        self.task_list = []
        self.monitor = TaskMonitor(self.task_list)
        self.monitor.start()
        self.task_list.append(self.monitor)
        logger.info('多线程任务监测开始运行。')

        # 基础参数设置
        self.cwd = os.getcwd()          # 当前路径
        self.cfg_dict = {}              # 配置文件字典

        # 初始化流程
        self.__init_setting_params()    # 初始化设置界面
        self.__init_datetime()          # 初始化主页面时间
        self.__init_bind_event()        # 初始化主页面绑定事件

        self._info_display('界面端：初始化完毕。')

    ########################
    #      搜索相关函数      #
    ########################
    """ 搜索事件 """
    def _search_event(self):
        self._info_display('界面端：用户触发搜索事件。')
        # 不允许同时开启多个搜索事件
        if len(self.task_list) >= 2:
            self._info_display('界面端：已经有搜索事件在运行，不允许同时开启多个搜索事件。或等待后台清理正在运行的任务！！！')
            return

        # 开始搜索之前，需要先检查各个参数
        params = self.__gather_params()
        self._save_setting_params()

        # 如果检查成功，则开始运行检查程序
        if params:
            t = SearchTask(params)
            t.start()
            t.qr_code.connect(self._img_display)
            t.log_signal.connect(self._info_display)
            t.platform_signal.connect(self.platformLine.setText)
            self.task_list.append(t)

    """ 收集参数 """
    def __gather_params(self):
        # 主页面参数
        main = {
            'platform': self.platformBox.currentText(),
            'max_num_hotel': self.maxHotelLine.text(),
            'destination': self.destinationLine.text(),
            'in_year': self.inYearBox.currentText(),
            'in_month': self.inMonthBox.currentText(),
            'in_day': self.inDayBox.currentText(),
            'out_year': self.outYearBox.currentText(),
            'out_month': self.outMonthBox.currentText(),
            'out_day': self.outDayBox.currentText(),
        }

        # 设置页面参数
        setting = {
            'th_num': self.threadBox.currentText(),
            'port': self.portLine.text(),
            'web_path': self.webPathLine.text(),
            'driver_path': self.driverPathLine.text(),
            'output_path': self.outPathLine.text(),
        }

        params = {
            'main': main,
            'setting': setting
        }

        logger.info('界面端：成功收集参数。')
        return params

    ########################
    #       初始化函数       #
    ########################
    """ 初始化设置界面参数 """
    def __init_setting_params(self):
        # 设置默认参数
        default_dict = {
            'cfg_path': './config/Config.cfg',
            'driver_path': './source/static/chromedriver.exe',
            'web_path': 'C:/Program Files/Google/Chrome/Application/chrome.exe',
            'output_path': './result/',
            'port': 8080,
        }

        # 判断是否有配置文件
        if not os.path.exists(default_dict['cfg_path']):
            self._info_display('界面端：未找到配置文件，将尝试设置默认参数。')
        else:
            # 读取配置文件
            self.cfg_dict = read_config()

            # 配置基础设置
            if 'driver_path' in self.cfg_dict['BASE'].keys():
                default_dict['driver_path'] = self.cfg_dict['BASE']['driver_path']

            if 'output_path' in self.cfg_dict['BASE'].keys():
                default_dict['output_path'] = self.cfg_dict['BASE']['output_path']

            if 'port' in self.cfg_dict['BASE'].keys():
                default_dict['port'] = self.cfg_dict['BASE']['port']

            if 'web_path' in self.cfg_dict['BASE'].keys():
                default_dict['web_path'] = self.cfg_dict['BASE']['web_path']

        # 在界面端设置参数
        self.webPathLine.setText(default_dict['web_path'])
        self.driverPathLine.setText(default_dict['driver_path'])
        self.outPathLine.setText(default_dict['output_path'])
        self.portLine.setText(str(default_dict['port']))

        self._info_display('界面端：设置界面参数初始化完毕。')

    """ 初始化主页面时间 """
    def __init_datetime(self):
        """ 主要是根据当前日期初始化日期面板 """
        # 获取当月天数
        today = datetime.datetime.today()
        month_range = calendar.monthrange(today.year, today.month)[1]

        # 根据当天日期初始化入住时间和退房时间的月份
        out_month = today.month + 1 if today.day == month_range else today.month
        out_year = today.year + 1 if out_month == 13 else today.year
        out_day = 1 if today.day == month_range else today.day + 1
        out_month = 1 if out_month == 13 else out_month

        # 根据相应的月份获得天数
        month_range_out = calendar.monthrange(out_year, out_month)[1]

        # 初始化组件
        self.inMonthBox.setCurrentIndex(today.month - 1)
        self.inDayBox.clear()
        self.inDayBox.addItems([str(i + 1) for i in range(month_range)])
        self.inDayBox.setCurrentIndex(today.day - 1)

        self.inYearBox.clear()
        self.inYearBox.addItems([str(i) for i in [today.year, today.year + 1]])

        self.outMonthBox.setCurrentIndex(out_month - 1)
        self.outDayBox.clear()
        self.outDayBox.addItems([str(i + 1) for i in range(month_range_out)])
        self.outDayBox.setCurrentIndex(out_day - 1)

        self.outYearBox.clear()
        if today.year == out_year:
            self.outYearBox.addItems([str(i) for i in [out_year, out_year + 1]])
        else:
            self.outYearBox.addItem(str(out_year))

        self._info_display('界面端：主页面时间初始化完毕。')

    """ 初始化主页面绑定事件 """
    def __init_bind_event(self):
        # 浏览器路径选择
        self.webChooseButton.clicked.connect(lambda: self.__choose_file(self.webPathLine, False))
        # 驱动路径选择
        self.driverChooseButton.clicked.connect(lambda: self.__choose_file(self.driverPathLine, False))
        # 输出路径选择
        self.outChooseButton.clicked.connect(lambda: self.__choose_file(self.outPathLine, True))
        # 设置界面参数保存
        self.storeButton.clicked.connect(self._save_setting_params)
        # 主页面时间刷新（年月改变，会带动日期数量改变）
        self.inYearBox.currentIndexChanged.connect(lambda: self.__refresh_days_num(True))
        self.inMonthBox.currentIndexChanged.connect(lambda: self.__refresh_days_num(True))
        self.outYearBox.currentIndexChanged.connect(lambda: self.__refresh_days_num(False))
        self.outMonthBox.currentIndexChanged.connect(lambda: self.__refresh_days_num(False))
        # 任务检测线程 log 输出
        self.monitor.log_signal.connect(self._info_display)

        # 搜索事件
        self.searchButton.clicked.connect(self._search_event)

        # 日志窗口
        self.actionLog.triggered.connect(self.log_window.show)

        self._info_display('界面端：主页面绑定事件初始化完毕。')

    ########################
    #       功能性函数       #
    ########################
    """ 保存设置界面参数 """
    def _save_setting_params(self):
        """ 设置存储事件 """
        # 获取基础设置
        self.cfg_dict = {
            'BASE': {}
        }

        # 开放端口
        if self.portLine.text():
            self.cfg_dict['BASE']['port'] = self.portLine.text()
        else:
            self.cfg_dict['BASE']['port'] = 8080

        # 浏览器路径
        if self.webPathLine.text():
            self.cfg_dict['BASE']['web_path'] = self.webPathLine.text()
        else:
            self.cfg_dict['BASE']['web_path'] = 'C:/Program Files/Google/Chrome/Application/chrome.exe'

        # 驱动路径
        if self.driverPathLine.text():
            self.cfg_dict['BASE']['driver_path'] = self.driverPathLine.text()
        else:
            self.cfg_dict['BASE']['driver_path'] = './source/static/chromedriver.exe'

        # 输出路径
        if self.outPathLine.text():
            self.cfg_dict['BASE']['output_path'] = self.outPathLine.text()
        else:
            self.cfg_dict['BASE']['output_path'] = './result/'

        # 保存
        save_config(self.cfg_dict)
        self._info_display('界面端：设置界面参数保存成功。')

    """ 选择文件或者文件夹，并传递到界面 """
    def __choose_file(self, line_edit, is_dir=False):
        if is_dir:
            file_name = QFileDialog.getExistingDirectory(self, "选取文件夹", self.cwd)
        else:
            file_name, _ = QFileDialog.getOpenFileName(self, "选取文件", self.cwd, 'Exe files(*.exe)')

        # 选择文件并传递给 line_edit
        if file_name:
            line_edit.setText(file_name)

        self._info_display('界面端：触发选择文件事件，路径选择为：{}。'.format(file_name))

    """ 刷新日期 """
    def __refresh_days_num(self, is_in):
        # 如果月份改变, 日期范围也要改变
        if is_in:
            current_year = int(self.inYearBox.currentText())
            current_month = int(self.inMonthBox.currentText())
        else:
            current_year = int(self.outYearBox.currentText())
            current_month = int(self.outMonthBox.currentText())

        month_range = calendar.monthrange(current_year, current_month)[1]

        if is_in:
            self.inDayBox.clear()
            self.inDayBox.addItems([str(i + 1) for i in range(month_range)])
        else:
            self.outDayBox.clear()
            self.outDayBox.addItems([str(i + 1) for i in range(month_range)])

        self._info_display('界面端：用户改变了年份或月份，现在时间为 {}/{}，当月有共 {} 日。'.format(
            current_year, current_month, month_range
        ))

    """ 信息分别展示到 textBrowser 和 log 窗口 """
    def _info_display(self, info):
        logger.info(info)
        self.textBrowser.append(info_format(info))

    """ 展示二维码 """
    def _img_display(self, img):
        try:
            img = img[-1]
            img = ImageQt.toqpixmap(img)
            self.imgView.setPixmap(img)
        except KeyError:
            return

    """ 关闭窗口 """
    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        reply = QMessageBox.question(self, '提示', '是否要关闭所有窗口？',
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)
        if reply == QMessageBox.Yes:
            a0.accept()
            sys.exit(0)
        else:
            a0.ignore()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWin = MyWindow()
    myWin.show()
    sys.exit(app.exec_())


