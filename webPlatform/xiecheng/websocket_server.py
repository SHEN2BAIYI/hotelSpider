import asyncio
import json
import threading
import websockets
import webbrowser
import os

from utils.utils import logger


class XieChengServer:
    def __init__(self, webbrowser_path, port):
        self.port = port
        self.conn_web = None
        self.conn_spiders = []
        self.conn_code = None
        webbrowser.register("chrome", None,
                            webbrowser.BackgroundBrowser(webbrowser_path))

        self.stop_event = threading.Event()

    async def echo(self, websocket, path):
        async for message in websocket:

            # 收到消息后，尝试通过 JS 解析
            try:
                message = json.loads(message)
            except:
                logger.info('服务器：接收到的消息不是 JSON 格式，不做处理。')
                return

            """ 爬虫端消息 """
            if message["type"] == 'spider':
                logger.info('服务器：接收到爬虫端消息，callback 是 {}。'.format(message['callback']))
                # 拼接爬虫端发送的 JS 代码
                js_code = message['fun1'] + message['fun2']

                # 以 callback 作为关键字保存当前 spider 的 websocket
                conn = {
                    'soc': websocket,
                    'callback': message['callback'],
                    'js_code': js_code,
                }
                self.conn_spiders.append(conn)

                # 判断有无网页端连接
                if not self.conn_web:
                    logger.info('服务器：无网页端连接，创建连接。')

                    # 打开浏览器，创建连接。
                    path = os.getcwd() + '/source/static/callback.html'
                    webbrowser.get('chrome').open('file://{}'.format(path))
                    logger.info('服务器：无网页端连接，打开网页 - {}。'.format(path))

                else:
                    logger.info('服务器：有网页端连接，发送 JS 代码。')
                    try:
                        await self.conn_web.send(js_code)
                    except websockets.exceptions.ConnectionClosedOK:
                        # 不小心关掉了网页
                        # 打开浏览器，创建连接。
                        path = os.getcwd() + '/source/static/callback.html'
                        logger.info('服务器：网页端连接关闭，重新打开网页 - {}。'.format(path))
                        webbrowser.get('chrome').open('file://{}'.format(path))

            """ 浏览器消息 """
            if message["type"] == 'web':
                logger.info('服务器：接收到浏览器消息，' + json.dumps(message))
                # 判断消息来自 onopen 还是 onmessage
                if "callback" not in message.keys():
                    logger.info('服务器：接收到浏览器消息，消息来自 onopen，保存连接。')
                    self.conn_web = websocket

                    # 发送 JS 代码给浏览器端
                    if len(self.conn_spiders):
                        logger.info('服务器：发送 JS 代码给浏览器端。')
                        await self.conn_web.send(self.conn_spiders[0]['js_code'])
                else:
                    logger.info(
                        '服务器：接收到浏览器端消息，消息来自onmessage，callback 是 {}。'.format(message['callback']))

                    # 将数据完整的发送给爬虫端
                    for index, conn in enumerate(self.conn_spiders):
                        if message['callback'] == conn['callback']:
                            logger.info('服务器：发送数据给爬虫端。')
                            soc = self.conn_spiders.pop(index)['soc']
                            await soc.send(json.dumps(message))
                            break

    async def echo_server(self, stop):
        async with websockets.serve(self.echo, "localhost", int(self.port)):
            await stop

    def run(self):
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        stop = new_loop.run_in_executor(None, self.stop_event.wait)
        new_loop.run_until_complete(self.echo_server(stop))
