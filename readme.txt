UDP客户端-服务器模拟
#1. 项目说明
本项目模拟了一个基于UDP的客户端-服务器通信，自定义实现了简单的 TCP 连接建立和断开过程：建立连接时，客户端发送SIN，服务器端返回SIN_ACK;断开连接时，客户端发送FIN，服务器端返回FIN_ACK。服务器监听客户端连接，客户端向服务器发送指定数目的数据包时（默认为12个，可自定义），服务器模拟丢包过程和拥塞过程，随机返回包含服务器的当前时间的报文。若客户端超出设置超时时间（默认为0.1s，可自定义）则进行重传，重传次数上限默认为2次（可自定义）；若收到则测量RTT（往返时间），记录服务器响应时间。在数据包传输完毕后客户端计算各种统计数据并汇总输出。

# 2. 运行环境

- Python 3.x
- 标准 Python 库：`socket`、`random`、`time`、`select`、`statistics`、`sys`、`datetime`

# 3. 运行服务器

(1) 服务器设置：
- 确保服务器机器的 IP 地址和端口可访问。
- 在服务器的终端或命令提示符中执行以下命令：
    python udpserver.py
(2) 服务器代码说明：
- `Server.__init__(self, server_ip, server_port, drop_pct=0.6, time_out=0.1)`：初始化服务器，绑定 IP 和端口，设置丢包率和超时时间。
- `Server.connection(self, client_addr)`：处理客户端的连接请求，发送 `SYN_ACK` 消息。
- `Server.disconnection(self, client_addr)`：处理客户端的断开请求，发送 `FIN_ACK` 消息。
- `Server.response(self, client_addr, message)`：处理并响应客户端的消息，模拟丢包和延迟。
- `Server.run(self)`：运行服务器，监听和处理客户端的请求。

# 4. 运行客户端

(1)客户端设置：
- 确保客户端机器能够访问服务器的 IP 地址和端口。
- 在客户端的终端或命令提示符中执行以下命令：
    python udpclient.py <ServerIP> <ServerPort> [time_out] [packet_num] [retras_times]
例如：
    python udpclient.py 127.0.0.1 12345 0.1 12 2 
    python udpclient.py 127.0.0.1 12345

(2) 客户端代码说明：
- `Client.__init__(self, server_ip, server_port, timeout=0.1, packet_num=12,retras_times=2)`：初始化客户端，设置服务器 IP 和端口，超时时间，数据包数目和最多重传次数。
- `Client.connection(self)`：处理与服务器的连接过程，发送 `SYN` 消息并等待 `SYN_ACK` 响应。
- `Client.disconnection(self)`：处理与服务器的断开过程，发送 `FIN` 消息并等待 `FIN_ACK` 响应。
- `Client.run(self)`：运行客户端，发送数据包，处理测量 RTT 并计算统计数据并汇总输出。
- `Client.close_socket(self)`：关闭客户端套接字。

# 5. 配置选项

- `drop_pct`：丢包率，默认值为 0.6（60% 的概率丢包）。
- `time_out`：服务器处理延迟时间，默认值为 0.1 秒。
- `timeout`：客户端等待服务器响应的超时时间，默认值为 0.1 秒。
- `packet_num`：客户端发送的数据包数量，默认值为 12。
- `retras_times`：客户端最多重传的次数，默认值为2。

# 6. 注意事项

- 请确保服务器和客户端的 IP 和端口配置正确，以便双方能够正常通信。
- 可以根据需要调整丢包率、超时时间、数据包数量和最多重传次数。

