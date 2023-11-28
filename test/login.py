import requests
import json
import cv2
import qrcode


# 链接转二维码图片
def url2qr(url):
    img = qrcode.make(url)
    img.save('qrcode.png')
    img.show()
    return img


cookies = {
    'GUID': '09031157416805138000',
    'UBT_VID': '1700565565487.77e3n9fskNvw',
    '_RSG': 'z7KiA.PgO979poW9.JhihA',
    '_RDG': '281d181c4a7e742bd83a904d889064e2ee',
    '_RGUID': '7258a99f-8ab1-41fd-aaec-ad3f89832cc9',
    'MKT_CKID': '1699106155139.4vbb5.5oc2',
    '_bfaStatusPVSend': '1',
    'nfes_isSupportWebP': '1',
    'Union': 'OUID=&AllianceID=4899&SID=155997&SourceID=&createtime=1700911994&Expires=1701516793990',
    'MKT_OrderClick': 'ASID=4899155997&AID=4899&CSID=155997&OUID=&CT=1700911993990&CURL=https%3A%2F%2Fflights.ctrip.com%2Fonline%2Fchannel%2Fdomestic%3Fallianceid%3D4899%26sid%3D155997%26utm_medium%3Dgoogle%26utm_campaign%3Dpp%26utm_source%3Dgoogleppc%26gclid%3DCjwKCAiA04arBhAkEiwAuNOsIjVCID_vd3PWyAz5FnzlBykzMgxtPVJu7La5cIXPnZXmbzAWByJenhoCeI8QAvD_BwE%26gclsrc%3Daw.ds%26keywordid%3D2642337343-70570537617&VAL={"pc_vid":"1700565565487.77e3n9fskNvw"}',
    '_RF1': '112.44.202.132',
    'MKT_CKID_LMT': '1700911995538',
    'MKT_Pagesource': 'PC',
    'manualclose': '1',
    '_bfa': '1.1700565565487.77e3n9fskNvw.1.1700911995396.1700912007907.3.3.10320670296',
    '_ubtstatus': '%7B%22vid%22%3A%221700565565487.77e3n9fskNvw%22%2C%22sid%22%3A3%2C%22pvid%22%3A3%2C%22pid%22%3A10320670296%7D',
    '_jzqco': '%7C%7C%7C%7C1700911995793%7C1.8327393.1700565570389.1700911995545.1700912007936.1700911995545.1700912007936.0.0.0.5.5',
    '_bfi': 'p1%3D10320670296%26p2%3D10320670296%26v1%3D3%26v2%3D2',
    '_bfaStatus': 'success',
}

headers = {
    'authority': 'm.ctrip.com',
    'accept': '*/*',
    'accept-language': 'zh-CN,zh;q=0.9,en-GB;q=0.8,en;q=0.7',
    'cache-control': 'max-age=0',
    'content-type': 'application/json; charset=UTF-8',
    # 'cookie': 'GUID=09031157416805138000; UBT_VID=1700565565487.77e3n9fskNvw; _RSG=z7KiA.PgO979poW9.JhihA; _RDG=281d181c4a7e742bd83a904d889064e2ee; _RGUID=7258a99f-8ab1-41fd-aaec-ad3f89832cc9; MKT_CKID=1699106155139.4vbb5.5oc2; _bfaStatusPVSend=1; nfes_isSupportWebP=1; Union=OUID=&AllianceID=4899&SID=155997&SourceID=&createtime=1700911994&Expires=1701516793990; MKT_OrderClick=ASID=4899155997&AID=4899&CSID=155997&OUID=&CT=1700911993990&CURL=https%3A%2F%2Fflights.ctrip.com%2Fonline%2Fchannel%2Fdomestic%3Fallianceid%3D4899%26sid%3D155997%26utm_medium%3Dgoogle%26utm_campaign%3Dpp%26utm_source%3Dgoogleppc%26gclid%3DCjwKCAiA04arBhAkEiwAuNOsIjVCID_vd3PWyAz5FnzlBykzMgxtPVJu7La5cIXPnZXmbzAWByJenhoCeI8QAvD_BwE%26gclsrc%3Daw.ds%26keywordid%3D2642337343-70570537617&VAL={"pc_vid":"1700565565487.77e3n9fskNvw"}; _RF1=112.44.202.132; MKT_CKID_LMT=1700911995538; MKT_Pagesource=PC; manualclose=1; _bfa=1.1700565565487.77e3n9fskNvw.1.1700911995396.1700912007907.3.3.10320670296; _ubtstatus=%7B%22vid%22%3A%221700565565487.77e3n9fskNvw%22%2C%22sid%22%3A3%2C%22pvid%22%3A3%2C%22pid%22%3A10320670296%7D; _jzqco=%7C%7C%7C%7C1700911995793%7C1.8327393.1700565570389.1700911995545.1700912007936.1700911995545.1700912007936.0.0.0.5.5; _bfi=p1%3D10320670296%26p2%3D10320670296%26v1%3D3%26v2%3D2; _bfaStatus=success',
    'origin': 'https://passport.ctrip.com',
    'referer': 'https://passport.ctrip.com/',
    'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
}

json_data = {
    'accessCode': 'PCAUTEHNTICATE',
    # 非必要
    'context': {
        'sequenceId': '1f0f2017-6920-4aaf-beb8-539c959b6e27',
    },
    'clientInfo': {
        'clientId': '09031157416805138000',
        'pageId': '10320670296',
        'rmsToken': 'fp=x9krkj-23kxba-1kh5hi8&vid=1700565565487.77e3n9fskNvw&pageId=10320670296&r=7258a99f8ab141fdaaecad3f89832cc9&ip=112.44.202.132&rg=fin&kpData=0_0_0&kpControl=0_0_0-0_0_0&kpEmp=0_0_0_0_0_0_0_0_0_0-0_0_0_0_0_0_0_0_0_0-0_0_0_0_0_0_0_0_0_0&screen=1707x960&tz=+8&blang=zh-CN&oslang=zh-CN&ua=Mozilla%2F5.0%20(Windows%20NT%2010.0%3B%20Win64%3B%20x64)%20AppleWebKit%2F537.36%20(KHTML%2C%20like%20Gecko)%20Chrome%2F119.0.0.0%20Safari%2F537.36&d=passport.ctrip.com&v=25&kpg=0_0_0_0_0_0_0_0_0_0&adblock=F&cck=F',
        'allianceId': '',
        'sid': '',
    },
    'head': {
        'extension': [
            {
                'name': 'sequence',
                'value': '1f0f2017-6920-4aaf-beb8-539c959b6e27',
            },
        ],
    },
}

response = requests.post('https://m.ctrip.com/restapi/soa2/24863/getQrCode', headers=headers, json=json_data)
print(response.text)
qr_data = json.loads(response.text)['data']
qr_img = url2qr(qr_data)

print(1)
# Note: json_data will not be serialized by requests
# exactly as it was in the original request.
#data = '{"accessCode":"PCAUTEHNTICATE","context":{"sequenceId":"1f0f2017-6920-4aaf-beb8-539c959b6e27"},"clientInfo":{"clientId":"09031157416805138000","pageId":"10320670296","rmsToken":"fp=x9krkj-23kxba-1kh5hi8&vid=1700565565487.77e3n9fskNvw&pageId=10320670296&r=7258a99f8ab141fdaaecad3f89832cc9&ip=112.44.202.132&rg=fin&kpData=0_0_0&kpControl=0_0_0-0_0_0&kpEmp=0_0_0_0_0_0_0_0_0_0-0_0_0_0_0_0_0_0_0_0-0_0_0_0_0_0_0_0_0_0&screen=1707x960&tz=+8&blang=zh-CN&oslang=zh-CN&ua=Mozilla%2F5.0%20(Windows%20NT%2010.0%3B%20Win64%3B%20x64)%20AppleWebKit%2F537.36%20(KHTML%2C%20like%20Gecko)%20Chrome%2F119.0.0.0%20Safari%2F537.36&d=passport.ctrip.com&v=25&kpg=0_0_0_0_0_0_0_0_0_0&adblock=F&cck=F","allianceId":"4899","sid":"155997"},"head":{"extension":[{"name":"sequence","value":"1f0f2017-6920-4aaf-beb8-539c959b6e27"}]}}'
#response = requests.post('https://m.ctrip.com/restapi/soa2/24863/getQrCode', cookies=cookies, headers=headers, data=data)