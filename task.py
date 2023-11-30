from PyQt5.QtCore import QThread, pyqtSignal
from webPlatform import XieCheng
from utils.utils import logger

import selenium.common.exceptions
import time
import os
import socket


class SearchTask(QThread):
    # 定义信号
    qr_code = pyqtSignal(list)
    platform_signal = pyqtSignal(str)
    log_signal = pyqtSignal(str)

    def __init__(self, params):
        super(SearchTask, self).__init__()
        self.params = params

    def run(self):
        # 携程任务
        self._xc_task()

    def _xc_task(self):
        # 检查参数正确性
        if not self.__check_params():
            return
        self._log('携程端：界面参数检查成功，开始进行搜索程序。')

        # 初始化爬虫，主要确认驱动是否存在
        try:
            spider = XieCheng(params=self.params)
        except selenium.common.exceptions.SessionNotCreatedException:
            self._log('携程端：驱动存在问题，请确认路径或版本是否正确。')
            return

        self.platform_signal.emit('携程')

        # 获取用户 cookie，进行登录
        self._log('携程端：开始获取 cookie。')
        success, qrcode = spider.load_cookie_file()
        if not success and qrcode:
            # 发送二维码到主页面
            self.qr_code.emit([qrcode])
            self._log('携程端：请扫描二维码进行携程登录。')

            # 监视页面，避免二维码过期
            while True:
                success, qrcode = spider.renew_qrcode()

                if not success and qrcode:
                    # 发送二维码到主页面
                    self.qr_code.emit([qrcode])
                    self._log('携程端：二维码过期，请重新扫描新二维码。')
                else:
                    self._log('携程端：二维码扫描成功，登录成功。')
                    break
        else:
            self._log('携程端：cookie 直接读取成功，该 cookie 有效，直接登录。')

        # 保存 cookie
        spider.store_cookie_file()
        self._log('携程端：cookie 保存成功，以待下次直接登录。')

        # 获取 city_id
        spider.get_city_by_keyword()
        self._log('携程端：成功获取 city id - {}。'.format(spider.params['main']['city']['cityId']))
        self._log('携程端：所有初始化程序已经完成，现在正式开始爬虫程序。期间会打开浏览器空白网页，请不要关闭。')

        # 开启服务器和客户端以生成 test ab 参数
        spider.start_server_client()

        # 获取酒店列表
        spider.get_hotel_list()
        self._log('携程端：成功获取酒店 {} 家，准备开始获取细节房间信息。'.format(len(spider.hotel_list)))

        # 获取酒店详情
        spider.get_hotel_detail()
        self._log('携程端：成功获取酒店细节，完成爬虫程序。')

        # 保存并清理
        spider.store_and_clear()
        self._log('携程端：成功保存数据，完成当前任务。')

    """ 日志记录 """
    def _log(self, info):
        self.log_signal.emit(info)

    def __check_params(self):
        # 检查主页面目的地
        if not self.params['main']['destination'].strip():
            self._log('携程端：用户没有输入目的地。')
            return False

        # 检查主页面时间
        in_time_str = '{}-{}-{}'.format(self.params['main']['in_year'],
                                        self.params['main']['in_month'],
                                        self.params['main']['in_day']
                                        if int(self.params['main']['in_day']) >= 10 else '0' + self.params['main']['in_day'])
        out_time_str = '{}-{}-{}'.format(self.params['main']['out_year'],
                                         self.params['main']['out_month'],
                                         self.params['main']['out_day']
                                         if int(self.params['main']['out_day']) >= 10 else '0' + self.params['main']['out_day'])

        in_time = time.strptime(in_time_str, '%Y-%m-%d')
        out_time = time.strptime(out_time_str, '%Y-%m-%d')

        in_time = int(time.mktime(in_time))
        out_time = int(time.mktime(out_time))
        self.params['main']['in_time'] = in_time_str
        self.params['main']['out_time'] = out_time_str

        if in_time >= out_time:
            self._log('携程端：用户选择的入住时间大于等于离开时间。')
            return False

        # 检查设置携程开放端口是否被占用
        if self.params['setting']['port'].strip():
            # 检查端口是否为整数
            try:
                self.params['setting']['port'] = int(self.params['setting']['port'])
            except ValueError:
                self._log('携程端：用户输入的端口不是整数。')
                return False

            # 检查端口是否合理
            if self.params['setting']['port'] < 0 or self.params['setting']['port'] > 65535:
                self._log('携程端：用户输入的端口不在 0-65535 范围内。')
                return False

            # 检查端口是否被占用
            try:
                sock = socket.socket()
                sock.connect(("localhost", self.params['setting']['port']))
                self._log('携程端：用户输入的端口被占用。')
                return False
            except:
                logger.info('携程端：用户输入的端口可用。')
            finally:
                if sock:
                    sock.close()
        else:
            self._log('携程端：用户没有输入端口。')
            return False

        # 检查设置携程浏览器路径，是否存在 exe 文件
        if self.params['setting']['web_path'].strip():
            if not os.path.exists(self.params['setting']['web_path']):
                self._log('携程端：用户输入的浏览器路径不存在。')
                return False
            elif not self.params['setting']['web_path'].endswith('.exe'):
                self._log('携程端：用户输入的浏览器路径不是 exe 文件。')
                return False
        else:
            self._log('携程端：用户没有输入浏览器路径。')
            return False
        logger.info('携程端：浏览器路径检查成功。')

        # 检查设置携程驱动路径，是否存在 exe 文件
        if self.params['setting']['driver_path'].strip():
            if not os.path.exists(self.params['setting']['driver_path']):
                self._log('携程端：用户输入的驱动路径不存在。')
                return False
            elif not self.params['setting']['driver_path'].endswith('.exe'):
                self._log('携程端：用户输入的驱动路径不是 exe 文件。')
                return False
        else:
            self._log('携程端：用户没有输入驱动路径。')
            return False
        logger.info('携程端：驱动路径检查成功。')

        # 检查设置携程输出路径，是否存在文件夹
        if self. params['setting']['output_path'].strip():
            if not os.path.exists(self.params['setting']['output_path']):
                # 不存在则创建文件夹
                try:
                    os.mkdir(self.params['setting']['output_path'])
                except Exception:
                    self._log('携程端：用户输入的输出路径不存在，且创建失败。')
                    return False
        else:
            self._log('携程端：用户没有输入输出路径。')
            return False
        logger.info('携程端：输出路径检查成功。')

        self._log('携程端：用户输入的参数检查成功。')
        return True
    

class TaskMonitor(QThread):
    # 定义信号
    log_signal = pyqtSignal(str)

    def __init__(self, pool):
        super(TaskMonitor, self).__init__()
        self.pool = pool

    def run(self):
        while True:

            # 如果线程结束,就将线程抛出
            for index, value in enumerate(self.pool):
                if not value.isRunning():
                    self.pool.pop(index)

            logger.info('任务检测：现在还有 {} 个后台任务正在运行.'.format(len(self.pool)))

            # # 如果只有1个剩余任务，则为本身，就不进行输出
            # if len(self.pool) > 1:
            #     self.log_signal.emit('还有 {} 个任务正在运行.'.format(len(self.pool)))

            self.sleep(20)
