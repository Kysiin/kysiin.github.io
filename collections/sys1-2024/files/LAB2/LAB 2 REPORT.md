# LAB 2 REPORT

## 1.实验步骤

* Testbench

```verilog
for(i=0;i<20;i=i+1)begin
            a=$random();
            b=$random();
            rand_val=$random();
            do_sub=rand_val[0];
            #5;
end
```

>由于do_sub只有一位，且random()函数产生32位的结果，需定义一个中间变量来截取random()的一位赋值给do_sub。

循环20次，每次随机赋值a,b,do_sub

![image-20240420095319813](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20240420095319813.png)

* 全加减法器

```verilog
// 异或操作对b进行按位取反，当do_sub=1时相当于减法
wire [LENGTH-1:0] b_xor;

// 对b进行按位异或操作，如果do_sub=1，则每位与1异或（即取反），如果do_sub=0，则与0异或，保持不变
assign b_xor = b ^ {LENGTH{do_sub}};

// 使用Adders模块进行加法操作
// 当do_sub=1时，b_xor为b的补码，同时c_in设置为1（相当于加上1），实现减法
// 当do_sub=0时，直接执行a和b的加法
Adders #(.LENGTH(LENGTH)) adder_instance (
    .a(a),
    .b(b_xor),
    .c_in(do_sub), // 当执行减法时，需要在最低位加上1，这里通过do_sub控制
    .s(s),
    .c_out(c)
);
```

<img src="D:\Documentary\WeChat Files\wxid_***\FileStorage\Temp\655cb452b940d53de4145b72200ea7d.jpg" alt="655cb452b940d53de4145b72200ea7d" style="zoom: 25%;" /><img src="D:\Documentary\WeChat Files\wxid_***\FileStorage\Temp\bf38aec6a0ff8fcdae6d21d158d7ce6.jpg" alt="bf38aec6a0ff8fcdae6d21d158d7ce6" style="zoom:25%;" /><img src="D:\Documentary\WeChat Files\wxid_***\FileStorage\Temp\ecb02fb50950acc51d20868099f0b11.jpg" alt="ecb02fb50950acc51d20868099f0b11" style="zoom:25%;" />

## 2.思考

### 改变adder格式

对于以下三种格式，

```verilog
reg [0:63] adder [0:7];
reg [0:63] adder [7:0];
reg [63:0] adder [0:7];
```

adder都会被初始化为，从`adder[0]`到`adder[7]`分别为`0123456789abcdef`到`afced27829378236`,[0:63]/[63:0]或者[0:7]/[7:0]并不改变赋值的任何顺序

而对于

```verilog
reg [127:0] adder [0:7];
```

adder会从`adder[0]`到`adder[7]`被依次赋值为`00000000000000000123456789abcdef`到`0000000000000000afced27829378236`，即在每个十六进制数前补充十六个`0`来填充宽度

因此，`$readmemh`在初始化时只受数组的宽度变化影响，高低位顺序不影响赋值顺序。

### 对于超前进位加法器，行波进位加法器存在什么缺点？

1. **速度较慢**：行波进位加法器的一个主要缺点是它的加法速度相对较慢。在RCA中，每个比特位置的进位信号需要等待前一个比特位置的进位信号计算完成后才能进行，因此进位信号需要逐个"行波"式传递。这导致了较长的延迟时间，特别是在进行多位数加法时。
2. **延迟时间与位数成正比**：由于进位信号需要逐级传递，RCA的总延迟时间大约是与加数位数成正比的。例如，一个32位的行波进位加法器可能需要经过32个进位传递阶段才能得到最终结果，这在高速计算需求下是不可接受的。
3. **扩展性较差**：随着加数的位数增加，行波进位加法器的延迟急剧增加，这限制了其在高位宽计算中的应用。对于大规模集成电路设计，这种延迟的增加会严重影响整体性能。

### 如何表示运算溢出？请给出溢出表示的布尔代数

```verilog
OVERFLOW = a_invert & b_invert & (~sum[31]) |(~a_invert) & (~b_invert) & sum[31]
```

