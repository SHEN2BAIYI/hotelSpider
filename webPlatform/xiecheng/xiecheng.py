import datetime
import json
import os
import time
import base64
import requests
import execjs
import threading
import asyncio
import websockets

import selenium.common.exceptions
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from utils.utils import dict2json, json2dict, logger, stop_thread
from websocket_client import XieChengClient
from websocket_server import XieChengServer

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
        self.headers = {
            'referer': 'https://www.ctrip.com/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        }

        # 初始化浏览器驱动
        self._init_web_driver()

        # 网页地址
        self._domain = domain_path
        self._domain_login = domain_path_login
        self._domain_home = domain_path_home

        """  更多参数 """
        # test_ab 相关的客户端和服务器
        self.client = XieChengClient()
        self.server = XieChengServer()
        self.test_ab = []
        self.thread_client = None
        self.thread_server = None

        # 酒店列表
        self.hotel_list = {}
        self.search_time = 0

    """ 保存并清理数据 """
    def store_and_clear(self):
        # 保存数据
        logger.info('爬虫端：开始保存数据。')
        wb = Workbook()
        ws = wb.active
        ws.append(['酒店名称', '酒店类型', '酒店评分', '酒店地址', '酒店类型',
                   '房间名称', '房间价格', '房量提示', '有无早餐', '可住人数'])
        for hotel_id, hotel in self.hotel_list.items():
            for room in hotel['roomList']:
                for room_sale in room['saleRoom']:
                    # 查看有无房
                    room_flag = '房量充足'
                    if room_sale['base']['isFullRoom']:
                        room_flag = "无房"

                    for tag in room_sale['tags']:
                        if "仅剩" in tag['title']:
                            room_flag = tag['title']
                            break

                    # 查看有无早餐
                    breakfast = '无早餐'
                    for fac in room_sale['facility']:
                        if '早餐' in fac['content']:
                            breakfast = fac['content']
                            break

                    ws.append([
                        hotel['hotelName'],
                        hotel['hotelType'],
                        hotel['hotelScore'],
                        hotel['hotelAddress'],
                        hotel['hotelType'],

                        room['baseRoom']['roomName'],
                        room_sale['money']['filterPrice'],
                        room_flag,
                        breakfast,
                        room_sale['base']['maxGuest'],
                    ])
        wb.save('hotel.xlsx')
        logger.info('爬虫端：保存数据成功。')

        # 清理数据
        self.hotel_list = {}
        self.test_ab.clear()
        self.search_time = 0

        self.client.ws.close()
        self.server.stop_event.set()
        logger.info('爬虫端：清理数据成功，端口释放完毕。')

        time.sleep(5)
        print(self.thread_client.is_alive())
        print(self.thread_server.is_alive())

    """ 获取 hotel 详情 """
    def get_hotel_detail(self):
        def do(id_list):
            for id in id_list:
                # 生成 test_ab 参数
                while True:
                    if len(self.test_ab):
                        test_ab = self.test_ab.pop(0)
                        break

                    self.get_test_ab()
                    time.sleep(1)

                params = {
                    'testab': test_ab,
                }
                json_data = {
                    'checkIn': '2023-11-29',
                    'checkOut': '2023-11-30',
                    'priceType': '',
                    'adult': 1,
                    'popularFacilityType': '',
                    'mpRoom': '',
                    'fgt': '',
                    'hotelUniqueKey': '',
                    'child': 0,
                    'roomNum': 1,
                    'masterHotelId': int(id),
                    'age': '',
                    'cityId': self.params['main']['city']['cityId'],
                    'roomkey': '',
                    'minCurr': '',
                    'minPrice': '',
                    'hotel': '{}'.format(id),
                    'filterData': [],
                    'filterCondition': {},
                    'guestCountFilterType': 1,
                    'head': {
                        'Locale': 'zh-CN',
                        'Currency': 'CNY',
                        'Device': 'PC',
                    },
                    'ServerData': '',
                }

                # 发出请求
                response = requests.post(
                    'https://m.ctrip.com/restapi/soa2/21881/json/rateplan',
                    params=params,
                    cookies=self.cookies,
                    headers=self.headers,
                    json=json_data,
                )

                # 解析请求
                res = json.loads(response.text)['Response']['baseRooms']
                self.hotel_list[id]['roomList'] = res

        logger.info('爬虫端：开始获取酒店详情。')

        ths_list = []
        key_list = []
        for index, key in enumerate(self.hotel_list.keys()):
            # 线程数据装载
            key_list.append(key)

            # 线程启动
            if len(key_list) == 5 or index == len(self.hotel_list.keys()) - 1:
                task = threading.Thread(target=do, args=(key_list,))
                task.start()
                ths_list.append(task)
                key_list = []

        # 等待线程结束
        for th in ths_list:
            th.join()

    """ 获取 hotel 列表 """
    def get_hotel_list(self):
        logger.info('爬虫端：开始获取酒店列表。')

        # 生成 test_ab 参数
        while True:
            if len(self.test_ab):
                test_ab = self.test_ab.pop(0)
                break

            self.get_test_ab()
            time.sleep(1)

        params = {
            'testab': test_ab,
        }
        json_data = {
            'searchCondition': {
                'sortType': '',
                'adult': 1,
                'child': 0,
                'age': '',
                'pageNo': self.search_time,
                'optionType': 'City',
                'optionId': self.params['main']['city']['cityId'],
                'lat': 0,
                'destination': self.params['main']['city']['cityName'],
                'keyword': '',
                'cityName': self.params['main']['city']['cityName'],
                'lng': 0,
                'cityId': self.params['main']['city']['cityId'],
                # 'checkIn': '{}-{}-{}'.format(self.params['main']['in_year'], self.params['main']['in_month'],
                #                              self.params['main']['in_day']),
                # 'checkOut': '{}-{}-{}'.format(self.params['main']['out_year'], self.params['main']['out_month'],
                #                               self.params['main']['out_day']),
                'checkIn': '2023-11-29',
                'checkOut': '2023-11-30',
                'roomNum': 1,
                'mapType': '',
                'travelPurpose': 0,
                'countryId': self.params['main']['city']['countryId'],
                'pageSize': 10,
                'timeOffset': 28800,
                'radius': 0,
                'directSearch': 0,
                'signInHotelId': 0,
                'signInType': 0,
            },
            'filterCondition': {
                'star': [],
                'rate': 0,
                'breakfast': [],
                'bookable': [],
                'zone': [],
                'landmark': [],
                'metro': [],
                'airportTrainstation': [],
                'location': [],
                'brand': [],
                'feature': [],
                'category': [],
                'amenty': [],
                'discount': [],
                'cityId': [],
                'payType': [],
                'bookPolicy': [],
                'bedType': [],
                'priceRange': {
                    'highPrice': -1,
                    'lowPrice': 0,
                    'curr': 'CNY',
                },
                'priceType': '',
                'promotion': [],
                'rateCount': [],
                'hotArea': [],
                'ctripService': [],
                'applicablePeople': [],
                'hotPoi': [],
                'covid': [],
            },
            # 'ssr': False,
            # 'genk': True,
            # 'pageTraceId': 'a17aabe4-c1f1-4d75-82bd-4ffc966e76a1',
            'head': {
                'Locale': 'zh-CN',
                'Currency': 'CNY',
                'Device': 'PC',
            },
            # 'ServerData': '',
        }

        # 过滤已查询酒店 ID 列表
        if len(self.hotel_list):
            json_data['deduplication'] = [x for x, _ in self.hotel_list.items()]
            logger.info('爬虫端：已经找到 {} 家酒店，过滤已查询酒店 ID 列表。'.format(len(self.hotel_list)))

        # 发出请求
        response = requests.post(
            'https://m.ctrip.com/restapi/soa2/21881/json/HotelSearch',
            params=params,
            cookies=self.cookies,
            headers=self.headers,
            json=json_data,
        )

        # 解析请求
        response = json.loads(response.text)['Response']
        hotel_list = response['hotelList']['list']
        logger.info('爬虫端：成功获取 {} 家酒店。'.format(len(hotel_list)))

        # 存储结果
        for hotel in hotel_list:
            info = {
                'hotelId': hotel['base']['hotelId'],
                'hotelName': hotel['base']['hotelName'],
                'hotelType': hotel['base']['hotelTypeTag'],
                'hotelScore': hotel['score']['number'],
                'hotelAddress': hotel['position']['address'],
            }
            self.hotel_list[hotel['base']['hotelId']] = info

        if len(self.hotel_list) < self.params['main']['max_hotel_num']:
            self.get_hotel_list()

    """ 开启获取 test_ab 的 server 和 client """
    def start_server_client(self):
        self.__init_websocket_server()
        time.sleep(2)
        self.__init_websocket_client()

    """ 获得 test_ab """
    def get_test_ab(self):
        # 生成 callback 参数
        callback = self.__get_callback()
        json_data = {
            'callback': callback,
        }

        # 发送请求，获得响应
        response = requests.post(
            'https://m.ctrip.com/restapi/soa2/21881/json/getHotelScript',
            headers=self.headers,
            json=json_data,
        )

        # 制作网页端发送代码
        html_code = ('{var data = {callback: "%s", type: %s, value: e()}; var data = JSON.stringify(data); ws.send(data)}' % (callback, '"web"'))

        # 获取响应中的 testab JS 代码
        data = {
            'fun1': "function {}(e) {};".format(json_data['callback'],
                                                html_code),
            'fun2': json.loads(response.text)['Response'],
            'callback': callback,
            'type': 'spider',
        }
        data = json.dumps(data)

        # 向模拟服务器发送消息
        self.client.ws.send(data)
        logger.info('爬虫端：成功发送 testab JS 代码。')

    """ 服务器会根据 callback 生成 testab 的 JS 代码 """
    @staticmethod
    def __get_callback():
        with open('callback.js', 'r', encoding='utf-8') as f:
            js_code = f.read()

        ctx = execjs.compile(js_code)
        res = ctx.call('callback')
        logger.info('爬虫端：成功生成 callback 参数: {}。'.format(res))
        return res

    def _init_web_driver(self):
        # 初始化浏览器参数，这里选 Chrome 浏览器
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                             "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36")

        service = webdriver.chrome.service.Service(self.params['setting']['driver_path'])

        # 初始化浏览器
        self._driver = webdriver.Chrome(service=service, options=options)

        # 最大化窗口
        self._driver.maximize_window()
        self._driver.implicitly_wait(5)

        logger.info('初始化浏览器驱动成功。')

    def __init_websocket_client(self):
        # 改变 websocket 的 onmessage
        def on_message(soc, message, *args):
            # 解析 message
            try:
                message = json.loads(message)
                logger.info('爬虫端：接收到服务器消息，' + json.dumps(message))
            except:
                logger.info('爬虫端：接收到的消息不是 JSON 格式，不做处理。')
                return

            self.search_time += 1
            self.test_ab.append(message['value'])

        # 新开线程运行，避免堵塞主线程
        self.client.on_message = on_message
        self.thread_client = threading.Thread(target=self.client.start)
        self.thread_client.start()
        logger.info('爬虫端：成功创建 websocket 客户端。')

    def __init_websocket_server(self):
        # def run():
        #     new_loop = asyncio.new_event_loop()
        #     asyncio.set_event_loop(new_loop)
        #     asyncio.get_event_loop().run_until_complete(websockets.serve(self.server.echo, 'localhost', 8080))
        #     asyncio.get_event_loop().run_forever()

        self.thread_server = threading.Thread(target=self.server.run)
        self.thread_server.start()
        logger.info('爬虫端：成功创建 websocket 服务器。')

    def get_city_by_keyword(self):
        # 构建数据
        json_data = {
            'keyword': self.params['main']['destination'],
            'searchType': 'D',
        }

        # 发送请求
        response = requests.post(
            'https://m.ctrip.com/restapi/soa2/21881/json/gaHotelSearchEngine',
            cookies=self.cookies,
            headers=self.headers,
            json=json_data,
        )
        cities = json.loads(response.text)['Response']['searchResults']

        # 筛选出满意的 city_id
        for city in cities:
            if city['countryId'] == 1:
                self.params['main']['city'] = city
                break

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

    def store_cookie_file(self, cookie_path='./source/cookie/'):
        cookie = self._driver.get_cookies()
        dict2json(cookie, json_path=os.path.join(cookie_path, 'xc.json'))

        self.cookies = {}
        for i in cookie:
            self.cookies[i['name']] = i['value']


if __name__ == '__main__':
    spider = XieCheng({
        'setting': {
            'driver_path': 'E:/pythonProject/hotelSpider/chromedriver.exe',
        },
        'main': {
            'destination': '成都',
            'max_hotel_num': 20,
        }
    })

    spider.get_city_by_keyword()
    spider.load_cookie_file('E:\pythonProject\hotelSpider\source\cookie')
    spider.store_cookie_file('')
    spider.start_server_client()
    spider.get_hotel_list()
    spider.get_hotel_detail()
    spider.store_and_clear()
