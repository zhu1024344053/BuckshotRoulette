from threading import Timer


class User:
    def __init__(self, username):
        self.username = username
        self.is_online = False  # 默认情况下，用户为离线状态
        self.timer = None  # 定时器对象

    def set_online_status(self, status):
        self.is_online = status

    def start_timer(self, timeout=10):
        # 如果已经有定时器在运行，先取消之前的定时器
        if self.timer is not None and self.timer.is_alive():
            self.timer.cancel()
        # 启动新的定时器
        self.timer = Timer(timeout, self.timeout_callback)
        self.timer.start()

    def timeout_callback(self):
        # 用户超时，将其设置为离线状态
        self.set_online_status(False)
        print(f"{self.username} 在20秒内没有消息，已下线")
