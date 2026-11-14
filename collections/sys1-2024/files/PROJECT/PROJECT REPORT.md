# PROJECT REPORT

## REG FILE

定义寄存器

>```verilog
>  integer i;
>  data_t register [0:31]; // x1 - x31, x0 keeps zero
>```

读入数据

>```verilog
> assign read_data_1 = (read_addr_1 == 0) ? 64'b0 : register[read_addr_1];
> assign read_data_2 = (read_addr_2 == 0) ? 64'b0 : register[read_addr_2];
>```

置零

>```verilog
>  for(i=0;i<32;i=i+1)begin
>    register[i] <= 0;
>  end
>```

若写使能且有地址则写入

>```verilog
>else if((write_addr!=0)&&we)begin
>   register[write_addr] <= write_data;
>end
>```

## ALU

```verilog
  data_t result;
  reg [4:0] addr = b[4:0];
  wire [31:0] addw_result = a[31:0] + b[31:0];
  wire [31:0] subw_result = a[31:0] - b[31:0];
  wire [31:0] sllw_result = a[31:0] << addr;

  always @(*) begin
    case (alu_op)
      ALU_ADD:    result = a + b;
      ALU_SUB:    result = a - b;
      ALU_AND:    result = a & b;
      ALU_OR:     result = a | b;
      ALU_XOR:    result = a ^ b;
      ALU_SLL:    result = a << b[5:0];
      ALU_SRL:    result = a >> b[5:0];
      ALU_SRA:    result = $signed(a) >>> $signed(b[5:0]);
      ALU_SLT:    result = ($signed(a) < $signed(b)) ? 64'b1 : 64'b0;
      ALU_SLTU:   result = (a <  b) ? 64'b1 : 64'b0;
      ALU_ADDW:   result = {{32{addw_result[31]}}, addw_result};
      ALU_SUBW:   result = {{32{subw_result[31]}}, subw_result};
      ALU_SLLW:   result = {{32{sllw_result[31]}}, sllw_result[31:0]};
      ALU_SRLW:   result = {{32{1'b0}}, a[31:0] >> addr};
      ALU_SRAW:   result = {{32{a[31]}}, $signed(a[31:0]) >>> addr};
      ALU_DEFAULT:result = 64'b0;
    endcase
  end
```



一开始`SLL`和`SRL`用的是b[4:0]，但发现有大于31的情况，于是改为[5:0]

符号位扩展容易出错，改来改去变成了先把32位的结果算出来，也就是`sllw_result`和`addw_result subw_result`，然后再扩展

## CMP

```verilog
CMP_NO:   result = 1'b0;
CMP_EQ:   result = (a == b);
CMP_NE:   result = (a != b);
CMP_LT:   result = ($signed(a) < $signed(b));
CMP_GE:   result = ($signed(a) >= $signed(b));
CMP_LTU:  result = (a < b);
CMP_GEU:  result = (a >= b);
default:  result = 1'b0;
```

## CONTROLLER

取inst中的低7位作为opcode，12到14位作为funct3，最后25到31位作为funct7。

通过opcode和funct判断指令类型，并分门别类给写使能、读使能、立即数类型等(即controller的输出)赋值。

示例：

```verilog
IMM_OPCODE: begin
                we_reg = 1;
                immgen_op = I_IMM;
                alu_asel = ASEL_REG;
                alu_bsel = BSEL_IMM;
                wb_sel = WB_SEL_ALU;
                case (funct3)
                    ADD_FUNCT3: alu_op = ALU_ADD;
                    SLL_FUNCT3: alu_op = ALU_SLL;
                    SLT_FUNCT3: alu_op = ALU_SLT;
                    SLTU_FUNCT3: alu_op = ALU_SLTU;
                    XOR_FUNCT3: alu_op = ALU_XOR;
                    SRL_FUNCT3: alu_op = (funct7 == 7'b0000000) ? ALU_SRL : ALU_SRA;
                    OR_FUNCT3: alu_op = ALU_OR;
                    AND_FUNCT3: alu_op = ALU_AND;
                    default: alu_op = ALU_DEFAULT;
                endcase
```

在`IMMW`和`REGW`中有些opcode是重复的，用funct3判断，funct3重复的用funct7判断。

## CORE

将REG ALU CONTROLLER CMP几个模块连接起来

`PC`

```verilog
	always @(posedge clk) begin
        if (rst) begin
            pc <= 64'b0;
        end else begin
            pc <= next_pc;
        end
    end

    always @(*) begin
        if (is_j) begin
            next_pc = (alu_asel == ASEL_PC) ? (pc + imm) : alu_res;
        end else if (is_b && cmp_res) begin
            next_pc = pc + imm;
        end else begin
            next_pc = pc + 4;
        end
    end
```

`写回`

```verilog
    assign wb_val = (wb_sel == WB_SEL_MEM) ? data_trun :
                    (wb_sel == WB_SEL_PC)  ? (pc + 4) :
                    (wb_sel == WB_SEL_ALU) ? alu_res :
                    imm;
```

`立即数生成`

```verilog
    always @(*) begin
        case (immgen_op)
            IMM0: imm = 64'b0;
            I_IMM: imm = {{52{inst[31]}}, inst[31:20]};
            S_IMM: imm = {{52{inst[31]}}, inst[31:25], inst[11:7]};
            B_IMM: imm = {{51{inst[31]}}, inst[31], inst[7], inst[30:25], inst[11:8], 1'b0};
            U_IMM: imm = {{32{inst[31]}}, inst[31:12], 12'b0};
            UJ_IMM: imm = {{43{inst[31]}}, inst[31], inst[19:12], inst[20], inst[30:21], 1'b0};
            default: imm = 64'b0;
        endcase
    end
```

`ALU输入赋值`

```verilog
    always @(*) begin
        case (alu_asel)
            ASEL0: alu_op1 = 0;
            ASEL_REG: alu_op1 = read_data_1;
            ASEL_PC: alu_op1 = pc;
            default: alu_op1 = 0;
        endcase
    end

    always @(*) begin
        case (alu_bsel)
            BSEL0: alu_op2 = 0;
            BSEL_REG: alu_op2 = read_data_2;
            BSEL_IMM: alu_op2 = imm;
            default: alu_op2 = 0;
        endcase
    end
```

`数据打包`

```verilog
    DataPackage dp (
        .data_in(read_data_2),
        .addr(alu_res[2:0]),
        .data_out(data_packaged)
    );
    DataMaskGeneration dmg (
        .mem_op(mem_op),
        .addr(alu_res[2:0]),
        .mask(mask)
    );
    DataTruncation dt (
        .data_in(data_from_mem),
        .mem_op(mem_op),
        .addr(alu_res[2:0]),
        .data_out(data_trun)
    );

    assign dmem_ift.r_request_bits.raddr = alu_res;
    assign dmem_ift.r_request_valid =re_mem ;
    assign data_from_mem = dmem_ift.r_reply_bits.rdata;
    assign dmem_ift.w_request_bits.waddr = alu_res;
    assign dmem_ift.w_request_bits.wdata = data_packaged;
    assign dmem_ift.w_request_bits.wmask = mask;
    assign dmem_ift.w_request_valid = we_mem;


    module DataMaskGeneration (
    input [2:0] mem_op,
    input [2:0] addr,
    output logic [7:0] mask
);
    import CorePack::*;
    always_comb begin
        case (mem_op)
            MEM_NO: mask = 8'b00000000<<(addr);
            MEM_B: mask = 8'b00000001<<(addr);
            MEM_H: mask = 8'b00000011<<(addr);
            MEM_W: mask = 8'b00001111<<(addr);
            MEM_D: mask = 8'b11111111<<(addr);
            MEM_UB: mask = 8'b00000001<<(addr);
            MEM_UH: mask = 8'b00000011<<(addr);
            MEM_UW: mask = 8'b00001111<<(addr);
            default: mask = 8'b00000000<<(addr);
        endcase
    end
endmodule

module DataPackage (
    input [63:0] data_in,
    input [2:0] addr,
    output logic [63:0] data_out
);
    import CorePack::*;
    assign data_out = data_in << (8*addr);
endmodule

module DataTruncation (
    input [63:0] data_in,
    input [2:0] mem_op,
    input [2:0] addr,
    output logic [63:0] data_out
);
    import CorePack::*;
    reg [63:0] data_in_reg;
    always @(*) begin
        data_in_reg = data_in >> (8 *addr);
        case (mem_op)
            MEM_NO:data_out = data_in_reg;
            MEM_D:data_out = data_in_reg;
            MEM_W:data_out = {{32{data_in_reg[31]}},data_in_reg[31:0]};
            MEM_H:data_out = {{48{data_in_reg[15]}},data_in_reg[15:0]};
            MEM_B:data_out = {{56{data_in_reg[7]}},data_in_reg[7:0]};
            MEM_UB:data_out = {{56{1'b0}},data_in_reg[7:0]};
            MEM_UH:data_out = {{48{1'b0}},data_in_reg[15:0]};
            MEM_UW:data_out = {{32{1'b0}},data_in_reg[31:0]};
            default:data_out = 0;
        endcase
    end
endmodule
```

## 仿真

### RTYPE

![8a067d3ccc00e629c4e26e3487c9ef6](D:\Documentary\WeChat Files\wxid_***\FileStorage\Temp\8a067d3ccc00e629c4e26e3487c9ef6.png)

### ITYPE

![af805d8f659ca6b9dbd744dd8e1cdf3](D:\Documentary\WeChat Files\wxid_***\FileStorage\Temp\af805d8f659ca6b9dbd744dd8e1cdf3.png)

### BTYPE

![image-20240625121620560](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20240625121620560.png)

### UTYPE

![image-20240625121652350](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20240625121652350.png)

### JTYPE

![image-20240625121715131](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20240625121715131.png)

### STYPE

![image-20240625121753762](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20240625121753762.png)

### REMAIN

![image-20240625121810763](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20240625121810763.png)

### FULL

![image-20240625121829504](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20240625121829504.png)

## 上板

<img src="D:\Documentary\WeChat Files\wxid_***\FileStorage\Temp\15b869639d7ed3cea935142d2e2245a.jpg" alt="15b869639d7ed3cea935142d2e2245a" style="zoom: 25%;" />