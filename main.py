import logging
import sys
import os
import datetime
import calendar
import threading
import time
import re

from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QFileDialog
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import QThread, pyqtSignal, QThreadPool, QObject
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

        # Log Window
        self.log_window = Log()

        # 多线程任务监测
        self.task_list = []
        self.monitor = TaskMonitor(self.task_list)
        self.monitor.start()
        self.task_list.append(self.monitor)
        logger.info('多线程任务监测开始运行。')

        # 基础设置
        self.cwd = os.getcwd()      # 当前路径

        # 初始化流程
        self._setting_init_event()  # 初始化设置界面
        self._init_datetime()       # 初始化主页面时间
        self._bind_event()          # 初始化主页面绑定事件

        logger.info('用户成功进入界面，并完成初始化。')

    def _check_params(self):
        params = self._gather_params()

        # 检查主页面目的地
        if not params['main']['destination'].strip():
            logger.info('用户目的地输入为空。')
            self.textBrowser.append(info_format('目的地为空，请重新输入目的地。'))
            return False

        # 检查主页面时间
        in_time = time.strptime('{}-{}-{}'.format(params['main']['in_year'],
                                                  params['main']['in_month'],
                                                  params['main']['in_day']),
                                '%Y-%m-%d')
        out_time = time.strptime('{}-{}-{}'.format(params['main']['out_year'],
                                                   params['main']['out_month'],
                                                   params['main']['out_day']),
                                 '%Y-%m-%d')

        in_time = int(time.mktime(in_time))
        out_time = int(time.mktime(out_time))

        if in_time >= out_time:
            logger.info('用户选择时间有误，请重新选择。')
            self.textBrowser.append(info_format('用户选择时间有误，请重新选择。'))
            return False

        # 检查设置界面路径
        if not params['setting']['driver_path'].strip():
            logger.info('用户没有选择控制器路径。')
            self.textBrowser.append(info_format('驱动路径为空，请重新选择驱动路径。'))
            return False
        elif not os.path.exists(params['setting']['driver_path']):
            logger.info('用户选择的路径没有找到驱动。')
            self.textBrowser.append(info_format('没有找到驱动，请重新选择驱动路径'))
            return False

        if not params['setting']['output_path'].strip():
            logger.info('用户没有选择保存路径。')
            self.textBrowser.append(info_format('保存路径为空，请重新选择保存路径。'))
            return False

        return params

    def _gather_params(self):
        # 主页面参数
        main = {
            'platform': self.pingtai.currentText(),
            'max_hotel_num': self.lineEdit_5.text(),
            'order': self.pingtai_2.currentText(),
            'destination': self.lineEdit_2.text(),
            'in_year': self.comboBox_5.currentText(),
            'in_month': self.comboBox.currentText(),
            'in_day': self.comboBox_2.currentText(),
            'out_year': self.comboBox_6.currentText(),
            'out_month': self.comboBox_3.currentText(),
            'out_day': self.comboBox_4.currentText(),
        }

        # 设置页面参数
        setting = {
            'driver_path': self.lineEdit.text(),
            'output_path': self.lineEdit_3.text()
        }

        params = {
            'main': main,
            'setting': setting
        }

        logger.info('读取界面中所有配置成功。')
        return params

    def _bind_event(self):
        self.chooseButton.clicked.connect(self._tb1_event)
        self.chooseButton_2.clicked.connect(self._tb2_event)
        self.storeButton.clicked.connect(self._setting_store_event)
        self.comboBox.currentIndexChanged.connect(lambda: self._refresh_days_num(True))
        self.comboBox_3.currentIndexChanged.connect(lambda: self._refresh_days_num(False))
        self.comboBox_5.currentIndexChanged.connect(lambda: self._refresh_days_num(True))
        self.comboBox_6.currentIndexChanged.connect(lambda: self._refresh_days_num(False))
        self.searchButton.clicked.connect(self._search_event)
        self.storeButton_2.clicked.connect(self._log_window_show)

        self.monitor.log_signal.connect(self._info_display)

        logger.info('界面组件槽函数绑定成功。')

    def _search_event(self):
        # 不允许同时开启多个搜索事件
        if len(self.task_list) >= 2:
            logger.info('不允许同时开启多个搜索事件。')
            self.textBrowser.append('任务正在运行中，请在完成后再重新开始。')
            return

        # 开始搜索之前，需要先检查各个参数
        params = self._check_params()

        # 如果检查成功，则开始运行检查程序
        if params:
            logger.info('界面参数检查成功，开始进行搜索程序。')
            t = SearchTask(params)
            t.start()
            t.qr_code.connect(self._img_display)
            t.log_signal.connect(self._info_display)
            t.platform_signal.connect(self._platform_display)
            self.task_list.append(t)
            logger.info('用户成功开始搜索事件。')

    def _test_event(self):
        for i in range(5):
            t = CountTask((i + 1) * 5, i)
            t.start()
            t.log_signal.connect(self._info_display)
            self.task_list.append(t)

    def _tb1_event(self):
        """ 第一个 toolButton 的事件, 选择 driver_path """

        file_name, _ = QFileDialog.getOpenFileName(self, "选取文件", self.cwd, 'Exe files(*.exe)')

        # 选择文件并传递给 line_edit
        if file_name:
            self.lineEdit.setText(file_name)

        logger.info('触发选择驱动路径事件，路径选择为：{}。'.format(file_name))

    def _tb2_event(self):
        """ 第二个 toolButton 的事件, 选择 output_path """

        output_dir = QFileDialog.getExistingDirectory(self, "选取文件夹", self.cwd)

        if output_dir:
            self.lineEdit_3.setText(output_dir)

        logger.info('触发选择输出文件路径事件，路径选择为：{}。'.format(output_dir))

    def _setting_store_event(self):
        """ 设置存储事件 """
        # 获取基础设置
        self.cfg_dict = {
            'BASE': {}
        }

        if self.lineEdit.text():
            self.cfg_dict['BASE']['driver_path'] = self.lineEdit.text()

        if self.lineEdit_3.text():
            self.cfg_dict['BASE']['output_path'] = self.lineEdit_3.text()

        self.textBrowser.append(info_format('基础设置保存完毕.'))
        logger.info('基础设置信息保存完毕。')

        # 保存
        save_config(self.cfg_dict)

        logger.info('用户完成了设置界面信息的保存。')

    def _setting_init_event(self):
        """ 设置初始化事件 """
        # 读取参数
        self.cfg_dict = read_config()

        if not self.cfg_dict:
            logger.info('未成功读取设置参数，请自行进行设置并保存。')
            return

        # 配置基础设置
        if 'driver_path' in self.cfg_dict['BASE'].keys():
            self.lineEdit.setText(self.cfg_dict['BASE']['driver_path'])

        if 'output_path' in self.cfg_dict['BASE'].keys():
            self.lineEdit_3.setText(self.cfg_dict['BASE']['output_path'])

        self.textBrowser.append(info_format('基础设置配置完成.'))
        logger.info('设置界面初始化完毕。')

    def _init_datetime(self):
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
        self.comboBox.setCurrentIndex(today.month - 1)
        self.comboBox_2.clear()
        self.comboBox_2.addItems([str(i + 1) for i in range(month_range)])
        self.comboBox_2.setCurrentIndex(today.day - 1)

        self.comboBox_5.clear()
        self.comboBox_5.addItems([str(i) for i in [today.year, today.year + 1]])

        self.comboBox_3.setCurrentIndex(out_month - 1)
        self.comboBox_4.clear()
        self.comboBox_4.addItems([str(i + 1) for i in range(month_range_out)])
        self.comboBox_4.setCurrentIndex(out_day - 1)

        self.comboBox_6.clear()
        if today.year == out_year:
            self.comboBox_6.addItems([str(i) for i in [out_year, out_year + 1]])
        else:
            self.comboBox_6.addItem(str(out_year))

        logger.info('主页面时间初始化完毕，入住时间为：{}/{}/{}，离开时间为：{}/{}/{}'
                    .format(today.year, today.month, today.day,
                            out_year, out_month, out_day))

    def _refresh_days_num(self, is_in):
        """ 如果月份改变, 日期范围也要改变 """
        if is_in:
            current_year = int(self.comboBox_5.currentText())
            current_month = int(self.comboBox.currentText())
        else:
            current_year = int(self.comboBox_6.currentText())
            current_month = int(self.comboBox_3.currentText())

        month_range = calendar.monthrange(current_year, current_month)[1]

        if is_in:
            self.comboBox_2.clear()
            self.comboBox_2.addItems([str(i + 1) for i in range(month_range)])
        else:
            self.comboBox_4.clear()
            self.comboBox_4.addItems([str(i + 1) for i in range(month_range)])

        logger.info('用户改变了年份或月份，现在时间为 {}/{}，当月有共 {} 日。'.format(
            current_year, current_month, month_range
        ))

    def _platform_display(self, info):
        self.lineEdit_4.setText(info)

    def _info_display(self, info):
        self.textBrowser.append(info_format(info))

    def _img_display(self, img):
        try:
            img = img[-1]
            img = ImageQt.toqpixmap(img)
            self.imgView.setPixmap(img)
        except KeyError:
            return

    def _log_window_show(self):
        self.log_window.show()

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


