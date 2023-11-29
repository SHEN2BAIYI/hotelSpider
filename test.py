from utils.utils import *


res = json2dict('./source/cookie/xc.json')
cookies = {}
for i in res:
    cookies[i['name']] = i['value']

print(1)