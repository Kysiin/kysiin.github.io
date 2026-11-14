# Lab1 Set-UID

## 任务1

#### `printenv`

![image-20260924012512044](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260924012512044.png)

## 任务2

#### 1. 编译`printenv.c`

![image-20260924012927798](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260924012927798.png)

#### 2. 注释后得到

![image-20260924013241468](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260924013241468.png)

#### 3. diff比较结果

![image-20260924013421712](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260924013421712.png)

两个文件完全一致。

fork()系统复制的子进程与父进程的地址空间一模一样，加上环境变量没变，因此结果不变。

## 任务3

#### 1.

![image-20260924013832477](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260924013832477.png)

没有输出

#### 2. 修改为execve

![image-20260924013954189](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260924013954189.png)

输出环境变量

#### 3. 新程序如何获得其环境变量

通过execve()的第三个参数接收环境变量，给到/usr/bin/env程序，打印出来

## 任务4

![image-20260924014519950](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260924014519950.png)

## 任务5

#### 1.

![image-20260924015644663](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260924015644663.png)

#### 2.

![image-20260924014819163](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260924014819163.png)

#### 3. 设置环境变量

`export KYSIIN_PATH="This is Kysiin"`

![image-20260924020302279](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260924020302279.png)

![image-20260924020338577](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260924020338577.png)

`export LD_LIBRARY_PATH=/home`

![image-20260924020513245](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260924020513245.png)

`export PATH=/home`

![image-20260924020647772](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260924020647772.png)

## 任务6

编写一个fakels.c如下：

```c
#include <stdio.h>
#include <unistd.h>
int main() {
    printf("=== 恶意代码被执行了！ ===\n");
    printf("当前进程的 EUID = %d\n", geteuid());
    return 0;
}
```

编译为myls，放在/home/seed文件夹下

![image-20260924022531125](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260924022531125.png)

myls程序是root运行的，但恶意程序不是

## 任务7

#### 1.

![image-20260924023133933](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260924023133933.png)

#### 2.

##### 普通程序/普通用户

![image-20260924023207579](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260924023207579.png)

##### Set-UID root程序/普通用户

![image-20260924024414982](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260924024414982.png)

##### Set-UID root程序/root设置LD_PRELOAD/普通用户

![image-20260924025943048](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260924025943048.png)

##### Set-UID user1程序/seed用户

![image-20260924030211922](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260924030211922.png)

发现LD_PRELOAD只在普通程序中生效

#### 3. 设计实验

写一个程序，打印出它**当前实际拥有的所有环境变量**，然后分别在普通用户和 Set-UID 场景下运行，对比 `LD_PRELOAD` 是否还存在。

## 任务8

#### 1.

![image-20260924030645430](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260924030645430.png)

可以破坏系统完整性

程序把用户输入的文件名 `argv[1]` 直接拼接到了 `/bin/cat` 后面，然后交给 `system()` 执行。因为 Bob 可以控制 `argv[1]`，他就可以注入额外的 Shell 命令。

如：

```
./catall "/etc/passwd; rm -rf /home/seed/Desktop/lab1/Labsetup/file"
```

![image-20260924031118748](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260924031118748.png)

删除了file文件

#### 2.

![image-20260924031314010](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260924031314010.png)

攻击无效了，因为`execve` 直接执行 `/bin/cat`，不经过 Shell。

## 任务9

#### 配置文件

![image-20260924031836280](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260924031836280.png)

#### 运行

![image-20260924031900410](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260924031900410.png)

#### 攻击

```
echo "hacked by Kysiin" >&3
```

![image-20260924032018204](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260924032018204.png)