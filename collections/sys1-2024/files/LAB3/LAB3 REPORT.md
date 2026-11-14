# LAB3 REPORT

## 3-1

### 使用 enum 语法 FSM 设计

```verilog
typedef enum logic [1:0] {S0,S1,S2,S3} fsm_state;

fsm_state statep;
always@(posedge clk or negedge rstn)begin
    if(~rstn)begin
        statep <= S0;
    end else begin
        case(state)
            S0:if(a) statep<=S1; else statep<=S0; //00 ,若a则01
            S1:if(a) statep<=S2; else if(b) statep<=S0;  //01，若a则10，若b则00
            S2:if(a) statep<=S3; else if(b) statep<=S0;  //10，若a则11，若b则00
            S3:if(a) statep<=S3; else statep<=S3;		 //保持11
        endcase
    end
end

assign state = statep;
```

### 综合实现有限状态机

<img src="D:\Documentary\WeChat Files\wxid_***\FileStorage\Temp\c2ced1a8a77ad6117ec740da6ac600b.jpg" alt="c2ced1a8a77ad6117ec740da6ac600b" style="zoom: 25%;" /><img src="D:\Documentary\WeChat Files\wxid_***\FileStorage\Temp\19200180cae7c42991fbb3ba3ef8dbf.jpg" alt="19200180cae7c42991fbb3ba3ef8dbf" style="zoom: 25%;" /><img src="D:\Documentary\WeChat Files\wxid_***\FileStorage\Temp\64d994c8614366bf1aa16fd538833f9.jpg" alt="64d994c8614366bf1aa16fd538833f9" style="zoom: 25%;" />

### 思考比较`enum + case`的编程范式和数组查表的编程范式之间的优劣

### 1. `enum+case` 写法

#### 优点

1. **代码可读性高**：
   - 使用 `enum` 定义状态，代码直观，容易理解和维护。
   - `case` 语句清晰地展示了每个状态的转换逻辑，便于调试和分析。
2. **调试方便**：
   - 由于状态是枚举类型，仿真和调试时可以直接看到具体的状态名称，而不是抽象的数值。
3. **不易出错**：
   - 每个状态的转换逻辑都显式地列出，减少了隐含错误的可能性。

#### 缺点

1. **代码冗长：**
   - 当状态和转换规则较多时，`case` 语句会显得冗长，增加代码的复杂度。
2. **状态逻辑修改困难：**
   - 添加或修改状态时需要手动修改 `case` 语句，容易引入新的错误。

### 2. 查表法

#### 优点

1. **代码简洁**：
   - 利用查表的方法，只需要初始化表格和一次状态查表操作，代码简洁明了。
2. **灵活性高**：
   - 状态转换逻辑存储在外部文件（如 hex 文件）中，修改状态机逻辑时只需修改该文件，不需要修改 Verilog 代码。

#### 缺点

1. **可读性差**：
   - 状态转换逻辑隐含在查表操作中，代码本身不直观，理解和调试困难。
2. 硬件实现复杂：
   - 如果有限状态机很庞大，LUT 的数目会很多，电路会比较复杂
3. **外部文件依赖**：
   - 需要依赖外部 hex 文件，增加了项目管理和文件同步的复杂度。

### 绘制一个有限状态机的状态图和状态转移表，如果输入的 01 字符串中 1 的个数大于 3 个，则 FSM 输出 1 表示接受，反之输出 0 表示拒绝

<img src="D:\Documentary\WeChat Files\wxid_***\FileStorage\Temp\bee9ad4aaa77fc6f6c997c28138d473.jpg" alt="bee9ad4aaa77fc6f6c997c28138d473" style="zoom: 25%;" />

### bonus

`state[1:0] <= state[0:1];` 意味着状态的第一个比特位（`state[1]`）由原来的第二个比特位（`state[0]`）决定，第二个比特位（`state[0]`）由原来的第一个比特位（`state[1]`）决定。时序逻辑不清晰，没有明确的状态转移逻辑，容易造成状态的不可预测性。

电路不稳时，状态机可能会进入不可预测的状态，导致整个电路的行为变得不确定，无法保证预期功能的实现。

## 3-2

### 仿真

![7ed5d048b71f11327149439428b248e](D:\Documentary\WeChat Files\wxid_***\FileStorage\Temp\7ed5d048b71f11327149439428b248e.png)

<img src="D:\Documentary\WeChat Files\wxid_***\FileStorage\Temp\d719dbd4007087a26cf9ea3b8d94a83.jpg" alt="d719dbd4007087a26cf9ea3b8d94a83" style="zoom:25%;" /><img src="D:\Documentary\WeChat Files\wxid_***\FileStorage\Temp\d70edf3e639067e58a33961969cb4e7.jpg" alt="d70edf3e639067e58a33961969cb4e7" style="zoom:25%;" /><img src="D:\Documentary\WeChat Files\wxid_***\FileStorage\Temp\86a80828815346d26d6ef3da969efa6.jpg" alt="86a80828815346d26d6ef3da969efa6" style="zoom:25%;" />

### 简述如何使用 Cnt2num 实现 1234 的 BCD 码计数器，并思考 Cnt2num 预留 co、low_co、high_rst 引脚的意义

1. 低位计算

```verilog
Cnt #(LOW_BASE, LOW_INIT) low_counter (
        .en(en),
        .clk(clk),
        .rstn(rstn),
        .low_co(low_co),
    	.high_rst(rsth), //rsth是high_rst的中间寄存器
        .co(low),
        .cnt(low_cnt)
    );
```

2. 高位计算

```verilog
Cnt #(HIGH_BASE, HIGH_INIT) high_counter (
        .en(en),
        .clk(clk),
        .rstn(rstn),
    	.low_co(low), // 低位计算获得的进位
        .high_rst(rsth),
        .co(high_co),
        .cnt(high_cnt)
    );
```

3. 赋值

```verilog
 // 计数器满23时归零
    assign rsth = (high_cnt == HIGH_CO[3:0] && low_cnt == LOW_CO[3:0] && low_co);

// 为输出赋值
	assign cnt = {high_cnt,low_cnt}; // 高低位计算的结果结合
    assign co = high_co||rsth; // 整个计数器的进位
```

4.预留 co、low_co、high_rst 引脚的意义

用于进位的计算，low_co可以为之后的正负和加减做准备，high_rst可以用于归零，co可以表示溢出

## 3-3

### 仿真

![image-20240512135336077](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20240512135336077.png)

<img src="D:\Documentary\WeChat Files\wxid_***\FileStorage\Temp\ace060acd61bbafdab92c2153c15755.jpg" alt="ace060acd61bbafdab92c2153c15755" style="zoom:25%;" /><img src="D:\Documentary\WeChat Files\wxid_***\FileStorage\Temp\09893fb1b46bd193be1cfafebae346b.jpg" alt="09893fb1b46bd193be1cfafebae346b" style="zoom:25%;" /><img src="D:\Documentary\WeChat Files\wxid_***\FileStorage\Temp\5ac0b8ddd6a727e0dd23b78b165db2a.jpg" alt="5ac0b8ddd6a727e0dd23b78b165db2a" style="zoom:25%;" /><img src="D:\Documentary\WeChat Files\wxid_***\FileStorage\Temp\f8239f57a7f2bc3dd3cce11571c2e71.jpg" alt="f8239f57a7f2bc3dd3cce11571c2e71" style="zoom:25%;" />

### start-finish

testbench：

```verilog
for (i = 0; i < 16; i++) begin
            // 生成随机的乘数和被乘数
            wait (!start);  // 确保上一轮运算已结束
            @(posedge clk);  // 在时钟上升沿触发

            // 随机生成乘数和被乘数
            multiplicand = $random;
            multiplier = $random;
            start = 1;  // 发送start信号

            @(posedge clk);
            start = 0;  // 保证start信号持续一个周期

            // 等待乘法器完成运算
            wait (finish == 1);

            // 检查finish信号，确认可以进行下一次运算
        end
```

乘数和被乘数生成后发出start信号，multiplier才会接收数据，接着等待一个时钟周期把start信号置零，并等待multiplier发送finish信号，则接受multiplier发送来的结果，并与交予judge检查

### **32bit 无符号整数除法器**

```pseudocode
function divide(dividend, divisor)
    if divisor == 0
        error "Divide by zero"
    end if

    quotient = 0
    remainder = 0
    current_bit = 31

    for i = current_bit down to 0
        remainder = (remainder << 1) | (dividend >> current_bit)
        dividend = dividend << 1

        if remainder >= divisor
            remainder = remainder - divisor
            quotient = quotient | (1 << current_bit)
        end if
    end for

    return quotient, remainder
end function

```

1. **初始化**：
   - 设定被除数 `dividend` 和除数 `divisor`。
   - 结果寄存器 `quotient` 初始化为0。
   - 当前位寄存器 `current_bit` 设置为31（最高位）。
   - 余数寄存器 `remainder` 初始化为0。
2. **主循环**：
   - 在每次循环中，将 `dividend` 左移一位并加到 `remainder` 中。
   - 检查 `remainder` 是否大于等于 `divisor`。
   - 如果 `remainder` 大于等于 `divisor`，则从 `remainder` 中减去 `divisor` 并将 `quotient` 的当前位设为1。
   - 将 `current_bit` 减1。
   - 重复上述步骤直到所有位都处理完毕。
3. **结果输出**：
   - 经过主循环，`quotient` 中存储的就是最终的商，`remainder` 中存储的就是最终的余数。
