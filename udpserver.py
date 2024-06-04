import socket
import random
import time
import select


class Server:
    # 指定丢包率，创建套接字，并设置为非阻塞
    def __init__(self, server_ip, server_port, drop_pct=0.6, time_out=0.1):
        self.server_ip = server_ip
        self.server_port = server_port
        self.drop_pct = drop_pct
        self.time_out = time_out
        # 创建套接字
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_address = (server_ip, server_port)
        self.server_socket.bind(server_address)
        print(f"Server is listening on {server_ip}:{server_port}")
        self.server_socket.setblocking(False)
        self.clients = {}

    # 模拟TCP连接建立的过程
    def connection(self, client_addr):
        syn_ack_message = b'SYN_ACK'
        self.clients[client_addr] = True
        self.server_socket.sendto(syn_ack_message, client_addr)
        # try:
        #     res, addr = self.server_socket.recvfrom(1024)
        #     if res == b'ACK' and addr == client_addr:
        #         return True
        # except BlockingIOError:
        #     pass
        # return False

    # 模拟TCP断开建立的过程
    def disconnection(self, client_addr):
        fin_ack_message = b'FIN_ACK'
        self.server_socket.sendto(fin_ack_message, client_addr)
        del self.clients[client_addr]
        # try:
        #     res, addr = self.server_socket.recvfrom(1024)
        #     print(res.decode())
        #     if res == b'ACK' and addr == client_addr:
        #         return True
        # except BlockingIOError:
        #     pass
        #

    def response(self, client_addr, message):
        # random构造丢包
        if random.random() < self.drop_pct:
            print(f"Drop packet from{client_addr}")
            return
        # 构建response报文
        # seq_no和ver与收到的报文相同,other_data存放系统响应时间
        seq_no = message[:2]
        ver = message[2:3]
        server_time = time.strftime('%H-%M-%S').encode()
        other_data = server_time + b' ' * (200 - len(server_time))
        response = seq_no + ver + other_data

        # 模拟延迟处理
        time.sleep(random.uniform(0.0, self.time_out))

        self.server_socket.sendto(response, client_addr)
        print(f"Send response to {client_addr}")

    def run(self):
        while True:
            r_list, w_list, e_list = select.select([self.server_socket], [], [], 1)
            for s in r_list:
                #   如果服务器有数据可读
                if s is self.server_socket:
                    try:
                        message, client_addr = self.server_socket.recvfrom(1024)
                        if client_addr not in self.clients:
                            self.clients[client_addr] = False
                        client_status=self.clients[client_addr]
                        if message == b'SYN' and not client_status:
                            self.connection(client_addr)
                            print(f"Connection established with {client_addr}")
                            continue

                        elif message == b'FIN' and client_status:
                            self.disconnection(client_addr)
                            print(f"Connection terminated with {client_addr}")
                            continue
                        elif client_status:
                            self.response(client_addr, message)
                        else:
                            print(message.decode())
                            print(f"Received message from unknown client {client_addr}")
                    except BlockingIOError as e:
                        continue
                    except Exception as e:
                        print(f"Unexpected error: {e}")
    def close_socket(self):
        self.server_socket.close()


def main():
    server_ip = '127.0.0.1'  # 改为虚拟机ip，如192.168.227.129，ifconfig查看
    server_port = 12345
    server = Server(server_ip, server_port)  # 如果修改丢包率和超时时间可以加上这两个参数
    try:
        server.run()
    except KeyboardInterrupt:
        server.close_socket()


if __name__ == "__main__":
    main()

# # server的IP和端口
# server_ip = '127.0.0.1'  # 改为虚拟机ip，如192.168.227.129，ifconfig查看
# server_port = 12345
# # 创建UDP套接字
# server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# server_address = (server_ip, server_port)
# server_socket.bind(server_address)
# print(f"Server is listening on {server_ip}:{server_port}")
#
# # 设置丢包率
# drop_pct = 0.6
#
#
# # 模拟TCP连接建立的过程
# def connection(client_addr):
#     syn_ack_message = b'SYN_ACK'
#     server_socket.sendto(syn_ack_message, client_addr)
#     try:
#         res, addr = server_socket.recvfrom(1024)
#         if res == b'ACK':
#             return True
#     except socket.timeout:
#         pass
#     return False
#
#
# # 模拟TCP断开建立的过程
# def disconnection(client_addr):
#     fin_ack_message = b'FIN_ACK'
#     server_socket.sendto(fin_ack_message, client_addr)
#     try:
#         res, addr = server_socket.recvfrom(1024)
#         if res == b'ACK':
#             return True
#     except socket.timeout:
#         pass
#     return False
#
#
# while True:
#     message, client_addr = server_socket.recvfrom(1024)
#
#     if message == b'SYN':
#         if connection(client_addr):
#             print(f"Connection established with {client_addr}")
#         else:
#             print("Connection failed")
#         continue
#
#     if message == b'FIN':
#         if disconnection(client_addr):
#             print(f"Connection terminated with {client_addr}")
#         else:
#             print("Disconnection failed")
#         continue
#
#     # random构造丢包
#     if random.random() < drop_pct:
#         print(f"Drop packet from{client_addr}")
#         continue
#
#     # 构建response报文
#     # seq_no和ver与收到的报文相同,other_data存放系统响应时间
#     seq_no = message[:2]
#     ver = message[2:3]
#     server_time = time.strftime('%H-%M-%S').encode()
#     other_data = server_time + b' ' * (200 - len(server_time))
#     response = seq_no + ver + other_data
#
#     # 模拟延迟处理
#     time.sleep(random.uniform(0.0, 0.1))
#
#     server_socket.sendto(response, client_addr)
#     print(f"Send response to {client_addr}")
#
# server_socket.close()
