# LAB1 REPORT

## LAB1-1

### 四路选择器原理图

![image-20240407161543513](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20240407161543513.png)

### 八路选择器代码解释

```verilog
module Mux8T1_1(
   input [7:0] I,
   input [2:0] S,
   output O
);

   //your verilog code
   wire [1:0]I_S;
   MUX4T1_1 MUX0(I[0],I[1],I[2],I[3],I_S[0],S[1:0]);
   MUX4T1_1 MUX1(I[4],I[5],I[6],I[7],I_S[1],S[1:0]);
   assign O = S[2] ? I_S[1] : I_S[0];

endmodule

```

在两个四路选择器的基础上用‘? :’运算符完成了一个二路选择器

### TestBench 设计

```verilog
initial begin
        //your test sample
        I=8'b10101010;
        S=3'b000;
        #5;
        S=3'b001;
        #5;
        S=3'b010;
        #5;
        S=3'b011;
        #5;
        S=3'b100;
        #5;
        S=3'b101;
        #5;
        S=3'b110;
        #5;
        S=3'b111;
        #5;
        I=8'b01010101;
        S=3'b000;
        #5;
        S=3'b001;
        #5;
        S=3'b010;
        #5;
        S=3'b011;
        #5;
        S=3'b100;
        #5;
        S=3'b101;
        #5;
        S=3'b110;
        #5;
        S=3'b111;
        #5;
    end
```

取两个固定的I，分别为01010101和10101010，然后遍历S的组合

### 其余实验步骤及截图

#### 上板

<img src="D:\Documentary\WeChat Files\wxid_***\FileStorage\Temp\65bf111b2af4f9a64f7f46e61625f26.jpg" alt="65bf111b2af4f9a64f7f46e61625f26" style="zoom:33%;" /><img src="D:\Documentary\WeChat Files\wxid_***\FileStorage\Temp\a337bd0edcbac42bd0134a0896f42d3.jpg" alt="a337bd0edcbac42bd0134a0896f42d3" style="zoom:33%;" /><img src="D:\Documentary\WeChat Files\wxid_***\FileStorage\Temp\2999f07cfbeda5a02bcfd9dfac0ddc5.jpg" alt="2999f07cfbeda5a02bcfd9dfac0ddc5" style="zoom:33%;" />

#### 仿真波形

![image-20240407162003596](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20240407162003596.png)

#### top.v

```verilog
module top(
  input [7+3:0] SW,
  output LD0
);

  // add connection from FPGA IO to the main
  Mux8T1_1 ldut(
        .I(SW[7:0]), // 8位输入
        .S(SW[10:8]), // 3位选择信号
        .O(LD0) // 输出
    );

endmodule
```

#### nexysa7.xdc

```verilog
## IO
set_property PACKAGE_PIN {J15} [get_ports {SW[0]}]
set_property IOSTANDARD {LVCMOS33} [get_ports {SW[0]}]
set_property PACKAGE_PIN {L16} [get_ports {SW[1]}]
set_property IOSTANDARD {LVCMOS33} [get_ports {SW[1]}]
set_property PACKAGE_PIN {M13} [get_ports {SW[2]}]
set_property IOSTANDARD {LVCMOS33} [get_ports {SW[2]}]
set_property PACKAGE_PIN {R15} [get_ports {SW[3]}]
set_property IOSTANDARD {LVCMOS33} [get_ports {SW[3]}]
set_property PACKAGE_PIN {R17} [get_ports {SW[4]}]
set_property IOSTANDARD {LVCMOS33} [get_ports {SW[4]}]
set_property PACKAGE_PIN {T18} [get_ports {SW[5]}]
set_property IOSTANDARD {LVCMOS33} [get_ports {SW[5]}]
set_property PACKAGE_PIN {U18} [get_ports {SW[6]}]
set_property IOSTANDARD {LVCMOS33} [get_ports {SW[6]}]
set_property PACKAGE_PIN {R13} [get_ports {SW[7]}]
set_property IOSTANDARD {LVCMOS33} [get_ports {SW[7]}]
set_property PACKAGE_PIN {T8} [get_ports {SW[8]}]
set_property IOSTANDARD {LVCMOS33} [get_ports {SW[8]}]
set_property PACKAGE_PIN {U8} [get_ports {SW[9]}]
set_property IOSTANDARD {LVCMOS33} [get_ports {SW[9]}]
set_property PACKAGE_PIN {R16} [get_ports {SW[10]}]
set_property IOSTANDARD {LVCMOS33} [get_ports {SW[10]}]
# add IO
set_property PACKAGE_PIN {H17} [get_ports {LD0}]
set_property IOSTANDARD {LVCMOS33} [get_ports {LD0}]
```

### 实验思考

#### 1.Mux2T1_1 是两个 AND，一个 OR 和一个 NOT 组成的简单结构，它是由哪种 decoder 和 AND-OR 结构组成的？

1-to-2¹-line decoder

2 * 2AND-OR

#### 2.Mux4T1_1 是如何组成的？

逻辑门：8个AND，1个OR和2个NOT组成

MUX：3个MUX2T1

- MUX2T1 #1：选择I0或I1，根据S0。
- MUX2T1 #2：选择I2或I3，根据S0。
- MUX2T1 #3：将第一级的两个输出作为输入，根据S1进行最终选择。

#### 3.Mux8T1_1 是如何组成的？

逻辑门：12个AND，9个OR，3个NOT

MUX：2个MUX4T1，1个MUX2T1

- MUX4T1 #1：选择I0、I1、I2或I3，根据S0和S1。
- MUX4T1 #2：选择I4、I5、I6或I7，根据S0和S1。
- MUX2T1：选择来自MUX4T1 #1或MUX4T1 #2的输出，根据S2。

#### 4.那么 Mux2^mT1_n 是如何构成的呢？

1-to-n Splitter

N-to-2^(n)-line decoder

2^(m) * 2 AND-OR

---

## LAB1-2

### 译码管设计

```verilog
`timescale 1ns / 1ps

module SegDecoder (
    input wire [3:0] data,
    input wire point,
    input wire LE,

    output wire a,
    output wire b,
    output wire c,
    output wire d,
    output wire e,
    output wire f,
    output wire g,
    output wire p
);

/* input your code here */
assign p = ~point;
assign g = LE|((~data[0]&~data[1]&data[2]&data[3])|(data[0]&data[1]&data[2]&~data[3])|(~data[1]&~data[2]&~data[3]));
assign f = LE|((data[0]&data[1]&~data[3])|(data[1]&~data[2]&~data[3])|(data[0]&~data[2]&~data[3])|(data[0]&~data[1]&data[2]&data[3]));
assign e = LE|((data[0]&~data[1]&~data[2])|(~data[1]&data[2]&~data[3])|(data[0]&~data[3]));
assign d = LE|((~data[0]&data[1]&~data[2]&data[3])|(data[0]&data[1]&data[2])|(~data[0]&~data[1]&data[2]&~data[3])|(data[0]&~data[1]&~data[2]&~data[3]));
assign c = LE|((data[1]&data[2]&data[3])|(~data[0]&data[1]&~data[2]&~data[3])|(~data[0]&data[2]&data[3]));
assign b = LE|((data[0]&data[1]&data[3])|(~data[0]&data[2]&data[3])|(~data[0]&data[1]&data[2])|(~data[1]&data[0]&data[2]&~data[3]));
assign a = LE|((data[0]&data[1]&~data[2]&data[3])|(data[0]&~data[1]&data[2]&data[3])|(~data[0]&~data[1]&data[2]&~data[3])|(data[0]&~data[1]&~data[2]&~data[3]));

endmodule //SegDecoder
```

>**图 lab1-2**　电路图原引自 ZJU 计算机系统Ⅰ课程网站（sys1-sp24），该站点已下线，图片未能收录。图为 a–g 各测试点的组合逻辑，题目要求对每个点写出表达式并用 Verilog 实现。

根据以上图像分别写出abcdefg的表达式，再用verilog写出来

### 复合多路选择器及语法分析比较

我选择了‘case’语法。

```verilog
module Mux4T1_32(
    input [31:0] I0,
    input [31:0] I1,
    input [31:0] I2,
    input [31:0] I3,
    input [1:0] S,
    output [31:0] O
);
    reg [31:0]out;
    //fill your code
    always @(*) begin
        case (S)
            2'b00: out <= I0;
            2'b01: out <= I1;
            2'b10: out <= I2;
            2'b11: out <= I3;
            default: out <= 32'b0; // 默认情况，可视具体需求而定
        endcase
    end
    assign O = out;

endmodule
```

#### 1. 多个一位多路选择器

- **优点**：逻辑清晰，直接映射到硬件实现，易于理解和验证。
- **缺点**：在硬件描述语言（HDL）中实现时，代码量大，可读性差，不易于扩展或维护。

#### 2. 与或形式

- **优点**：紧凑，能直观地表示逻辑功能，便于理论分析和优化。
- **缺点**：对于非专业人士可能难以理解，且在复杂逻辑中可读性差。

#### 3. `?:` 语法（条件运算符）

- **优点**：代码紧凑，可读性好，适用于简单逻辑判断。
- **缺点**：对于非常复杂的逻辑，嵌套使用可能导致代码难以阅读和理解。

#### 4. 索引语法（假设是在某些高级语言中使用数组或列表的索引）

- **优点**：代码非常简洁，特别是当选择信号直接映射到输入数组的索引时。
- **缺点**：可读性依赖于读者对语言的熟悉程度，且可能不易于直接映射到硬件实现。

#### 5. `if-else` 语法

- **优点**：逻辑表达清晰，易于理解和维护。
- **缺点**：可能导致代码冗长，特别是在处理多个条件分支时。

#### 6. `case` 语法

- **优点**：对于处理多个选择分支非常有效，代码结构清晰，易于扩展。
- **缺点**：在某些语言或环境中，可能不如索引语法直接。

#### 7. 与或式 vs 高级语法式

- **优点（与或式）**：直接表达硬件逻辑，对硬件设计师友好。
- **缺点（与或式）**：对于软件程序员或非硬件专业的人士来说，可能难以理解。
- **优点（高级语法）**：提高代码的可读性和可维护性，易于软件程序员理解。
- **缺点（高级语法）**：可能难以直接转换为硬件逻辑，不利于硬件实现的优化。

#### 8. 复合多路选择器实现译码器

- **优点**：可以有效利用现有的多路选择器构件来构建复杂的逻辑功能，如译码器，减少设计工作量。
- **缺点**：可能不如直接设计的译码器在性能或资源使用上优化。

### 综合实现数码管

![4850497ebc6faea90216bbc3bdb6155](D:\Documentary\WeChat Files\wxid_***\FileStorage\Temp\4850497ebc6faea90216bbc3bdb6155.jpg)

### 将testbench.v for语句展开为初始化序列

```verilog
initial begin
    LE=1'b1;
    point=1'b1;
    data=4'h9;
    #5;
    LE=1'b0;
    // 展开第一个for循环
    data=4'h0;
    #5;
    data=4'h1;
    #5;
    data=4'h2;
    #5;
    data=4'h3;
    #5;
    data=4'h4;
    #5;
    data=4'h5;
    #5;
    data=4'h6;
    #5;
    data=4'h7;
    #5;
    // 展开第二个for循环
    data=4'h8;
    #5;
    data=4'h9;
    #5;
    data=4'ha;
    #5;
    data=4'hb;
    #5;
    data=4'hc;
    #5;
    data=4'hd;
    #5;
    data=4'he;
    #5;
    data=4'hf;
    #5;
    point=1'b0;
    $finish;
end
```

**第一个`for`循环**：

- 用于将`data`变量通过8次迭代分别设置为0到7的值（使用`i[3:0]`提取`i`的低4位作为`data`的值）。每次赋值后有一个5个时间单位的延迟。

**第二个`for`循环**：

- 类似于第一个循环，但这次是将`data`变量设置为8到15的值，每次迭代同样有5个时间单位的延迟。

### 对于各种多路选择器的写法进行比较，请写出你最喜欢的多路选择器语法，并给出理由

我最喜欢case。

- **清晰的结构**：`case`语法允许清楚地列出所有可能的选择情况和对应的输出，这使得理解和分析MUX的行为变得直观。
- **易于维护**：当需要添加更多输入或修改现有逻辑时，`case`语法的结构化特性允许开发者快速定位并更新特定的分支，而不必重新理解或重构整个逻辑。
- **可读性**：与其他方法相比，`case`语法提供了更高的可读性，特别是对于那些具有多个输入信号的复杂多路选择器。它几乎像自然语言一样描述了多路选择器的功能，即“在这种情况下做这个，否则做那个”。
- **可扩展性**：如果未来需要扩展多路选择器以处理更多的输入，使用`case`语法的代码可以很容易地添加新的分支，而无需对现有逻辑进行大量修改或重写。