# LAB0实验报告

## LAB0-1

### 1.反相器的电压传输特性

#### 1.截图

![37be0f8685d8c5e1beb1684ecefa511](D:\Documentary\WeChat Files\wxid_***\FileStorage\Temp\37be0f8685d8c5e1beb1684ecefa511.png)

#### 2.输入输出关系

当Vin大于临界值(约0.7V)，Vout为0V

当Vin小于临界值(约0.7V)，Vout为2V

#### 3.给 Vin 接入一个正弦变化的电压

![Capture_20240317_200331](D:\Huawei Share\Huawei Share\Capture_20240317_200331.jpg)

当Vin大于临界值时Vout为0V，当Vin小于临界值时Vout为2V

#### 4.逻辑 0 和逻辑 1 的阈值

逻辑0的阈值应设为1.0-2.0V，逻辑1的阈值应设为0-0.6V

### 2.Logisim 电路仿真

#### 1.截图

![64e3936a8b5249d8d360d94009174fd](D:\Documentary\WeChat Files\wxid_***\FileStorage\Temp\64e3936a8b5249d8d360d94009174fd.png)

#### 2.真值表

|      |      |      |        |
| ---- | ---- | ---- | ------ |
| I0   | I1   | I2   | OUTPUT |
| 0    | 0    | 0    | 0      |
| 0    | 0    | 1    | 1      |
| 0    | 1    | 0    | 1      |
| 0    | 1    | 1    | 0      |
| 1    | 0    | 0    | 1      |
| 1    | 0    | 1    | 0      |
| 1    | 1    | 0    | 0      |
| 1    | 1    | 1    | 1      |

## LAB0-2

### 1.Verilog 练习

#### 1.化简卡诺图

![5b4ab3277c821b45f774bc4977a4d43](D:\Documentary\WeChat Files\wxid_***\FileStorage\Temp\5b4ab3277c821b45f774bc4977a4d43.png)

>有处笔误，**最后的表达式中$\bar AC应为AC$**

#### 2.上板

![3348c227a6d7f0873c44af334279f77](D:\Documentary\WeChat Files\wxid_***\FileStorage\Temp\3348c227a6d7f0873c44af334279f77.jpg)

![64b65d5afa713167963a6809612343a](D:\Documentary\WeChat Files\wxid_***\FileStorage\Temp\64b65d5afa713167963a6809612343a.jpg)

### 2.仿真练习

#### 1.verilator仿真

从I0到I3为0000，每#5加1，直到1111

![image-20240317202802765](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20240317202802765.png)

![77223fcb05e5c031d3fb75056a47a5e](D:\Documentary\WeChat Files\wxid_***\FileStorage\Temp\77223fcb05e5c031d3fb75056a47a5e.png)

#### 2.vivado仿真

![image-20240317203103024](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20240317203103024.png)

