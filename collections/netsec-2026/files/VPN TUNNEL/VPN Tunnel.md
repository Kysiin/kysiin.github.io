# VPN Tunnel

60.5 V(77)

## 1.设置网路

### 测试

1. 主机 U 可以与 VPN Server 通信。

![image-20260421195615282](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260421195615282.png)

2. VPN Server可以与主机 V 通信。

![image-20260421195253430](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260421195253430.png)

3. 主机 U 应该不能与主机 V 通信。

![image-20260421195934135](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260421195934135.png)

4. 在路由器上运行 tcpdump，并嗅探每个网络上的流量以测试你是否可以捕获数据包。

![image-20260421195849695](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260421195849695.png)

![image-20260421200039722](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260421200039722.png)

## 2.创建和配置 TUN 接口

### 2.A

修改前：

![image-20260421200405531](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260421200405531.png)

修改后：

![image-20260421200734593](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260421200734593.png)

只需将`ifr = struct.pack('16sH', b'tun%d', IFF_TUN | IFF_NO_PI)`改为`ifr = struct.pack('16sH', b'wang%d', IFF_TUN | IFF_NO_PI)`即可

### 2.B

![image-20260421201008573](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260421201008573.png)

已成功将接口开启

### 2.C

- 在主机 U 上，ping 内部网络 192.168.60.0/24 中的主机，tun.py 是否打印出任何内容？为什么？

不打印

- 在主机 U 上，ping 一下 192.168.53.0/24 网络中的主机。tun.py 程序打印出了什么？发生了什么事？为什么？

![image-20260421201400989](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260421201400989.png)

打印出了

### 2.D

```python
while True:
  # 从tun接口获取一个数据包
  packet = os.read(tun, 2048)
  if packet:
    ip = IP(packet)
    print(ip.summary())
    if ICMP in ip and ip[ICMP].type == 8: #如果是ICMP echo request
      print("  -> ICMP echo request detected, constructing reply...")
      reply = IP(src=ip.dst, dst=ip.src) / ICMP(type=0, id=ip[ICMP].id, seq=ip[ICMP].seq) / ip[ICMP].payload
      print("  -> Sending echo reply: {}".format(reply.summary()))
      os.write(tun, bytes(reply))
```

`ping 192.168.53.5`后得到

![image-20260421203242474](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260421203242474.png)

```python
while True:
  # 从tun接口获取一个数据包
  packet = os.read(tun, 2048)
  if packet:
    ip = IP(packet)
    print(ip.summary())
    if ICMP in ip and ip[ICMP].type == 8: #如果是ICMP echo request
      print("  -> ICMP echo request detected, constructing reply...")
      print("  -> Sending echo reply: {}".format(reply.summary()))
      os.write(tun, bytes("Hello World", encoding='utf-8'))
```

无法收到回复的数据包

![image-20260421205331926](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260421205331926.png)

## 3

```python
#!/usr/bin/env python3

import fcntl, struct, os, socket
from scapy.all import *

TUNSETIFF = 0x400454ca
IFF_TUN   = 0x0001
IFF_NO_PI = 0x1000

SERVER_IP  = "10.9.0.11"
SERVER_PORT = 9090

tun = os.open("/dev/net/tun", os.O_RDWR)
ifr = struct.pack('16sH', b'tun%d', IFF_TUN | IFF_NO_PI)
ifname_bytes = fcntl.ioctl(tun, TUNSETIFF, ifr)
ifname = ifname_bytes.decode('UTF-8')[:16].strip("\x00")
print("Interface Name: {}".format(ifname))

os.system("ip addr add 192.168.53.99/24 dev {}".format(ifname))
os.system("ip link set dev {} up".format(ifname))

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while True:
  packet = os.read(tun, 2048)
  if packet:
      sock.sendto(packet, (SERVER_IP, SERVER_PORT))
```

`ping 192.168.53.3`后

![image-20260421210259220](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260421210259220.png)

`ping 192.168.60.5`后，无法ping通

![image-20260421210333694](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260421210333694.png)

添加`ip route add 192.168.60.0/24 dev tun0 via 192.168.53.99`

![image-20260421210532442](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260421210532442.png)

成功

分别在U和server上tcpdump

![image-20260421210827727](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260421210827727.png)

两者同时出现，数据包通过了隧道。

## 4.设置VPN服务器

```python
#!/usr/bin/env python3

import fcntl, struct, os, socket
from scapy.all import *

TUNSETIFF = 0x400454ca
IFF_TUN   = 0x0001
IFF_NO_PI = 0x1000

SERVER_IP  = "10.9.0.11"
SERVER_PORT = 9090

#创建tun
tun = os.open("/dev/net/tun", os.O_RDWR)
ifr = struct.pack('16sH', b'wang%d', IFF_TUN | IFF_NO_PI)
ifname_bytes = fcntl.ioctl(tun, TUNSETIFF, ifr)
ifname = ifname_bytes.decode('UTF-8')[:16].strip("\x00")
print("Interface Name: {}".format(ifname))

os.system("ip addr add 192.168.53.99/24 dev {}".format(ifname))
os.system("ip link set dev {} up".format(ifname))

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while True:
  packet = os.read(tun, 2048) #从socket获取数据
  if packet:
      sock.sendto(packet, (SERVER_IP, SERVER_PORT))#写入tun接口
```

![image-20260421212927432](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260421212927432.png)

可以看到V已经接收到ICMP包

## 5

tun_server.py

```python
#!/usr/bin/env python3

import fcntl, struct, os, socket, select
from scapy.all import *

TUNSETIFF = 0x400454ca
IFF_TUN   = 0x0001
IFF_NO_PI = 0x1000

tun = os.open("/dev/net/tun", os.O_RDWR)
ifr = struct.pack('16sH', b'wang%d', IFF_TUN | IFF_NO_PI)
ifname_bytes  = fcntl.ioctl(tun, TUNSETIFF, ifr)
ifname = ifname_bytes.decode('UTF-8')[:16].strip("\x00")
print("Interface Name: {}".format(ifname))

os.system("ip addr add 192.168.53.1/24 dev {}".format(ifname))
os.system("ip link set dev {} up".format(ifname))

IP_A = "0.0.0.0"
PORT = 9090

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((IP_A, PORT))

client_addr = None

while True:
      ready, _, _ = select.select([sock, tun], [], [])

      for fd in ready:
          if fd is sock:
              # 从隧道收到数据包 → 写入 TUN，交给内核路由到主机 V
              data, (ip, port) = sock.recvfrom(2048)
              client_addr = (ip, port)
              pkt = IP(data)
              print("From socket <==: {} --> {}".format(pkt.src, pkt.dst))
              os.write(tun, data)

          if fd is tun:
              # 从 TUN 收到返回包 → 通过 socket 发回主机 U
              packet = os.read(tun, 2048)
              pkt = IP(packet)
              print("From tun    ==>: {} --> {}".format(pkt.src, pkt.dst))
              if client_addr:
                  sock.sendto(packet, client_addr)
```

tun_client.py

```python
#!/usr/bin/env python3

import fcntl, struct, os, socket, select
from scapy.all import *

TUNSETIFF = 0x400454ca
IFF_TUN   = 0x0001
IFF_NO_PI = 0x1000

SERVER_IP  = "10.9.0.11"
SERVER_PORT = 9090

tun = os.open("/dev/net/tun", os.O_RDWR)
ifr = struct.pack('16sH', b'wang%d', IFF_TUN | IFF_NO_PI)
ifname_bytes = fcntl.ioctl(tun, TUNSETIFF, ifr)
ifname = ifname_bytes.decode('UTF-8')[:16].strip("\x00")
print("Interface Name: {}".format(ifname))

os.system("ip addr add 192.168.53.99/24 dev {}".format(ifname))
os.system("ip link set dev {} up".format(ifname))
os.system("ip route add 192.168.60.0/24 dev {} via 192.168.53.1".format(ifname))

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while True:
  ready, _, _ = select.select([sock, tun], [], [])

  for fd in ready:
    if fd is sock:
      # 从隧道收到数据包 → 写入 TUN，交给内核
      data, (ip, port) = sock.recvfrom(2048)
      pkt = IP(data)
      print("From socket <==: {} --> {}".format(pkt.src, pkt.dst))
      os.write(tun, data)

    if fd is tun:
      # 从 TUN 收到数据包 → 通过 socket 发往 VPN Server
      packet = os.read(tun, 2048)
      pkt = IP(packet)
      print("From tun    ==>: {} --> {}".format(pkt.src, pkt.dst))
      sock.sendto(packet, (SERVER_IP, SERVER_PORT))
```



![image-20260421213856592](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260421213856592.png)

![image-20260421213944422](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260421213944422.png)

![image-20260421214027578](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260421214027578.png)

![image-20260421214037371](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260421214037371.png)

数据包流向：

 主机U → wang0 → tun_client.py → UDP隧道 → tun_server.py → TUN → 内核 → 主机V

 主机V → 内核 → TUN → tun_server.py → UDP隧道 → tun_client.py → wang0 → 主机U

## 6

中断后telnet无法显示输入的字符，但链接没有断开，重新连接后，刚刚输入的字符显示了出来

![image-20260421214320262](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260421214320262.png)

## 7

`ip route add 192.168.53.0/24 via 192.168.60.11`

![image-20260421214933975](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260421214933975.png)

## 8

在client中修改了

```python
os.system("ip addr add 192.168.53.12/24 dev {}".format(ifname))
```

在server中修改了

```python
os.system("ip route add 192.168.50.0/24 dev {} via 192.168.53.12".format(ifname))
```

在用户U上tcpdump可以看到封装后的udp包

![image-20260421220157625](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260421220157625.png)

## 9

```python
#!/usr/bin/env python3

import fcntl, struct, os
from scapy.all import *

TUNSETIFF = 0x400454ca
IFF_TAP   = 0x0002
IFF_NO_PI = 0x1000

tap = os.open("/dev/net/tun", os.O_RDWR)
ifr = struct.pack('16sH', b'tap%d', IFF_TAP | IFF_NO_PI)
ifname_bytes = fcntl.ioctl(tap, TUNSETIFF, ifr)
ifname = ifname_bytes.decode('UTF-8')[:16].strip("\x00")
print("Interface Name: {}".format(ifname))

os.system("ip addr add 192.168.53.99/24 dev {}".format(ifname))
os.system("ip link set dev {} up".format(ifname))

while True:
  packet = os.read(tap, 2048)
  if packet:
      ether = Ether(packet)
      print(ether.summary())
```

`ping 192.168.53.1`

![image-20260421221014152](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260421221014152.png)

```python
while True:#arp回复
  packet = os.read(tap, 2048)
  if packet:
      print("--------------------------------")
      ether = Ether(packet)
      print(ether.summary())

      FAKE_MAC = "aa:bb:cc:dd:ee:ff"
      if ARP in ether and ether[ARP].op == 1:
          arp     = ether[ARP]
          newether = Ether(dst=ether.src, src=FAKE_MAC)
          newarp   = ARP(psrc=arp.pdst, hwsrc=FAKE_MAC,
                         pdst=arp.psrc, hwdst=ether.src, op=2)
          newpkt   = newether/newarp
          print("***** Fake response: {}".format(newpkt.summary()))
          os.write(tap, bytes(newpkt))
```

`arping -I tap0 192.168.53.33`

![image-20260421221254869](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260421221254869.png)

`arping -I tap0 1.2.3.4`

![image-20260421221406862](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260421221406862.png)