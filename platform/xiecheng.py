import datetime
import json
import os
import time
import base64

import selenium.common.exceptions
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from utils.utils import dict2json, json2dict, logger

from io import BytesIO
from PIL import Image
from openpyxl import Workbook
from bs4 import BeautifulSoup


"""
    进行携程酒店信息爬取
"""


class XieCheng:
    def __init__(self,
                 params,
                 domain_path='https://www.ctrip.com/',
                 domain_path_login='https://passport.ctrip.com/user/login',
                 domain_path_home='https://my.ctrip.com/myinfo/home'):

        # 导入参数
        self.params = params
        self.cookies = None

        # 初始化浏览器驱动
        self._init_web_driver()

        # 网页地址
        self._domain = domain_path
        self._domain_login = domain_path_login
        self._domain_home = domain_path_home

    def _init_web_driver(self):
        # 初始话浏览器参数，这里选 Chrome 浏览器
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                             "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36")

        # 初始话浏览器
        self._driver = webdriver.Chrome(self.params['setting']['driver_path'], options=options)

        # 最大化窗口
        self._driver.maximize_window()
        self._driver.implicitly_wait(5)

        logger.info('初始化浏览器驱动成功。')

    def get_hotel_detail(self, hotel_list):
        # 需要先进入单个酒店界面
        hotels = self._driver.find_elements(by=By.CLASS_NAME, value='list-card-title')
        for hotel in hotels:
            try:
                hotel.click()
                self._driver.switch_to.window(self._driver.window_handles[-1])
                break
            except selenium.common.exceptions.ElementClickInterceptedException:
                continue

        WebDriverWait(self._driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, 'roomlist')))

        # 获取当前 url，并进行解析
        url = self._driver.current_url
        url = url.split('?hotelId=')
        url_head = url[0] + '?hotelId='
        url_tail = '&checkIn=' + url[-1].split('checkIn=')[-1]

        # Excel 保存步骤
        wb = Workbook()
        ws = wb.create_sheet('Sheet1')
        ws.append(["酒店名称", "酒店位置", "入住时间",
                   "离开时间", "房间名称", "房间价格",
                   "房量提示", "房间配置", "有无早餐", "特殊信息"])

        for index, hotel in enumerate(hotel_list):
            new_url = url_head + str(hotel['base']['hotelId']) + url_tail
            logger.info('酒店信息获取：{}/{}。'.format(index, len(hotel_list)))
            logger.info('酒店细节信息获取：{}。'.format(new_url))
            self._driver.get(new_url)
            WebDriverWait(self._driver, 20)\
                .until(EC.presence_of_element_located((By.CLASS_NAME, 'roomlist-baseroom-card')))

            # BeautifulSoap 解析页面
            soup = self._get_html()

            # 获取 trace info
            trace_info = json.loads(hotel['traceInfo'])

            # 获取酒店房间
            room_container = soup.find('div', class_='roomlist-container')
            room_list = room_container.find_all('div', class_='roomlist-baseroom-card')
            logger.info('酒店细节信息获取：共有 {} 种类型房间。'.format(len(room_list)))

            for room in room_list:
                # 获取房间名称
                room_name = room.find('div', class_='roomname').text

                # 获取房间参数
                room_config = ''
                config_info = room.find('div', class_='roompanel-facility-desc').find_all('span')
                for info in config_info:
                    room_config += info.text

                # 获取房间配置，一种房间有不同的配置，比如早饭之类的东西
                rooms_table = room.find_all('div', class_='ubt-salecard')

                for room_table in rooms_table:
                    # 该种房间类型早餐
                    room_bf = room_table.find('div', class_='bm-item').span.text

                    # 该种房间特殊信息
                    room_special = ''
                    special_info = room_table.find_all('div', class_='policy')
                    for info in special_info:
                        info = info.span.text
                        room_special += info
                        room_special += ','

                    # 该种房间放量
                    room_num = room_table.find('p', class_='roomhold')
                    if room_num:
                        room_num = room_num.text
                    else:
                        room_num = '房量宽裕'

                    # 该种房间价格
                    room_price = room_table.find('div', class_='price-display')
                    if room_price:
                        room_price = room_price.text
                    else:
                        room_price = 0
                        room_num = '房间售罄'

                    data = [hotel['base']['hotelName'], hotel['position']['address'],
                            trace_info['checkIn'], trace_info['checkOut'],
                            room_name, room_price, room_num, room_config, room_bf, room_special]

                    logger.info(data)
                    ws.append(data)

        now = time.strftime("%Y-%m-%d-%H-%M")

        logger.info("酒店爬取完成，数据保存路径为 {}。".format(os.path.join(self.params['setting']['output_path'], '{}-xc.xlsx'.format(now))))
        wb.save(os.path.join(self.params['setting']['output_path'], '{}-xc.xlsx'.format(now)))

    def get_hotel_info(self):
        def hotel_info():
            logs = self._driver.get_log('performance')

            for log in logs:
                log_json = json.loads(log["message"])["message"]

                if log_json["method"] == 'Network.responseReceived':
                    params = log_json["params"]
                    try:
                        request_url = params["response"]["url"]
                        if "HotelSearch?" in request_url and "restapi" in request_url:
                            request_id = params['requestId']
                            response_body = self._driver.execute_cdp_cmd('Network.getResponseBody',
                                                                         {'requestId': request_id})
                            response_body = json.loads(response_body['body'])
                            data.append(response_body)
                    except Exception as e:
                        # logger.info(e)
                        continue
            return data

        # 获取 hotel 的编号
        hotel_list = []
        data = []
        while len(hotel_list) < int(self.params['main']['max_hotel_num']):
            hotel_list = []
            infos = hotel_info()

            for info in infos:
                try:
                    info_list = info['Response']['hotelList']['list']

                    for hotel in info_list:
                        hotel_list.append(hotel)
                except KeyError:
                    logger.info('Performance 处出现异常，暂时不影响。')
                    self._driver.save_screenshot('./now.png')
                    # 下滚页面
                    for i in range(4):
                        self._driver.execute_script('window.scrollBy(0, 200)')
                    self._driver.save_screenshot('./now1.png')
                    time.sleep(20)

                    continue
            logger.info('找到 {} 家酒店，酒店数量阈值为 {}。'.format(len(hotel_list),
                                                       int(self.params['main']['max_hotel_num'])))

            # 未达到数量阈值，需要继续查找。
            try:
                # 点击查看更多
                self._driver.find_element(by=By.CLASS_NAME, value='btn-box').click()
                time.sleep(2)
            except:
                # 下滚页面
                for i in range(4):
                    self._driver.execute_script('window.scrollBy(0, 200)')
                time.sleep(1)

        self._driver.refresh()
        WebDriverWait(self._driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'card-item-wrap')))
        logger.info('页面刷新成功，结束酒店信息获取，准备开始酒店细节信息获取。')
        return hotel_list

    def go_target(self):
        self._driver.get(self._domain)
        logger.info('正式开始爬取携程酒店，前往符合目标参数的网页。')

        # 选择目的地
        self._pick_destination(self.params['main']['destination'])
        logger.info('成功选择目的地-{}。'.format(self.params['main']['destination']))

        # 选择时间
        self._pick_date(self.params['main']['in_month'],
                        self.params['main']['in_day'],
                        self.params['main']['out_month'],
                        self.params['main']['out_day'])
        logger.info('成功选择时间-{}/{} {}/{}。'.format(
            self.params['main']['in_month'],
            self.params['main']['in_day'],
            self.params['main']['out_month'],
            self.params['main']['out_day']
        ))

        # 选择人数
        self._pick_person_room_num(self.params['main']['person_num'],
                                   self.params['main']['room_num'])

        # 找到搜索按钮
        button = self._driver.find_element(by=By.CLASS_NAME, value='hs_search-btn-container_R0HuJ')
        button.click()

        # 跳转页面，不能用 sleep，而是用等待元素出现
        WebDriverWait(self._driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'card-item-wrap')))
        logger.info('成功到达目标页面，开始正式爬取酒店信息。')

    def _get_html(self):
        page_source = self._driver.page_source
        soup = BeautifulSoup(page_source, 'lxml')
        return soup

    def _pick_destination(self, destination):
        """
            设置目的地（special）
        """
        # 找到目的地
        area_destination = self._driver.find_element(by=By.ID, value='hotels-destination')

        area_destination.click()
        time.sleep(0.5)
        area_destination.clear()
        time.sleep(0.5)
        for key in destination:
            area_destination.send_keys(key)
            time.sleep(1.5)

        # 取得联想地点
        try:
            # 等待联想关键地点的出现
            locator = (By.CLASS_NAME, 'hs_associative-item_z55zG')
            WebDriverWait(self._driver, 5).until(EC.presence_of_element_located(locator))
        except Exception as e:
            return None

        # 选择第一个联想地点
        ass_destination = self._driver.find_element(by=By.CLASS_NAME, value='hs_associative-item_z55zG')
        ass_destination.click()

    def _pick_date(self, in_month, in_day, out_month, out_day):
        def _do(index, day):
            months = self._driver.find_elements(By.CLASS_NAME, value='c-calendar-month')
            month = self._driver.find_elements(By.CLASS_NAME, value='c-calendar-month__title')[index].text
            dates = months[index].find_elements(By.TAG_NAME, 'li')
            for date in dates:
                if date.text == str(day):
                    logger.info('找到日期 {}/{}。'.format(month, str(day)))
                    date.click()
                    break

        logger.info('进行日期选择，入住时间：{}/{}，离开时间：{}/{}。'.format(
            in_month, in_day, out_month, out_day
        ))

        # 点击按钮，召唤日期
        self._driver.find_element(By.ID, value='checkIn').click()

        # 判断是这个月还是下个月
        today = datetime.datetime.today()
        logger.info('入住时间选择：{}/{}-{}/{}。'.format(in_month, in_day, today.month, today.day))
        if str(in_month) == str(today.month):
            _do(0, in_day)
        else:
            _do(1, in_day)

        time.sleep(1)
        logger.info('离开时间选择：{}/{}-{}/{}。'.format(out_month, out_day, today.month, today.day))
        if str(out_month) == str(today.month):
            _do(0, out_day)
        else:
            _do(1, out_day)

    def _pick_person_room_num(self, person_num, room_num):
        logger.info('进行房间数量及人口数量选择，房间数量：{}，人口数量：{}。'.format(room_num, person_num))

        # 激活房间及人数框
        self._driver.find_element(by=By.CLASS_NAME, value='hs_info_BG7Yo').click()

        buttons = self._driver.find_elements(by=By.CLASS_NAME, value='hs_u-icon-ic_plus_iE-7E')

        for i in range(int(room_num)-1):
            buttons[0].click()
            time.sleep(0.5)
        time.sleep(5)
        for i in range(int(person_num)-int(room_num)):
            buttons[1].click()
            time.sleep(0.5)

    def load_cookie_file(self, cookie_path='./source/cookie/'):
        # 寻找是否有 cookie 文件，没有就需要扫码，有的话就加载
        if not os.path.exists(os.path.join(cookie_path, 'xc.json')):
            logger.info('没有找到 cookie 文件，需要进行扫码登陆操作')
            # 1.进入登录页面
            self._driver.get(self._domain_login)

            # 2.点击扫码登陆按钮，点击调出二维码
            login_button = self._driver.find_element(by=By.CLASS_NAME, value='login-code')
            login_button.click()
            time.sleep(1)

            # 3.裁剪出 qrcode
            qrcode = self._cut_qrcode()
            return False, qrcode

        else:
            logger.info('找到 cookie 文件夹了，期待直接加载。')
            # 找到 cookie 文件，进行读取文件
            self.cookies = json2dict(os.path.join(cookie_path, 'xc.json'))

            # 进入登录页面
            self._driver.get(self._domain_login)

            # 导入 cookie
            for cookie in self.cookies:
                self._driver.add_cookie(cookie)

            # 进入 home 界面
            self._driver.get(self._domain_home)

            try:
                # 跳转页面等待
                WebDriverWait(self._driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'member-box')))
                logger.info('读取 cookie 文件成功，该 cookie 有效。')
                return True, None
            except Exception:
                os.remove(os.path.join(cookie_path, 'xc.json'))
                logger.info('读取 cookie 文件成功，但是该文件无效，删除该文件，并且使用扫码登陆。')
                return self.load_cookie_file()

    def renew_qrcode(self):
        try:
            # 等待登录成功
            WebDriverWait(self._driver, 62).until(EC.presence_of_element_located((By.CLASS_NAME, 'member-box')))
            logger.info('扫描二维码登录成功。')
            return True, None

        except:
            # 没有登录成功，二维码过期，重新刷新
            try:
                if self._driver.find_element(by=By.CLASS_NAME, value='er_void') \
                        .value_of_css_property('display') != 'none':
                    logger.info('二维码过期，进行刷新。')
                    refresh_button = self._driver.find_element(by=By.CLASS_NAME, value='btn-refresh')
                    refresh_button.click()
            except:
                self._driver.find_element(by=By.CLASS_NAME, value='lg_loginbox_refresh_btn').click()
                logger.info('二维码过期，进行刷新。')

            time.sleep(2)
            return False, self._cut_qrcode()

    def _cut_qrcode(self):
        screen_shot = self._driver.get_screenshot_as_base64()
        screen_shot = base64.b64decode(screen_shot)
        screen_shot = BytesIO(screen_shot)
        screen_shot = Image.open(screen_shot)

        try:
            QR_area = self._driver.find_element(by=By.ID, value='qrcode_img')
        except selenium.common.exceptions.NoSuchElementException:
            QR_area = self._driver.find_element(by=By.CLASS_NAME, value='qrcode-box')

        left, top = QR_area.location['x'], QR_area.location['y']
        right, bottom = left + QR_area.size['width'], top + QR_area.size['height']
        QR = screen_shot.crop((left, top, right, bottom))
        logger.info('成功寻找到二维码，裁剪并输出。')
        return QR

    def store_cookie(self, cookie_path='./source/cookie/'):
        cookie = self._driver.get_cookies()
        dict2json(cookie, json_path=os.path.join(cookie_path, 'xc.json'))


if __name__ == '__main__':
    spider = XieCheng()
    spider.search()
