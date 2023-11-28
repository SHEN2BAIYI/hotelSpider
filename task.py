from PyQt5.QtCore import QThread, pyqtSignal
from platform.xiecheng import XieCheng
from utils.utils import logger
import selenium.common.exceptions


class SearchTask(QThread):
    # 定义信号
    qr_code = pyqtSignal(list)
    platform_signal = pyqtSignal(str)
    log_signal = pyqtSignal(str)

    def __init__(self, params):
        super(SearchTask, self).__init__()
        self.params = params

    def run(self):
        # 初始化爬虫，主要确认驱动是否存在
        try:
            spider = XieCheng(params=self.params)
        except selenium.common.exceptions.SessionNotCreatedException:
            logger.info('驱动存在问题，请确认路径是否正确。')
            self.log_signal('驱动存在问题，请确认路径是否正确。')
            return

        self.platform_signal.emit('携程')

        # 获取用户 cookie，进行登录
        logger.info('正在进行用户 cookie 的获取。')
        success, qrcode = spider.load_cookie_file()
        if not success and qrcode:
            # 发送二维码到主页面
            self.qr_code.emit([qrcode])
            self.log_signal.emit('请扫描二维码进行携程登录。')

            # 监视页面，避免二维码过期
            while True:
                success, qrcode = spider.renew_qrcode()

                if not success and qrcode:
                    # 发送二维码到主页面
                    self.qr_code.emit([qrcode])
                    self.log_signal.emit('二维码过期，请重新扫描新二维码。')
                else:
                    self.log_signal.emit('扫描二维码登录成功。')
                    break
        else:
            self.log_signal.emit('cookie 直接读取成功，该 cookie 有效，直接登录。')

        # 保存 cookie
        spider.store_cookie()
        self.log_signal.emit('cookie 保存成功，以待下次直接登录。')
        logger.info('保存 cookie 成功，以待下次直接登录。')

        # 根据搜索条件，到达 target 酒店
        spider.go_target()

        # 开始搜索
        hotel_list = spider.get_hotel_info()
        self.log_signal.emit('成功获取酒店 {} 家，准备开始写入。'.format(len(hotel_list)))

        # 完成搜索，开始查找酒店细节
        spider.get_hotel_detail(hotel_list)
        self.log_signal.emit('成功写入酒店数据，完成搜索任务。')


class CountTask(QThread):
    # 定义信号
    log_signal = pyqtSignal(str)

    def __init__(self, count, flag):
        super(CountTask, self).__init__()
        self.count = count
        self.flag = flag

    def run(self):
        i = 0
        while True:

            if i == self.count:
                break
            else:
                self.log_signal.emit('当前第 {} 线程正在运行, 当前计数 {}.'.format(self.flag, i))
                i += 1
            self.sleep(2)


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

            self.sleep(30)
