import socket

def start_client(username):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('127.0.0.1', 9999))

    # 发送用户名信息给服务端
    client.send(username.encode('utf-8'))

    while True:
        message = input("Enter message: ")
        client.send(message.encode('utf-8'))

if __name__ == "__main__":
    username = input("Enter your username: ")
    start_client(username)
