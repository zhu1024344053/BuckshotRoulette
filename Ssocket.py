import socket
import threading

# 存储用户ID与客户端socket的映射关系
clients = {}


def handle_client(client_socket, user_id):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                print(f"Connection with {user_id} closed.")
                break

            print(f"Received message from {user_id}: {message}")

            # 在这里处理服务端发送消息给指定用户的逻辑
            # 例如，可以根据消息中的目标用户ID找到对应的socket，并发送消息

        except Exception as e:
            print(f"Error handling client {user_id}: {str(e)}")
            break

    # 当连接关闭时，从clients字典中移除对应的映射关系
    del clients[user_id]
    client_socket.close()


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 9999))
    server.listen()

    print("Server listening on port 9999...")

    while True:
        client_socket, addr = server.accept()
        print(f"Accepted connection from {addr}")

        # 获取用户ID信息
        user_id = client_socket.recv(1024).decode('utf-8')
        print(f"{addr} connected with user ID: {user_id}")

        # 将用户ID与客户端socket建立映射关系
        clients[user_id] = client_socket

        # 启动处理客户端的线程
        client_handler = threading.Thread(target=handle_client, args=(client_socket, user_id))
        client_handler.start()


if __name__ == "__main__":
    start_server()
