# -*- coding: utf-8 -*-
import asyncio
import http.cookies
import socket
from typing import *
import aiohttp
from aiohttp import web  # 添加导入语句
import blivedm
import blivedm.models.web as web_models
from Handlers.BuckshotRoulette import BiliBiliBuckShotRouletteHandler


# 直播间ID的取值看直播间URL
TEST_ROOM_IDS = [
    31882096,
    # 3865675,
]
roomdata = {}
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('0.0.0.0', 9999))
server.settimeout(3)  # Set a timeout of 3 seconds
server.listen(1000)

# 这里填一个已登录账号的cookie。不填cookie也可以连接，但是收到弹幕的用户名会打码，UID会变成0
# SESSDATA = '_uuid=106478F41-E128-D596-A1C7-13EB691A1A7D11144infoc;LIVE_BUVID=AUTO4717062779132342;buvid4=9D4D90F5-41E1-79B8-DDC6-D46D77301D9E49760-024012614-p6V1/wFZ2Zs/+kaywlMNvw%3D%3D;buvid3=16D038B7-2672-1E1A-27B7-FF09A385D16613360infoc;b_nut=1706277912;fingerprint=c361479fb876345501fd2db89420adea;PVID=1;b_lsid=2F431F21_18D4B4F7053;buvid_fp=EAB11005-02BE-6062-FDDB-6C5D86DD586D49760infoc;buvid_fp_plain=undefined;bili_jct=744b01fe5f8729cec99ea3db0f3a2b7e;DedeUserID=233266909;DedeUserID__ckMd5=7a9ad20d61d079e0;sid=g6mij8pj;'
# SESSDATA = 'ffa01b7f%2C1721836551%2C91ff0%2A11CjCr1n-2iMjEQ0hcwOeaLc_aLzXTyoA58z6sT0Vtn98nSLFCaoXqrJ3XCB-QhhdJeR8SVnY5ZUFPODVOdlJwdGxNaFV3THNQRWJnak1hUzNQR2VvUGNtVlFidU5uWHpVMUhtMzlPdTd5Q0VvalBQQ2cyM1dZcDJnczVxcHpBZG1CaVJ2SU45ODNBIIEC'
SESSDATA = 'dd9f2a30%2C1722178077%2C39404%2A11CjDDkZTvdCqr3R2msdxMg7OgHyuZ77XgJ8LVgodVyoWDj68rWILNY_Vo8Mx5pwwoTSsSVnFkTWMzcDZCeHBfZm9ubkNhYkxCQmYzSU9JQVR4TnBsTTByZ056WmVIalUzc0dINzZFSnd2R2MydFFKM3I1a1oycWVmak1yaE5wT1JETVc4VG1DaUFnIIEC'

session: Optional[aiohttp.ClientSession] = None

async def process_user_info(request):
    try:
        data = await request.json()
        username = data.get("UserName", "")
        password = data.get("PassWord", "")
        user_ip = data.get("UserIP", "")
        user_port = data.get("UserPort", "")
        room_id = data.get("RoomID", 0)
        if room_id not in TEST_ROOM_IDS:
            TEST_ROOM_IDS.append(room_id)
        # 在这里可以添加逻辑，比如展示信息或进行其他处理
        # 创建一个socket对象
        conn = handle_connection(room_id,user_ip,user_port)
        if conn is None:
            return web.Response(text=f"链接失败", status=500)
        print(f"Received POST request with JSON data: {data}")
        asyncio.create_task(run_single_client(room_id))
        return web.Response(text="Request processed successfully")
    except Exception as e:
        return web.Response(text=f"Error processing request: {str(e)}", status=500)

# 删除room_id
async def delete_room_id(request):
    try:
        data = await request.json()
        room_id = data.get("RoomID", 0)
        if room_id in TEST_ROOM_IDS:
            TEST_ROOM_IDS.remove(room_id)
            if room_id in roomdata:
                for client in roomdata[room_id]:
                    await client.stop_and_close()
                del roomdata[room_id]
        # 获取socket对象
        conn = connections.get(room_id, None)
        if conn is not None:
            conn.close()
            del connections[room_id]
        return web.Response(text="Request processed successfully")
    except Exception as e:
        return web.Response(text=f"Error processing request: {str(e)}", status=500)
async def main():
    init_session()
    try:
        app = web.Application()

        app.router.add_post('/process_user_info', process_user_info)
        # 删除room_id
        app.router.add_post('/delete_room_id', delete_room_id)
        await asyncio.create_task(web._run_app(app, port=8080,host='127.0.0.1'))
    finally:
        print("finally")
        await session.close()


# 创建一个socket字典
def handle_connection(room_id,HOST,PORT):
    global connections
    # 连接到服务端
    # 连接到服务端
    try:
        # 绑定主机和端口号

        conn, addr = server.accept()
        print(f'Connected by {addr}')
        # 根据客户端地址为每个连接对象创建一个唯一的key
        connections[room_id] = conn
        return conn
    except ConnectionRefusedError:
        print('Connection failed')
        return None




def init_session():
    cookies = http.cookies.SimpleCookie()
    cookies['SESSDATA'] = SESSDATA
    cookies['SESSDATA']['domain'] = 'bilibili.com'

    global session
    session = aiohttp.ClientSession()
    session.cookie_jar.update_cookies(cookies)


async def run_single_client(room_id):
    """
    演示监听一个直播间
    """

    clients = [blivedm.BLiveClient(room_id, session=session) ]

    handler = BiliBiliBuckShotRouletteHandler()
    for client in clients:
        roomdata[room_id] = {client}
        client.set_handler(handler)
        client.start()

    try:
        await asyncio.gather(*(
            client.join() for client in clients
        ))
    finally:
        await asyncio.gather(*(
            client.stop_and_close() for client in clients
        ))


async def run_multi_clients():
    """
    演示同时监听多个直播间
    """
    clients = [blivedm.BLiveClient(room_id, session=session) for room_id in TEST_ROOM_IDS]
    handler = BiliBiliBuckShotRouletteHandler()
    for client in clients:
        client.set_handler(handler)
        client.start()

    try:
        await asyncio.gather(*(
            client.join() for client in clients
        ))
    finally:
        await asyncio.gather(*(
            client.stop_and_close() for client in clients
        ))



if __name__ == '__main__':
    # 添加创建HTTP服务器的代码
    asyncio.run(main())

