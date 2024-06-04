import socket
import statistics
import time
import sys
import datetime


class Client:
    def __init__(self, server_ip, server_port, timeout=0.1, packet_num=12, retrans_times=2):
        self.server_ip = server_ip
        self.server_port = server_port
        self.timeout = timeout
        self.retrans_times = retrans_times
        # 创建UDP套接字
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # 设置超时时间
        self.client_socket.settimeout(self.timeout)
        self.packet_num = packet_num

    # 模拟TCP连接建立的过程，自定义：客户端请求发送SYN 服务器端返回SYN_ACK
    def connection(self):
        syn_message = b'SYN'
        self.client_socket.sendto(syn_message, (self.server_ip, self.server_port))
        try:
            res, server_addr = self.client_socket.recvfrom(1024)
            print(f"received the response of server:{res}")
            print("build connection")
            if res == b'SYN_ACK':
                return True
        except socket.timeout:
            print("timeout error,exit")
            pass
        return False

    # 模拟TCP断开建立的过程，自定义：客户端请求发送FIN 服务器端返回FIN_ACK
    def disconnection(self):
        fin_message = b'FIN'
        self.client_socket.sendto(fin_message, (self.server_ip, self.server_port))
        try:
            res, server_addr = self.client_socket.recvfrom(1024)
            if res == b'FIN_ACK':
                print(f"received the response of server:{res}")
                print("close connection")
                # ack_message = b'ACK'
                # client_socket.sendto(ack_message, (server_ip, server_port))
                return True
        except socket.timeout:
            pass
        return False

    def run(self):
        # 发送数据包,测量
        rtts = []
        cnt = 0
        First_response_time = None
        Last_response_time = None
        # seq no:[1,12] [1,packet_num] 可以指定包数目
        for i in range(1, self.packet_num + 1):
            # 构造报文
            # seq_no转换成两字节的字节序列;大端模式，高位字节在前
            seq_no = i.to_bytes(2, byteorder='big')
            # ver自定义为2
            ver = (2).to_bytes(1, byteorder='big')
            other_data = b'X' * 200
            send_message = seq_no + ver + other_data
            response = None
            # 最多重传retrans_times次
            for j in range(self.retrans_times+1):
                start_time = time.time()
                self.client_socket.sendto(send_message, (self.server_ip, self.server_port))
                try:
                    response, addr = self.client_socket.recvfrom(1024)
                    # 计算rtt并转换为ms
                    cur_time = time.time()
                    rtt = (cur_time - start_time) * 1000
                    rtts.append(rtt)
                    # 获取server的系统时间，除去空格
                    server_time = response[3:].decode().strip()
                    # 记录第一次和最后一次的响应时间 即为None时记录第一次 之后不断更新最后一次
                    if First_response_time is None:
                        First_response_time = server_time
                    Last_response_time = server_time
                    cnt += 1
                    # 格式化时间
                    server_time_formatted = datetime.datetime.strptime(server_time, "%H-%M-%S").strftime("%H:%M:%S")
                    # 每次接收到server发回来的包 都会显示server_addr seq.no,rtt,server响应时间
                    print(
                        f"Received response from {addr}: sequence_no={i}, RTT={rtt:.2f} ms, server_time={server_time_formatted}")
                    break
                # 请求超时
                except socket.timeout:
                    # 除了显示Request还会显示这是seq no报文的第几次请求超时
                    print(f"Request {i}, attempt {j + 1}: Request timed out")
                if j == self.retrans_times and response is None:
                    print(f"No response received.Request {i} failed")

        # 汇总结果并打印
        print("total:")
        # 计算接受数目和丢包率
        print(
            f"Packets received: {cnt}/{self.packet_num}, Packet loss: {((self.packet_num - cnt) / self.packet_num * 100):.2f}%")
        # 计算RTT最大值，最小值，平均值，标准差
        if rtts:
            max_rtt = max(rtts)
            min_rtt = min(rtts)
            avg_rtt = sum(rtts) / len(rtts)
            stddev_rtt = statistics.stdev(rtts)

            print(f"RTT: max={max_rtt:.2f} ms, min={min_rtt:.2f} ms, avg={avg_rtt:.2f} ms, stddev={stddev_rtt:.2f} ms")
            # 计算服务器整体响应时间
            if First_response_time and Last_response_time:
                FRT = time.strptime(First_response_time, "%H-%M-%S")
                LRT = time.strptime(Last_response_time, "%H-%M-%S")
                server_response_time = (LRT.tm_hour * 3600 + LRT.tm_min * 60 + LRT.tm_sec) - (
                        FRT.tm_hour * 3600 + FRT.tm_min * 60 + FRT.tm_sec)
                print(f"Server overall response time: {server_response_time} s")
        else:
            print("No response received")

    def close_socket(self):
        self.client_socket.close()


def get_arguments():
    # 检查命令行参数，用户可自定义超时时间和包数目
    if len(sys.argv) < 3:
        print("python3 udpclient.py <ServerIP> <ServerPort> [time_out] [packet_num][retrans_times]")
        sys.exit(1)
    # 从命令行获取服务器IP和端口号
    server_ip = sys.argv[1]
    server_port = int(sys.argv[2])
    time_out = 0.1
    packet_num = 12
    retrans_times = 2
    if len(sys.argv) > 3:
        time_out = float(sys.argv[3])
    if len(sys.argv) > 4:
        packet_num = int(sys.argv[4])
    if len(sys.argv) > 5:
        retrans_times = int(sys.argv[5])
    return server_ip, server_port, time_out, packet_num, retrans_times


def main():
    server_ip, server_port, time_out, packet_num, retrans_times = get_arguments()
    client = Client(server_ip, server_port, time_out, packet_num, retrans_times)
    if not client.connection():
        print("Connection error")
        client.close_socket()
        sys.exit(1)
    client.run()
    if client.disconnection():
        client.close_socket()


if __name__ == "__main__":
    main()
# # 创建UDP套接字
# client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# # 设置超时时间
# timeout = 0.1
# client_socket.settimeout(timeout)


# 模拟TCP连接建立的过程
# def connection():
#     syn_message = b'SYN'
#     client_socket.sendto(syn_message, (server_ip, server_port))
#     try:
#         res, server_addr = client_socket.recvfrom(1024)
#         print(f"received the response of server:{res}")
#         print("build connection")
#         if res == b'SYN_ACK':
#             # ack_message = b'ACK'
#             # client_socket.sendto(ack_message, (server_ip, server_port))
#             return True
#     except socket.timeout:
#         print("timeout error,exit")
#         pass
#     return False
#
#
# # 模拟TCP断开建立的过程
# def disconnection():
#     fin_message = b'FIN'
#     client_socket.sendto(fin_message, (server_ip, server_port))
#     try:
#         res, server_addr = client_socket.recvfrom(1024)
#         if res == b'FIN_ACK':
#             print(f"received the response of server:{res}")
#             print("close connection")
#             # ack_message = b'ACK'
#             # client_socket.sendto(ack_message, (server_ip, server_port))
#             return True
#     except socket.timeout:
#         pass
#     return False
#
#
# # 模拟TCP建立连接
# if not connection():
#     print("Connection error")
#     client_socket.close()
#     sys.exit(1)
#
# # 发送数据包,测量
# rtts = []
# cnt = 0
# First_response_time = None
# Last_response_time = None
# # seq no:[1,12]
# for i in range(1, 13):
#     # 构造报文
#     # seq_no转换成两字节的字节序列;大端模式，高位字节在前
#     seq_no = i.to_bytes(2, byteorder='big')
#     # ver自定义为2
#     ver = (2).to_bytes(1, byteorder='big')
#     other_data = b'X' * 200
#     send_message = seq_no + ver + other_data
#     response = None
#     # 最多重传两次
#     for j in range(3):
#         start_time = time.time()
#         client_socket.sendto(send_message, (server_ip, server_port))
#         try:
#             response, addr = client_socket.recvfrom(1024)
#             # 计算rtt并转换为ms
#             cur_time = time.time()
#             rtt = (cur_time - start_time) * 1000
#             rtts.append(rtt)
#             # 获取server的系统时间，除去空格
#             server_time = response[3:].decode().strip()
#             # 记录第一次和最后一次的响应时间 即为None时记录第一次 之后不断更新最后一次
#             if First_response_time is None:
#                 First_response_time = server_time
#             Last_response_time = server_time
#             cnt += 1
#             # 格式化时间
#             server_time_formatted = datetime.datetime.strptime(server_time, "%H-%M-%S").strftime("%H:%M:%S")
#             print(
#                 f"Received response from {addr}: sequence_no={i}, RTT={rtt:.2f} ms, server_time={server_time_formatted}")
#             break
#         # 请求超时
#         except socket.timeout:
#             print(f"Request {i}, attempt {j + 1}: Request timed out")
#         if j == 2 and response is None:
#             print(f"No response received.Request {i} failed")
# print("total:")
# # 计算接受数目和丢包率
# print(f"Packets received: {cnt}/12, Packet loss: {(12 - cnt) / 12 * 100:.2f}%")
# # 计算RTT最大值，最小值，平均值，标准差
# if rtts:
#     max_rtt = max(rtts)
#     min_rtt = min(rtts)
#     avg_rtt = sum(rtts) / len(rtts)
#     stddev_rtt = statistics.stdev(rtts)
#
#     print(f"RTT: max={max_rtt:.2f} ms, min={min_rtt:.2f} ms, avg={avg_rtt:.2f} ms, stddev={stddev_rtt:.2f} ms")
#     # 计算服务器整体响应时间
#     if First_response_time and Last_response_time:
#         FRT = time.strptime(First_response_time, "%H-%M-%S")
#         LRT = time.strptime(Last_response_time, "%H-%M-%S")
#         server_response_time = (LRT.tm_hour * 3600 + LRT.tm_min * 60 + LRT.tm_sec) - (
#                 FRT.tm_hour * 3600 + FRT.tm_min * 60 + FRT.tm_sec)
#         print(f"Server overall response time: {server_response_time} s")
# else:
#     print("No response received")
# 模拟TCP连接释放
# if disconnection():
#     client_socket.close()
