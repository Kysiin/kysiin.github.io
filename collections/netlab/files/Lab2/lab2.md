









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
    报告日期:  2026年 10月 9日
  </font>
</center>



<div STYLE="page-break-after: always;"></div>



# Lab2  Webget 与字节流（ByteStream）


## 实验目的

- 学习掌握Linux虚拟机的用法
- 学习掌握网页的抓取方法
- 学习掌握ByteStream的相关知识

## 实验内容

- 安装配置Linux虚拟机并在其上完成本次实验。

- 使用应用层程序访问网页。

- 编写小程序webget，通过网络获取web页面。

- 实现字节流ByteStream：

  - 字节流可以从写入端写入，并以相同的顺序，从读取端读取；

  - 字节流是有限的，写者可以终止写入。而读者可以在读取到字节流末尾时，产生EOF标志，不再读取；

  - 写入的字节流可能会很长，必须考虑到字节流大于缓冲区大小的情况。

## 主要仪器设备

- 联网的PC机
- Linux虚拟机

## 操作方法与实验步骤

### 使用Telnet获取网页
![[Pasted image 20261008233824.png|312]]
### Webget
配置好`ssh`后`git clone`

![[Pasted image 20261009001907.png|439]]

在`CMake`时报错`CMake`版本过高，采取添加`-DCMAKE_POLICY_VERSION_MINIMUM=3.5`参数方法让`CMake`以兼容模式处理

>后把CMakeList中的`cmake_minimum_required`修改为`version 3.5`

![[Pasted image 20261009001642.png|396]]
![[Pasted image 20261009001617.png|398]]

`make`编译，发现报错：

![[Pasted image 20261009003210.png|513]]

是因为新版GCC不再隐式包含`<cstdint>`导致的
于是用VSC为`/home/cs144/zju-comnet-labs-2026/libsponge/util/buffer.hh`在开头加上了`#include <cstdint>`后重新编译成功

![[Pasted image 20261009005051.png|402]]

完成`get_URL`函数：

```cpp
void get_URL(const string &host, const string &path) {
	//Connection
	Address addr(host, "http");
	TCPSocket sock;
	sock.connect(addr);

	//Construct Request
	std::string reques
	request += "GET " + path + " HTTP/1.1\r\n";
	request += "Host: " + host + "\r\n";
	request += "Connection: close\r\n";
	request += "\r\n";

	//Send Request
	sock.write(request);

	//Read
	std::string response;
	while(!sock.eof()){
		sock.read(response);
		std::cout << response;
		response.clear();
	}

	//Close Socket
	sock.close();

	cerr << "Function called: get_URL(" << host << ", " << path << ").\n";
    cerr << "Warning: get_URL() has not been implemented yet.\n";
}
```

编译后运行：

![[Pasted image 20261009090625.png|500]]

运行测试通过：

![[Pasted image 20261009090645.png|500]]

### 可靠的字节流
根据`byte_stream.cc`的需求构建`byte_stream.hh`的`private`类：

```cpp
std::string _buffer{};      //Buffer
size_t _capacity = 0;       //Capacity
bool _input_ended = false;  //is input ended
size_t _bytes_written = 0;  // bytes that have been written
size_t _bytes_read = 0;     //bytes that have been read
```

然后重新构建`byte_stream.cc`：

```cpp
#include "byte_stream.hh"
using namespace std;

ByteStream::ByteStream(const size_t capacity) : _capacity(capacity) {}

size_t ByteStream::write(const string &data) {
    size_t n = min(data.size(), remaining_capacity());
    _buffer.append(data, 0, n);
    _bytes_written += n;
    return n;
}

//! \param[in] len bytes will be copied from the output side of the buffer
string ByteStream::peek_output(const size_t len) const {
    return _buffer.substr(0, len);
}

//! \param[in] len bytes will be removed from the output side of the buffer
void ByteStream::pop_output(const size_t len) {
    size_t n = min(len, _buffer.size());
    _buffer.erase(0, n);
    _bytes_read += n;
 }

//! Read (i.e., copy and then pop) the next "len" bytes of the stream
//! \param[in] len bytes will be popped and returned
//! \returns a string
std::string ByteStream::read(const size_t len) {
    string result = peek_output(len);
    pop_output(result.size());
    return result;
}

void ByteStream::end_input() { _input_ended = true;}

bool ByteStream::input_ended() const { return _input_ended; }

size_t ByteStream::buffer_size() const { return _buffer.size(); }

bool ByteStream::buffer_empty() const { return _buffer.empty(); }

bool ByteStream::eof() const { return _input_ended && _buffer.empty(); }

size_t ByteStream::bytes_written() const { return _bytes_written; }

size_t ByteStream::bytes_read() const { return _bytes_read; }

size_t ByteStream::remaining_capacity() const {
    return _capacity - _buffer.size();
}
```

编译运行测试成功

![[Pasted image 20261009093713.png|454]]
## <span id='result'> 实验结果与分析 </span>

- 抓取网页（通过浏览器和telnet）的运行结果
浏览器访问
![[Pasted image 20261008232832.png|441]]
telnet访问：
![[Pasted image 20261008233824.png|312]]
- 使用webget抓取网页运行结果
![[Pasted image 20261009090625.png|519]]
- 运行make check_webget的测试结果展示
![[Pasted image 20261009090645.png|499]]
- 运行make check_lab0测试结果。
![[Pasted image 20261009093713.png|452]]
### 思考题
- 完成webget程序编写后的测试结果和Fetch a Web page步骤的运行结果一致吗？如果不一致的话你认为问题出在哪里？请描述一下所写的webget程序抓取网页的流程。

一致
Webget抓取网页流程：
1. 解析主机名，建立 TCP 连接
2. 构造 HTTP/1.1 请求
3. 发送请求
4. 循环读取直到EOF
5. 关闭套接字

- 请描述ByteStream是如何实现流控制的？

用容量上限`_capacity`约束 writer，用已写`_bytes_written`/已读`_bytes_read`计数让 reader 知道何时能读、writer 知道何时能写

- 当遇到超出capacity范围的数据流的时候，该如何进行处理？如果不限制流的长度会怎么样？

缓冲区已满时，`remaining_capacity() == 0`，`n = 0`，一个字节也不写。只写 `n` 个字节，剩下的 `data.size() - n` 个字节被抛弃

如果不限制流的长度，内存上限将持续增长，writer永远能写，reader永远落后，无法通过 `remaining_capacity()` 判断该不该继续写

## 讨论、心得

主要是make方面遇到的一些版本问题，通过搜索和AI解决
在`get_URL`函数编写中遗漏了一些空格导致测试不通过