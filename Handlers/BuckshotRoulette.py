import time
import blivedm
import blivedm.models.web as web_models
from Handlers.User import User
# 创建一个socket字典
connections = {}

# 创建用户列表
BuckShotUser_list = []



#  哔哩哔哩 恶魔轮盘赌的回调类
class BiliBiliBuckShotRouletteHandler(blivedm.BaseHandler):
    # # 演示如何添加自定义回调
    # _CMD_CALLBACK_DICT = blivedm.BaseHandler._CMD_CALLBACK_DICT.copy()
    #
    # # 入场消息回调
    # def __interact_word_callback(self, client: blivedm.BLiveClient, command: dict):
    #     print(f"[{client.room_id}] INTERACT_WORD: self_type={type(self).__name__}, room_id={client.room_id},"
    #           f" uname={command['data']['uname']}")
    # _CMD_CALLBACK_DICT['INTERACT_WORD'] = __interact_word_callback  # noqa

    # init
    def __init__(self, playing_time=400, timeout=60):
        # 正在玩的用户
        self.playing_user = None
        # 当前用户的最后一条消息时间
        self.last_message_time = None
        # 用户超时时间
        self.timeout = timeout
        # 当前用户玩游戏的时间
        self.playing_time = playing_time
        # 当前用户开始玩游戏的时间
        self.start_time = None

    def _on_heartbeat(self, client: blivedm.BLiveClient, message: web_models.HeartbeatMessage):
        print(f'[{client.room_id}] 心跳')

    def _on_danmaku(self, client: blivedm.BLiveClient, message: web_models.DanmakuMessage):
        # interact_word(self, client, message)
        print(f'[{client.room_id}] {message.uname}：{message.msg}')

    def _on_gift(self, client: blivedm.BLiveClient, message: web_models.GiftMessage):
        print(f'[{client.room_id}] {message.uname} 赠送{message.gift_name}x{message.num}'
              f' （{message.coin_type}瓜子x{message.total_coin}）')

    def _on_buy_guard(self, client: blivedm.BLiveClient, message: web_models.GuardBuyMessage):
        print(f'[{client.room_id}] {message.username} 购买{message.gift_name}')

    def _on_super_chat(self, client: blivedm.BLiveClient, message: web_models.SuperChatMessage):
        print(f'[{client.room_id}] 醒目留言 ¥{message.price} {message.uname}：{message.message}')


# 处理普通消息
def interact_word(self, client: blivedm.BLiveClient, message: web_models.DanmakuMessage):
    if message.msg == '上机':
        # 如果是已经在玩的用户，不做处理
        if self.playing_user == message.uname:
            return
        # 创建一个用户对象 添加到用户列表 要判断是否已经存在
        for user in BuckShotUser_list:
            if user.username == message.uname:
                user.set_online_status(True)
                user.start_timer()
                return
        user = User(message.uname)
        BuckShotUser_list.append(user)
        user.set_online_status(True)
        user.start_timer()
        print(f'[{client.room_id}] {message.uname} 上机')
        return
    # 如果是下机消息，将用户设置为离线状态 并且取消定时器 在用户列表中删除
    if message.msg == '下机':
        for user in BuckShotUser_list:
            if user.username == message.uname:
                user.set_online_status(False)
                print(f'[{client.room_id}] {message.uname} 下机')
                return
        print(f'[{client.room_id}] {message.uname} 下机')
        return
    # 如果是其他消息，把用户设置为在线状态
    for user in BuckShotUser_list:
        if user.username == message.uname:
            user.set_online_status(True)
            user.start_timer()

    # 如果当前没有正在玩的用户，选择最早上机的用户
    if self.playing_user is None:
        for user in BuckShotUser_list:
            if user.is_online:
                self.playing_user = user.username
                # 删除用户
                BuckShotUser_list.remove(user)
                self.last_message_time = time.time()
                self.start_time = time.time()
                break
            else:
                BuckShotUser_list.remove(user)
                break
    # 如果当前有正在玩的用户，判断是否玩够了
    if self.last_message_time is not None:
        if time.time() - self.last_message_time > self.playing_time:
            print(f'[{client.room_id}] {self.playing_user} 超时')
            self.playing_user = None
            self.last_message_time = None
            self.start_time = None
            return
    # 如果当前有正在玩的用户，根据最后一条消息的时间判断是否超时
    if self.last_message_time is not None:
        if time.time() - self.last_message_time > self.timeout:
            print(f'[{client.room_id}] {self.playing_user} 超时')
            self.playing_user = None
            self.last_message_time = None
            self.start_time = None
            return
    # 现在是在玩的用户，发送消息
    if self.playing_user is not None:
        if message.uname == self.playing_user:
            # 根据socket对象发送消息
            conn = connections.get(client.room_id, None)
            # 如果socket对象存在
            if conn is not None:
                # 如果socket对象有效
                if conn.fileno() > 0:
                    # 发送消息
                    conn.sendall(message.msg.encode('utf-8'))
                    print(f'[{client.room_id}] {message.uname} 发送消息 {message.msg}')
            self.last_message_time = time.time()
