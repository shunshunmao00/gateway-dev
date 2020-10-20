# -*- coding: utf-8 -*-
from app.global_data.global_data import g
from app.service import gateway_service, login_service


class AppCore(object):
    
    def __init__(self):
        g.load_global_data()
        if not g.init_success:
            raise Exception('初始化加载 global_data 失败！')

    def forward_request(self, prev_request):
        return gateway_service.forward_request(prev_request)

    def login(self, **args):
        return login_service.login(**args)

    def logout(self, **args):
        return login_service.logout(**args)

    # 代理websocket请求的时候, 在收到websocket请求后, 与upstream建立websocket连接, 返回connection
    async def get_up_websocket(self, prev_request, handler):
        ws = await gateway_service.get_up_websocket(prev_request)
        # 启动一个异步的task来进行接收upstream的数据，并转发到downstream
        import tornado.ioloop
        io_loop = tornado.ioloop.IOLoop.current()
        io_loop.spawn_callback(self._recv_up_message, ws, handler)
        return ws

    # 接收upstream的数据，并转发到downstream
    async def _recv_up_message(self, ws, handler):
        try:
            while ws.closed is False:
                recv_message = await ws.recv()
                await handler.write_message(recv_message, binary=True)
        except Exception:
            handler.close()
