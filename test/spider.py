import requests
import execjs
import json
from websocket_client import XieCheng
import threading


"""
    1. 通过 callback，获取用于生成的 JS 代码
"""


# 获取 callback
def get_callback():
    with open('callback.js', 'r', encoding='utf-8') as f:
        js_code = f.read()

    ctx = execjs.compile(js_code)
    res = ctx.call('callback')
    print(res)
    return res


# 为字符串添加转义字符
def add_escape(value):
    reserved_chars = r'''"\\'''
    replace = ['\\' + l for l in reserved_chars]
    trans = str.maketrans(dict(zip(reserved_chars, replace)))
    return value.translate(trans)


cookies = {
    '_RGUID': '7258a99f-8ab1-41fd-aaec-ad3f89832cc9',
    '_RSG': 'z7KiA.PgO979poW9.JhihA',
    '_RDG': '281d181c4a7e742bd83a904d889064e2ee',
    'MKT_CKID': '1700918308098.javo7.cfp1',
    'MKT_CKID_LMT': '1700918308099',
    'GUID': '09031107416969064109',
    '_RF1': '112.44.202.132',
    '_bfaStatusPVSend': '1',
    # 'cticket': '0DE108EA50CFF267910F472B6B6E9B5C8719508694D8B17CB199E59BC5EBACC3',
    'login_type': '0',
    'login_uid': '95362D6AC68C1654258E00828D7B2BEA',
    'DUID': 'u=95362D6AC68C1654258E00828D7B2BEA&v=0',
    'IsNonUser': 'F',
    'AHeadUserInfo': 'VipGrade=10&VipGradeName=%BB%C6%BD%F0%B9%F3%B1%F6&UserName=%C9%F2%D7%D3%BD%DC&NoReadMessageCount=0',
    'MKT_Pagesource': 'PC',
    'ibulanguage': 'CN',
    'ibulocale': 'zh_cn',
    'cookiePricesDisplayed': 'CNY',
    'UBT_VID': '1700918308056.3drtr7',
    'nfes_isSupportWebP': '1',
    'intl_ht1': 'h4=2_68488139',
    '_abtest_userid': 'af732f85-f271-4b46-bb40-7015d85077a9',
    'FlightIntl': 'Search=[%22CTU|%E6%88%90%E9%83%BD(CTU)|28|CTU|480%22%2C%22SHA|%E4%B8%8A%E6%B5%B7(SHA)|2|SHA|480%22%2C%222023-11-26%22%2C%222023-11-29%22]',
    '_ubtstatus': '%7B%22vid%22%3A%221700918308056.3drtr7%22%2C%22sid%22%3A1%2C%22pvid%22%3A48%2C%22pid%22%3A102001%7D',
    '_bfi': 'p1%3D102001%26p2%3D102001%26v1%3D48%26v2%3D3',
    '_bfaStatus': 'success',
    'librauuid': '',
    '_jzqco': '%7C%7C%7C%7C1700918308146%7C1.1298985147.1700918308097.1700975954433.1700975964856.1700975954433.1700975964856.undefined.0.0.79.79',
    '_bfa': '1.1700918308056.3drtr7.1.1700975964161.1700975966022.2.2.102002',
}

headers = {
    'authority': 'm.ctrip.com',
    'accept': 'application/json',
    'accept-language': 'zh-CN,zh;q=0.9,en-GB;q=0.8,en;q=0.7',
    'cache-control': 'no-cache',
    'content-type': 'application/json;charset=UTF-8',
    # 'cookie': '_RGUID=7258a99f-8ab1-41fd-aaec-ad3f89832cc9; _RSG=z7KiA.PgO979poW9.JhihA; _RDG=281d181c4a7e742bd83a904d889064e2ee; MKT_CKID=1700918308098.javo7.cfp1; MKT_CKID_LMT=1700918308099; GUID=09031107416969064109; _RF1=112.44.202.132; _bfaStatusPVSend=1; cticket=0DE108EA50CFF267910F472B6B6E9B5C8719508694D8B17CB199E59BC5EBACC3; login_type=0; login_uid=95362D6AC68C1654258E00828D7B2BEA; DUID=u=95362D6AC68C1654258E00828D7B2BEA&v=0; IsNonUser=F; AHeadUserInfo=VipGrade=10&VipGradeName=%BB%C6%BD%F0%B9%F3%B1%F6&UserName=%C9%F2%D7%D3%BD%DC&NoReadMessageCount=0; MKT_Pagesource=PC; ibulanguage=CN; ibulocale=zh_cn; cookiePricesDisplayed=CNY; UBT_VID=1700918308056.3drtr7; nfes_isSupportWebP=1; intl_ht1=h4=2_68488139; _abtest_userid=af732f85-f271-4b46-bb40-7015d85077a9; FlightIntl=Search=[%22CTU|%E6%88%90%E9%83%BD(CTU)|28|CTU|480%22%2C%22SHA|%E4%B8%8A%E6%B5%B7(SHA)|2|SHA|480%22%2C%222023-11-26%22%2C%222023-11-29%22]; _ubtstatus=%7B%22vid%22%3A%221700918308056.3drtr7%22%2C%22sid%22%3A1%2C%22pvid%22%3A48%2C%22pid%22%3A102001%7D; _bfi=p1%3D102001%26p2%3D102001%26v1%3D48%26v2%3D3; _bfaStatus=success; librauuid=; _jzqco=%7C%7C%7C%7C1700918308146%7C1.1298985147.1700918308097.1700975954433.1700975964856.1700975954433.1700975964856.undefined.0.0.79.79; _bfa=1.1700918308056.3drtr7.1.1700975964161.1700975966022.2.2.102002',
    'origin': 'https://hotels.ctrip.com',
    'p': '69980301162',
    'pragma': 'no-cache',
    'referer': 'https://hotels.ctrip.com/',
    'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
}

json_data = {
    'callback': get_callback(),
    'a': 0,
    'b': '2023-11-26',
    'c': '2023-11-27',
    'd': 'zh-cn',
    'e': 2,
    'head': {
        'Locale': 'zh-CN',
        'Currency': 'CNY',
        'Device': 'PC',
        'UserIP': '112.44.202.132',
        'Group': 'ctrip',
        'ReferenceID': '',
        'UserRegion': 'CN',
        'AID': None,
        'SID': None,
        'Ticket': '',
        'UID': '',
        'IsQuickBooking': '',
        'ClientID': '09031107416969064109',
        'OUID': None,
        'TimeZone': '8',
        'P': '69980301162',
        'PageID': '102002',
        'Version': '',
        'HotelExtension': {
            'WebpSupport': True,
            'group': 'CTRIP',
            'Qid': '309064463492',
            'hasAidInUrl': False,
        },
        'Frontend': {
            'vid': '1700918308056.3drtr7',
            'sessionID': '2',
            'pvid': '2',
        },
    },
    'ServerData': '',
}

response = requests.post(
    'https://m.ctrip.com/restapi/soa2/21881/json/getHotelScript',
    cookies=cookies,
    headers=headers,
    json=json_data,
)

# 获取生成 testab 的 JS 代码
func2 = json.loads(response.text)['Response']
func1 = "function {}(e) {};".format(json_data['callback'], "{ws.send(e())}")
# func = add_escape(func1 + func2)
func = func1 + func2
print(func)

# 创建 WebSocket 客户端
web = XieCheng()
task = threading.Thread(target=web.start)
task.start()
web.ws.send('Spider myjscode:' + func)

# Note: json_data will not be serialized by requests
# exactly as it was in the original request.
#data = '{"callback":"AhXiZgthka","a":0,"b":"2023-11-26","c":"2023-11-27","d":"zh-cn","e":2,"head":{"Locale":"zh-CN","Currency":"CNY","Device":"PC","UserIP":"112.44.202.132","Group":"ctrip","ReferenceID":"","UserRegion":"CN","AID":null,"SID":null,"Ticket":"","UID":"","IsQuickBooking":"","ClientID":"09031107416969064109","OUID":null,"TimeZone":"8","P":"69980301162","PageID":"102002","Version":"","HotelExtension":{"WebpSupport":true,"group":"CTRIP","Qid":"309064463492","hasAidInUrl":false},"Frontend":{"vid":"1700918308056.3drtr7","sessionID":"2","pvid":"2"}},"ServerData":""}'
#response = requests.post('https://m.ctrip.com/restapi/soa2/21881/json/getHotelScript', cookies=cookies, headers=headers, data=data)