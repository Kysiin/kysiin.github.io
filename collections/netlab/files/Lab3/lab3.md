









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
    报告日期:  2026年 10月 31日
  </font>
</center>


# Lab3  网络接口与 IP 路由器


## 实验目的

- 学习掌握网络接口的工作原理
- 学习掌握ARP地址解析协议相关知识
- 学习掌握IP路由的工作原理

## 实验内容

- 实现network interface，为每个下一跳地址查找（和缓存）以太网地址，即实现地址解析协议ARP。
- 实现简易路由器，对于给定的数据包，确认发送接口以及下一跳的IP地址。

## 主要仪器设备

- 联网的PC机
- Linux虚拟机

## 操作方法与实验步骤
### 实现网络接口类
#### 组装以太网帧
以太网帧由两部分组成：**14 字节的头部** + **负载（payload）**

| 字段   | 长度  | 说明       |
| ---- | --- | -------- |
| dst  | 6   | 目的MAC地址  |
| src  | 6   | 源 MAC 地址 |
| type | 2   | 上层协议类型   |
`IPv4Datagram::serialize()` 返回一个 `BufferList`，就是"以太网帧的负载"
反序列化：接收端先从帧里取出负载，再交给 `IPv4Datagram::parse()`
arp：

| 字段                      | 长度  | 说明                                          |
| ----------------------- | --- | ------------------------------------------- |
| hardware_type           | 2   | 链路层类型                                       |
| protocol_type           | 2   | 网络层类型                                       |
| hardware_address_size   | 1   | MAC 地址长度                                    |
| protocol_address_size   | 1   | IP 地址长度                                     |
| opcode                  | 2   | OPCODE_REQUEST = 1 请求 / OPCODE_REPLY = 2 应答 |
| sender_ethernet_address | 6   | 发送方 MAC                                     |
| sender_ip_address       | 4   | 发送方 IP                                      |
| target_ethernet_address | 6   | 目标 MAC                                      |
| target_ip_address       | 4   | 目标 IP                                       |
序列化：`serialize()` 返回 `std::string`。发送时把它作为以太网帧负载

#### 代码实现
在`libsponge/network_interface.hh`中，添加了`ARPEntry`、`ARPRequestRecord`、`WaitingQueue`三个结构分别作为ARP 缓存条目、 ARP 请求发送记录、 等待 MAC 的数据报队列，并添加了一些辅助函数便于.cc文件的编写。具体实现如下：
```C
//辅助函数
NetworkInterface::ARPEntry *NetworkInterface::_find_arp_entry(uint32_t ip) {
    for (auto &e : _arp_cache) {
        if (e.ip == ip)
            return &e;
    }
    return nullptr;
}

NetworkInterface::ARPRequestRecord *NetworkInterface::_find_request_record(uint32_t ip) {
    for (auto &r : _arp_request_records) {
        if (r.ip == ip)
            return &r;
    }
    return nullptr;
}

NetworkInterface::ARPRequestRecord &NetworkInterface::_find_or_create_request_record(uint32_t ip) {
    if (auto *p = _find_request_record(ip))
        return *p;
    _arp_request_records.push_back(ARPRequestRecord{ip, 0});
    return _arp_request_records.back();
}

NetworkInterface::WaitingQueue *NetworkInterface::_find_waiting(uint32_t ip) {
    for (auto &w : _waiting_datagrams) {
        if (w.ip == ip)
            return &w;
    }
    return nullptr;
}

NetworkInterface::WaitingQueue &NetworkInterface::_find_or_create_waiting(uint32_t ip) {
    if (auto *p = _find_waiting(ip))
        return *p;
    _waiting_datagrams.push_back(WaitingQueue{ip, {}});
    return _waiting_datagrams.back();
}

void NetworkInterface::_send_arp_request(const uint32_t target_ip) {
    ARPMessage arp;
    arp.opcode = ARPMessage::OPCODE_REQUEST;
    arp.sender_ethernet_address = _ethernet_address;
    arp.sender_ip_address = _ip_address.ipv4_numeric();
    arp.target_ethernet_address = {};
    arp.target_ip_address = target_ip;

    EthernetFrame frame;
    frame.header().src = _ethernet_address;
    frame.header().dst = ETHERNET_BROADCAST;
    frame.header().type = EthernetHeader::TYPE_ARP;
    frame.payload() = arp.serialize();

    _frames_out.push(frame);

    // 记录/重置请求时间
    _find_or_create_request_record(target_ip).age_ms = 0;
}

void NetworkInterface::_send_ipv4_datagram(const InternetDatagram &dgram, const EthernetAddress &dst) {
    EthernetFrame frame;
    frame.header().src = _ethernet_address;
    frame.header().dst = dst;
    frame.header().type = EthernetHeader::TYPE_IPv4;
    frame.payload() = dgram.serialize();

    _frames_out.push(frame);
}

void NetworkInterface::_flush_waiting(const uint32_t ip) {
    auto *w = _find_waiting(ip);
    if (!w)
        return;

    auto *entry = _find_arp_entry(ip);
    if (!entry)
        return;

    const EthernetAddress dst = entry->eth_addr;
    while (!w->dgrams.empty()) {
        _send_ipv4_datagram(w->dgrams.front(), dst);
        w->dgrams.pop_front();
    }

    // 删除空的等待队列
    _waiting_datagrams.erase(
        std::remove_if(_waiting_datagrams.begin(),
                       _waiting_datagrams.end(),
                       [ip](const WaitingQueue &q) { return q.ip == ip; }),
        _waiting_datagrams.end());
}
```
并修改原来的DUMMYCODE如下：
```C
void NetworkInterface::send_datagram(const InternetDatagram &dgram, const Address &next_hop) {
    // convert IP address of next hop to raw 32-bit representation (used in ARP header)
    const uint32_t next_hop_ip = next_hop.ipv4_numeric();
    // 1. ARP 缓存命中
    if (auto *entry = _find_arp_entry(next_hop_ip)) {
        _send_ipv4_datagram(dgram, entry->eth_addr);
        return;
    }
    // 2. 缓存数据报
    _find_or_create_waiting(next_hop_ip).dgrams.push_back(dgram);
    // 3. 5 秒去重后广播 ARP 请求
    auto *rec = _find_request_record(next_hop_ip);
    if (rec == nullptr || rec->age_ms >= ARP_REQUEST_INTERVAL_MS) {
        _send_arp_request(next_hop_ip);
    }
}
optional<InternetDatagram> NetworkInterface::recv_frame(const EthernetFrame &frame) {
    // 目标 MAC 过滤
    if (frame.header().dst != _ethernet_address && frame.header().dst != ETHERNET_BROADCAST) {
        return {};
    }
    // IPv4
    if (frame.header().type == EthernetHeader::TYPE_IPv4) {
        InternetDatagram dgram;
        if (dgram.parse(frame.payload()) == ParseResult::NoError) {
            return dgram;
        }
        return {};
    }
    // ARP
    if (frame.header().type == EthernetHeader::TYPE_ARP) {
        ARPMessage arp;
        if (arp.parse(frame.payload()) != ParseResult::NoError) {
            return {};
        }
        const uint32_t sender_ip = arp.sender_ip_address;
        if (auto *entry = _find_arp_entry(sender_ip)) {
            entry->eth_addr = arp.sender_ethernet_address;
            entry->ttl_ms = ARP_CACHE_TTL_MS;
        } else {
            _arp_cache.push_back(ARPEntry{sender_ip, arp.sender_ethernet_address, ARP_CACHE_TTL_MS});
        }
        _flush_waiting(sender_ip);
        // 针对本机 IP 的请求 -> 回复
        if (arp.opcode == ARPMessage::OPCODE_REQUEST &&
            arp.target_ip_address == _ip_address.ipv4_numeric()) {
            ARPMessage reply;
            reply.opcode = ARPMessage::OPCODE_REPLY;
            reply.sender_ethernet_address = _ethernet_address;
            reply.sender_ip_address = _ip_address.ipv4_numeric();
            reply.target_ethernet_address = arp.sender_ethernet_address;
            reply.target_ip_address = arp.sender_ip_address;
            EthernetFrame reply_frame;
            reply_frame.header().src = _ethernet_address;
            reply_frame.header().dst = arp.sender_ethernet_address;
            reply_frame.header().type = EthernetHeader::TYPE_ARP;
            reply_frame.payload() = reply.serialize();
            _frames_out.push(reply_frame);
        }
        return {};
    }
    return {};
}
void NetworkInterface::tick(const size_t ms_since_last_tick) {
    // 1. ARP 缓存过期
    for (auto it = _arp_cache.begin(); it != _arp_cache.end();) {
        if (it->ttl_ms <= ms_since_last_tick) {
            it = _arp_cache.erase(it);
        } else {
            it->ttl_ms -= ms_since_last_tick;
            ++it;
        }
    }
    // 2. 请求记录过期
    for (auto it = _arp_request_records.begin(); it != _arp_request_records.end();) {
        if (it->age_ms >= ARP_REQUEST_INTERVAL_MS) {
            it = _arp_request_records.erase(it);
        } else {
            it->age_ms += ms_since_last_tick;
            ++it;
        }
    }
}
```

### 简易路由器
#### 实现路由类
在`router.hh`中的`router`类构建`RouteEntry`结构作为一条转发规则，组建`_routes`作为路由表：
```C
struct RouteEntry {
	uint32_t route_prefix;
	uint8_t prefix_length;
	std::optional<Address> next_hop;
	size_t interface_num;
};

std::vector<RouteEntry> _routes{};
```
并替换.cc文件中的DUMMYCODE：
```C
void Router::add_route(const uint32_t route_prefix,
                       const uint8_t prefix_length,
                       const optional<Address> next_hop,
                       const size_t interface_num) {
    cerr << "DEBUG: adding route " << Address::from_ipv4_numeric(route_prefix).ip() << "/" << int(prefix_length)
         << " => " << (next_hop.has_value() ? next_hop->ip() : "(direct)") << " on interface " << interface_num << "\n";
    _routes.push_back(RouteEntry{route_prefix, prefix_length, next_hop, interface_num});
}
void Router::route_one_datagram(InternetDatagram &dgram) {
    // TTL <= 1 直接丢弃
    if (dgram.header().ttl <= 1)
        return;
    const uint32_t dst = dgram.header().dst;
    // 最长前缀匹配
    const RouteEntry *best = nullptr;
    for (const auto &route : _routes) {
        // 高 prefix_length 位相同才匹配
        if (route.prefix_length == 0) {
            // /0 匹配所有，作为兜底
            if (best == nullptr || route.prefix_length > best->prefix_length)
                best = &route;
            continue;
        }
        const uint32_t mask = route.prefix_length >= 32
                                  ? 0xFFFFFFFFu
                                  : (0xFFFFFFFFu << (32 - route.prefix_length));
        if ((dst & mask) == (route.route_prefix & mask)) {
            if (best == nullptr || route.prefix_length > best->prefix_length)
                best = &route;
        }
    }
    // 没有匹配路由则丢弃
    if (best == nullptr)
        return;
    // TTL 减 1（后续序列化时会重算校验和）
    dgram.header().ttl--;
    // 决定下一跳：有 next_hop 用它，否则用目的地址（直连）
    const Address next_hop = best->next_hop.has_value() ? best->next_hop.value()
                                                        : Address::from_ipv4_numeric(dst);
    // 从对应接口发出
    _interfaces.at(best->interface_num).send_datagram(dgram, next_hop);
}
```
## <span id='result'> 实验结果与分析 </span>
- 测试ARP协议的运行截图
![[Pasted image 20261015202258.png|523]]
- 运行make check_lab1命令的测试结果展示
![[Pasted image 20261015205832.png]]
### 思考题

**根据你编写的程序运行效果，分别解答以下问题（实验报告中请去除此段）**

- 通过代码，请描述network interface是如何发送一个以太网帧的？

send_datagram
  ├─ ARP 缓存命中 ──────────────► _send_ipv4_datagram ──► _frames_out
  └─ 未命中
       ├─ 数据报存入 WaitingQueue
       └─ 需节流判断 ──► _send_arp_request ──► _frames_out (广播 ARP)

(稍后) recv_frame 收到 ARP 应答
       ├─ 学习 IP→MAC，写入 _arp_cache
       └─ _flush_waiting ──► _send_ipv4_datagram ×N ──► _frames_out

- 虽然在此次实验不需要考虑这种情况，但是当network interface发送一个ARP请求后如果没收到一个应答该怎么解决？请思考。

ARP 层：限次重发（指数退避）→ 达上限后放弃
        └─ 清理 WaitingQueue
- 请描述一下你为了记录路由表所建立的数据结构？为什么？
```C
struct RouteEntry {
	uint32_t route_prefix;
	uint8_t prefix_length;
	std::optional<Address> next_hop;
	size_t interface_num;
};

std::vector<RouteEntry> _routes{};
```
使用RouteEntry作为一条转发规则的规范，然后用RouteEntry的数组作为路由表
## 讨论、心得
在编写网络接口的实现代码时发现如果用原来的那几个成员和函数来实现，最终代码会很难debug写到最后我自己都没看懂，后来用辅助函数把一些功能拆分出来了。