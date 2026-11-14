# Sniffing and Spoofing - 副本

### 1.1

ifconfig得到网卡接口

![image-20260306161549793](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260306161549793.png)

```
br-75a05db36049
```

![image-20260306161910944](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260306161910944.png)



### 1.1A

```python
#!/usr/bin/env python3
from scapy.all import *

def print_pkt(pkt):
  pkt.show()

pkt = sniff(iface='br-75a05db36049', filter='icmp', prn=print_pkt)
```



ping hostA后

![image-20260306165744780](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260306165744780.png)

捕捉到

![image-20260306165717311](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260306165717311.png)

不用root权限

![image-20260306165929337](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260306165929337.png)

`Operation not permitted`显示不用root权限，程序无法打开网络接口的Raw Socket，从而捕获不了经过该接口的数据包。

### 1.1B

- 只捕获 ICMP 包：

`pkt = sniff(iface='br-75a05db36049', filter='icmp', prn=print_pkt)`

- 捕获来自某个特定 IP 地址并且目标端口号为 23 的 TCP 包：

`pkt = sniff(iface='br-75a05db36049', filter='tcp and src host 10.9.0.5 and dst port 23', prn=print_pkt)`

![image-20260306170936057](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260306170936057.png)

- 捕获来自或去往某个特定网络的包：

```python
#!/usr/bin/env python3
from scapy.all import *

def print_pkt(pkt):
  pkt.show()

pkt = sniff(iface='br-75a05db36049', filter='net 128.230.0.0/16', prn=print_pkt)
```

![image-20260306171225547](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260306171225547.png)

### 1.2

```python
>>> from scapy.all import *
>>> a = IP()
>>> a.dst = '10.9.0.5'
>>> b = ICMP()
>>> p = a/b
>>> send(p)
```



![image-20260310133835462](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260310133835462.png)

### 1.3

ttl=1

![image-20260310140626074](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260310140626074.png)

ttl=3

![image-20260310140810787](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260310140810787.png)

ttl=4

![image-20260310140823447](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260310140823447.png)

### 1.4

运行前

![image-20260310154747218](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260310154747218.png)

运行后

![image-20260310154654808](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260310154654808.png)

![image-20260310154851823](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260310154851823.png)



