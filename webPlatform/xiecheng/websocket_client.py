import websocket
import json


class XieChengClient:
    def __init__(self):
        self.url = 'ws://127.0.0.1:8080'
        self.ws = None
        self.testab = []

    def on_message(self, soc, message, *args):
        self.testab.append(json.loads(message))

    def on_error(self, error, *args):
        pass

    def on_close(self, message, *args):
        pass

    def on_open(self, *args):
        # self.ws.send('Spider open')
        pass

    def start(self):
        websocket.enableTrace(False)
        self.ws = websocket.WebSocketApp(self.url,
                                         on_open=self.on_open,
                                         on_message=self.on_message,
                                         on_error=self.on_error,
                                         on_close=self.on_close)
        self.ws.run_forever()

