









<center>
  <font face="黑体" size = 100>
    《计算机网络》实验报告
  </font>
</center>
<center><font face="黑体" size = 4>
  </font>
</center>
<center><font face="黑体" size = 4>
  </font>
</center>
<center><font face="黑体" size = 4>
  </font>
</center>
<center><font face="黑体" size = 4>
  </font>
</center>
<center><font face="黑体" size = 4>
  </font>
</center>
<center><font face="黑体" size = 4>
  </font>
</center>







<center><font face="黑体" size = 5>
    报告日期:  2026年 10月 8日
  </font>
</center>




<div STYLE="page-break-after: always;"></div>



# Lab1 WireShark软件初探和常见网络命令的使用


## 实验目的和要求

- 初步了解WireShark软件的界面和功能
- 熟悉各类常用网络命令的使用

## 实验内容和原理

- Wireshark是PC上使用最广泛的免费抓包工具，可以分析大多数常见的协议数据包。有Windows版本、Linux版本和Mac版本，可以免费从网上下载
- 初步掌握网络协议分析软件Wireshark的使用，学会配置过滤器
- 根据要求配置Wireshark，捕获某一类协议的数据包
- 在PC机上熟悉常用网络命令的功能和用法: Ping.exe，Netstat.exe, Telnet.exe, Tracert.exe, Arp.exe, Ipconfig.exe, Net.exe, Route.exe, Nslookup.exe
- 利用WireShark软件捕捉上述部分命令产生的数据包

## 主要仪器设备

- 联网的PC机
- WireShark协议分析软件

## 操作方法与实验步骤

1. 安装网络包捕获软件Wireshark
2. 配置网络包捕获软件，捕获所有类型的数据包
3. 配置网络包捕获软件，只捕获特定类型的包
4. 在Windows命令行方式下，执行适当的命令，完成以下功能(请以管理员身份打开命令行)：
   - 测试到特定地址的联通性、数据包延迟时间
   - 显示本机的网卡物理地址、IP地址
   - 显示本机的默认网关地址、DNS服务器地址
   - 显示本机记录的局域网内其它机器IP地址与其物理地址的对照表
   - 显示从本机到达一个特定地址的路由
   - 显示某一个域名的IP地址
   - 显示已经与本机建立TCP连接的端口、IP地址、连接状态等信息
   - 显示本机的路由表信息，并手工添加一个路由
   - 显示本机的NetBIOS名称
   - 显示局域网内某台机器的共享资源
   - 使用telnet连接WEB服务器的端口，输入（\<cr\>表示回车）获得该网站的主页内容：
     - GET / HTTP/1.1
     - Host:www.baidu.com

​	5. 利用WireShark实时观察在执行上述命令时，哪些命令会额外产生数据包，并记录这些数据包的种类。

## <span id='result'> 实验结果与分析 </span>

- 运行Wireshark软件，主界面是由哪几个部分构成？各有什么作用？

<img src="C:\Users\***\Pictures\Screenshots\Screenshot 2026-10-08 184059.png" alt="Screenshot 2026-10-08 184059" style="zoom: 33%;" />

菜单栏：Wireshark的菜单栏

工具栏：包含各种常用功能的快捷按钮，提供快速访问菜单中经常用到的项目的功能。

过滤器：提供处理当前显示过滤得方法。

Packet List（图中蓝色框部分）：显示每个数据帧的摘要。这里采用表格的形式列出了当前捕获文件中的所有数据包，其中包括了数据包序号、数据包捕获的相对时间、数据包的源地址和目标地址、数据包的协议以及在数据包中找到的概况信息等。

Packet Details（图中绿色框的左半部分）：分析数据包的详细信息。这个面板分层次地显示了一个数据包中的内容，并且可以通过展开或是收缩来显示这个数据包中所捕获的全部内容。

Packet Bytes（图中绿色框的右半部分）：以十六进制和ASCII码的形式显示数据包的内容。这里显 示了一个数据包未经处理的原始样子，也就是在链路上传播时的样子。

状态栏（图的底部）：包含有专家信息、注释、包的数量和Profile。

- 开始捕获网络数据包，你看到了什么？有哪些协议？

看到了Packet List中滚动过各种网络数据包，不同的协议、SourceIP、DestinationIP。

有`TCP / SSL / TLS / DNS / SSDP / IGMP / LLMNR / ICMP / HTTP / MDNS`等等协议

- 配置显示过滤器，让界面只显示某一协议类型的数据包。

设置显示过滤器为`tcp`协议，显示了`HTTP / TCP / TLS`三种协议

<img src="C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20261008185648202.png" alt="image-20261008185648202" style="zoom:33%;" />

这是由于`HTTP / TLS`是承载在`TCP`协议上的协议，因此也会被显示。

- 配置捕获过滤器，只捕获某类协议的数据包。

暂停捕获后，在上方菜单栏的`捕获`选项下选择`选项`打开`捕获选项`菜单，在页面下方的捕获过滤器中设置`tcp`协议

<img src="C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20261008190504476.png" alt="image-20261008190504476" style="zoom:33%;" />

- 利用ping, ipconfig, arp, tracert, nslookup, nbtstat, route, netstat, NET SHARE, telnet命令完成在实验步骤4中列举的11个功能。

| 指令                                                                  | 截图                                                                                                                                                                                                                                                                                                                                                                                                           | 结论                                         |
| ------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------ |
| ping 8.8.8.8                                                        | <img src="C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20261008191759811.png" alt="image-20261008191759811" style="zoom: 33%;" />                                                                                                                                                                                                                                                         | 从8.8.8.8接收到回复，证明联通<br>平均延迟为 118ms          |
| ipconfig/all                                                        | <img src="C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20261008192210041.png" alt="image-20261008192210041" style="zoom:33%;" />                                                                                                                                                                                                                                                          | 显示本机的网卡物理地址、IP地址 <br/>显示本机的默认网关地址、DNS服务器地址 |
| arp -a                                                              | <img src="C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20261008192414758.png" alt="image-20261008192414758" style="zoom:33%;" />                                                                                                                                                                                                                                                          | 显示本机记录的局域网内其它机器IP地址与其物理地址的对照表              |
| tracert 8.8.8.8                                                     | <img src="C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20261008193144508.png" alt="image-20261008193144508" style="zoom:33%;" />                                                                                                                                                                                                                                                          | 显示从本机到达一个特定地址的路由                           |
| nslookup www.baidu.com                                              | ![image-20261008193752887](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20261008193752887.png)                                                                                                                                                                                                                                                                                            | 显示某一个域名的IP地址                               |
| netstat -n                                                          | <img src="C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20261008193958875.png" alt="image-20261008193958875" style="zoom:33%;" />                                                                                                                                                                                                                                                          | 显示已经与本机建立TCP连接的端口、IP地址、连接状态等信息             |
| route print & route add 255.0.0.0 mask 255.0.0.0 19.162.0.1         | <img src="C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20261008194056936.png" alt="image-20261008194056936" style="zoom:33%;" />![Screenshot 2026-10-08 194450](C:\Users\***\Pictures\Screenshots\Screenshot 2026-10-08 194450.png)<img src="C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20261008194524384.png" alt="image-20261008194524384" style="zoom:33%;" /> | 显示本机的路由表信息，并手工添加一个路由                       |
| nbtstat -n                                                          | <img src="C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20261008195044139.png" alt="image-20261008195044139" style="zoom:33%;" />                                                                                                                                                                                                                                                          | 显示本机的NetBIOS名称                             |
| NET SHARE                                                           | ![image-20261008195129595](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20261008195129595.png)                                                                                                                                                                                                                                                                                            | 显示局域网内某台机器的共享资源                            |
| telnet www.baidu.com <br/>`GET / HTTP/1.1`<br/>`HOST:www.baidu.com` | <img src="C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20261008200136157.png" alt="image-20261008200136157" style="zoom:33%;" />                                                                                                                                                                                                                                                          | 使用telnet连接WEB服务器的端口                        |



- 观察使用ping命令时在WireShark中出现的数据包并捕获。这是什么协议？

`ICMP`协议（图片在表格中）

- 观察使用tracert命令时在WireShark中出现的数据包并捕获。这是什么协议？

`ICMP`协议（图片在表格中）

- 观察使用nslookup命令时在WireShark中出现的数据包并捕获。这是什么协议？

`DNS`协议（图片在表格中）

- 观察使用telnet命令时在WireShark中出现的数据包并捕获。这是什么协议？

<img src="C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20261008201122553.png" alt="image-20261008201122553" style="zoom:33%;" />

有`TCP / HTTP`协议

### 思考题

- WireShark的两种过滤器有什么不同？

捕获过滤只能识别链路层、网络层、传输层字段（IP、端口、协议类型），而显示过滤能解析所有协议字段，包括应用层（HTTP、DNS 等）

捕获过滤无法在正在捕获数据包时改变，显示过滤可以

捕获过滤发生在捕获前，显示过滤发生在捕获后

- 哪些网络命令会产生在WireShark中产生数据包，为什么？

`ping tracert nslookup nbtstat telnet`会产生数据包，因为需要向外发送数据包来查询或访问

- ping发送的是什么类型的协议数据包？什么时候会出现ARP消息？ping一个域名和ping一个IP地址出现的数据包有什么不同？

`ICMP`协议

在不知道通讯对方的MAC地址时会产生ARP消息

ping域名时会比ping IP多出`DNS`查询域名的IP地址

## 讨论、心得

由于做实验时开着实验网站和一些其他网页，Wireshark捕获到了许多不相干的数据包，需要自己仔细辨别哪些是实验命令产生的，哪些是网页产生的，注意观察Source IP、Destination IP和Info就行。