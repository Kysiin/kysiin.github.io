# `crack_enigma.c` 代码详解

>本文逐段解释 `crack_enigma.c` 的实现原理。该程序模拟一台 Enigma 加密机，
>并利用题目给出的「齿轮旋转次数」约束条件，对 Enigma 的密钥空间进行剪枝搜索，
>从而在很短时间内破解出齿轮排列 `init_rotor` 和明文 `plain`。

---

## 一、题目背景

给定：

- `cipher`：密文（≤255 个大写字母）
- `key_word`：明文的**首个单词**（长度 n ∈ [5, 26]），它一定是 `plain` 的开头
- `init_plug`：接线板（plugboard）初始连线，`main()` 中固定为
  `"AZ BY CX DW EV FU GT HS IR JQ KP LO MN"`

求：

- `init_rotor`：3 个齿轮的排列（例如 `"321"`）
- `plain`：完整明文

**关键已知条件（题目第 ④ 条）**：用 Enigma 解密 `cipher` 前 n 个字符的过程中，

1. **右侧齿轮**会旋转 **n 次**（每个字符必转一次）
2. **中间齿轮**会旋转 **恰好 2 次**
3. **左侧齿轮**会旋转 **恰好 1 次**

这条约束是整个剪枝算法的核心——它把原本庞大的搜索空间压缩成可以瞬间枚举的小集合。

---

## 二、Enigma 工作原理速览

一个字符 `ch` 的加/解密路径（Enigma 是对合的，加密与解密用同一过程）：

```
键盘输入 ch
   │
   ▼
[接线板 plugboard]  ──►  [右齿轮]►[中齿轮]►[左齿轮]
                                              │
                                          [反射板 reflector]
                                              │
[接线板 plugboard]  ◄──  [右齿轮]◄[中齿轮]◄[左齿轮]
   │
   ▼
亮灯输出
```

- 信号先**正向**穿过 右→中→左 三个齿轮，经反射板，再**反向**穿过 左→中→右。
- 每按下一个键，齿轮**先转动再加密**。
- 转动规则（含著名的「双步进 / double-stepping」现象）：
  - 右齿轮每次都转。
  - 当右齿轮处在 notch（卡口）位置时，带动中齿轮转。
  - 当中齿轮自身处在 notch 位置时，中齿轮**自己也转一次**（双步进），并带动左齿轮转。

---

## 三、全局数据结构

```c
char plugboard[27];   // 接线板映射表（被填充并使用）
char rotor[3];        // 题目模板保留的全局量（本实现中未实际使用）
char ring[4];         // 同上，未使用
char key[4];          // 同上，未使用

char rotor_table[5][27] = { ... };  // 5 种齿轮的内部接线（1~5 号）
char reflector[]  = "YRUHQSLDPXNGOKMIEBFZCWVJAT";  // 反射板接线
char step_char[6] = "RFWKA";        // 各齿轮 notch 的参考字母
```

为加速运算，程序把这些字符表预处理成整数下标表（`'A'→0 … 'Z'→25`）：

```c
static int plugboard_map[26];  // 接线板：字母 i ↔ plugboard_map[i]
static int rotor_fwd[5][26];   // 第 r 号齿轮的正向接线（下标版）
static int rotor_rev[5][26];   // 第 r 号齿轮的反向接线（rotor_fwd 的逆）
static int reflector_map[26];  // 反射板（下标版）
```

---

## 四、辅助函数逐个详解

### 1. `mod26` —— 取模到 [0,25]

```c
static int mod26(int x) {
    x %= 26;
    if (x < 0) x += 26;   // C 语言负数取模结果可能为负，需修正
    return x;
}
```

齿轮位置、偏移都在模 26 的环上运算，所有加减都要经过它。

### 2. `notch_pos` —— 计算某号齿轮的 notch 位置

```c
static int notch_pos(int rotor_no) {
    return mod26((step_char[rotor_no - 1] - 'A') - 1);
}
```

`step_char = "RFWKA"`，例如 1 号齿轮的参考字母是 `'R'`。
题目规定 `notch = step_char[r-1] - 1`，即取**前一个字母**的位置。
所以 1 号齿轮 notch = `('R'-'A') - 1 = 17 - 1 = 16`。

「齿轮位置 == notch_pos」时，下一次按键会带动相邻齿轮转动。

### 3. `init_tables` —— 预处理接线表

```c
static void init_tables(void) {
    for (r = 0; r < 5; ++r) {
        for (i = 0; i < 26; ++i)
            rotor_fwd[r][i] = rotor_table[r][i] - 'A';   // 字符表 → 下标表
        for (i = 0; i < 26; ++i)
            rotor_rev[r][ rotor_fwd[r][i] ] = i;         // 求逆：正向的逆即反向
    }
    for (i = 0; i < 26; ++i)
        reflector_map[i] = reflector[i] - 'A';
}
```

`rotor_rev` 是 `rotor_fwd` 的**逆置换**：若正向把 i 映射到 j，则反向把 j 映射回 i。
信号「回程」穿过齿轮时用 `rotor_rev`。

### 4. `build_plugboard` —— 构造接线板映射

```c
static void build_plugboard(const char init_plug[]) {
    for (i = 0; i < 26; ++i) {          // 默认每个字母映射到自己
        plugboard_map[i] = i;
        plugboard[i] = 'A' + i;
    }
    // 把 init_plug 中的字母两两成对，互相交换
    for (i = 0; init_plug[i]; ++i) {
        char ch = init_plug[i];
        if (ch < 'A' || ch > 'Z') continue;   // 跳过空格
        if (first == -1) first = ch - 'A';    // 记住一对中的第一个
        else {
            int second = ch - 'A';
            plugboard_map[first]  = second;    // 双向交换
            plugboard_map[second] = first;
            ...
            first = -1;
        }
    }
}
```

输入如 `"AZ BY CX ..."`，含义是 A↔Z、B↔Y、C↔X……该函数把这些配对写进 `plugboard_map`。
未出现在配对里的字母保持映射到自身。

### 5. `rotor_forward` / `rotor_backward` —— 带偏移的齿轮置换

```c
static int rotor_forward(int rotor_no, int offset, int ch) {
    int idx = mod26(ch + offset);             // 进入齿轮前，加上偏移
    int out = rotor_fwd[rotor_no - 1][idx];   // 查接线表
    return mod26(out - offset);               // 出齿轮后，减回偏移
}
```

`offset` 表示该齿轮当前「**位置 − 环设置(ring)**」的等效偏移量。
齿轮转动 = `offset` 增大；接线表本身不动，靠加减 `offset` 模拟旋转。
`rotor_backward` 完全相同，只是查的是逆表 `rotor_rev`（回程）。

### 6. `enigma_char` —— 单个字符的完整加/解密

```c
static char enigma_char(const int order[3], int off_l, int off_m, int off_r, char ch) {
    int x = ch - 'A';
    x = plugboard_map[x];                 // 接线板
    x = rotor_forward (order[2], off_r, x);   // 右齿轮（正向）
    x = rotor_forward (order[1], off_m, x);   // 中齿轮
    x = rotor_forward (order[0], off_l, x);   // 左齿轮
    x = reflector_map[x];                     // 反射板
    x = rotor_backward(order[0], off_l, x);   // 左齿轮（反向）
    x = rotor_backward(order[1], off_m, x);   // 中齿轮
    x = rotor_backward(order[2], off_r, x);   // 右齿轮
    x = plugboard_map[x];                 // 接线板
    return 'A' + x;
}
```

注意 `order[0]=左`、`order[1]=中`、`order[2]=右`。
信号严格按「右→中→左 → 反射 → 左→中→右」流动，与 Enigma 物理结构一致。
此函数**不**改变齿轮位置，转动由调用方负责。

### 7. `match_keyword` —— 验证一组密钥能否解出 key_word

```c
static int match_keyword(cipher, key_word, order,
                         init_pos_m, init_pos_r,      // 中/右齿轮初始“位置”
                         init_off_l, init_off_m, init_off_r) // 三齿轮初始“偏移”
{
    pos_l = 0; pos_m = init_pos_m; pos_r = init_pos_r;
    off_l = init_off_l; off_m = init_off_m; off_r = init_off_r;

    for (i = 0; i < len; ++i) {
        int middle_at_notch = (pos_m == notch_pos(order[1]));
        int right_at_notch  = (pos_r == notch_pos(order[2]));

        if (middle_at_notch) {            // 双步进：中在 notch → 左转、中转
            pos_l = mod26(pos_l + 1); off_l = mod26(off_l + 1);
        }
        if (middle_at_notch || right_at_notch) {  // 右在 notch 或 中在 notch → 中转
            pos_m = mod26(pos_m + 1); off_m = mod26(off_m + 1);
        }
        pos_r = mod26(pos_r + 1); off_r = mod26(off_r + 1);  // 右每次都转

        if (enigma_char(order, off_l, off_m, off_r, cipher[i]) != key_word[i])
            return 0;   // 只要有一个字符对不上，这组密钥不成立
    }
    return 1;           // 前 n 个字符全部匹配
}
```

这里同时维护两套量：

- `pos_*`：齿轮**真实位置**，只用于判断是否到达 notch（控制转动逻辑）。
- `off_*`：齿轮**有效偏移**（位置 − ring），用于实际接线运算。
  二者相差一个常数（ring 设置），所以始终同步 +1。

「先转动、后加密」的顺序与真实 Enigma 一致。

### 8. `decrypt_text` —— 解出完整明文

与 `match_keyword` 的循环体逐字相同，只是不做比较，而是把每个解密结果写入 `plain[i]`，
最后补 `'\0'`。在确认密钥正确后调用，输出整段明文。

### 9. `first_step_offset` —— 预计算第一步的转动增量

```c
static void first_step_offset(order, init_pos_m, init_pos_r,
                              int *delta_l, int *delta_m, int *delta_r) {
    int middle_at_notch = (init_pos_m == notch_pos(order[1]));
    int right_at_notch  = (init_pos_r == notch_pos(order[2]));
    *delta_l = 0; *delta_m = 0; *delta_r = 1;     // 右一定转
    if (middle_at_notch)                  *delta_l = 1;
    if (middle_at_notch || right_at_notch) *delta_m = 1;
}
```

因为「按键先转动」，加密第 0 个字符时齿轮已经转了一步。
该函数算出第 0 步左/中/右各自的增量 `delta`，供 `crack()` 做**快速预筛**（见下文）。

---

## 五、核心破解函数 `crack()`

### 5.1 整体结构

```c
init_tables();
build_plugboard(init_plug);
word_len = strlen(key_word);   // n

for (a=1..5)               // 左齿轮编号
 for (b=1..5, b!=a)        // 中齿轮编号
  for (c=1..5, c!=a,!=b)   // 右齿轮编号        —— 共 5×4×3 = 60 种排列
   order = {a,b,c};
   for (mode=0..1)                              —— 双步进发生顺序的两种情形
    for (trigger = mode .. word_len-2+mode)     —— 右齿轮在第几个字符到达 notch
     for (off_m=0..25)
      for (off_r=0..25)
       for (off_l=0..25)
         先用 cipher[0] 快速预筛；
         通过后再调用 match_keyword 完整验证；
         成功 → 写 init_rotor、调用 decrypt_text、return。
```

### 5.2 为什么不用暴力枚举所有齿轮位置？

朴素做法要枚举：齿轮排列 60 × 三齿轮初始位置 26³ ≈ 100 万组，再考虑 ring 又是 26³。
本程序利用题目约束，把**中、右齿轮的初始位置**直接推算出来，
只剩偏移 `off_l/off_m/off_r`（即 ring 设置的自由度）需要枚举，搜索空间大幅缩小。

### 5.3 约束如何转化为 `mode` 与 `trigger`

题目保证前 n 个字符中：**左转 1 次、中转 2 次、右转 n 次**。

- 左齿轮只在「中齿轮处于 notch」时转 → 中处于 notch 的事件**恰好发生 1 次**，
  且这一次同时贡献「左转 1 次 + 中转 1 次」（双步进）。
- 中齿轮还需再转 1 次，只能来自「右齿轮处于 notch」→ 右到达 notch 的事件
  **也恰好发生 1 次**。
- 这两个事件必须发生在**不同字符**上（若同一字符，中只会 +1，凑不够 2 次）。

于是 n 个字符里精确存在两个特殊位置：一个是「右到达 notch」，一个是「中到达 notch（双步进）」。
两者的先后顺序产生两种情形，对应 `mode`：

| `mode` | 中齿轮初始位置 `init_pos_m` | 含义 |
|:------:|:--------------------------|:-----|
| 1 | `notch_pos(中)` | 中齿轮**一开始就在 notch**：第 0 个字符即双步进（左转+中转），右到达 notch 在之后的 `trigger` 处 |
| 0 | `notch_pos(中) - 1` | 中齿轮在 notch 前一格：先由「右到达 notch」（第 `trigger` 处）把中推到 notch，紧接着第 `trigger+1` 处发生双步进 |

```c
init_pos_m = notch_pos(order[1]);
if (mode == 0) init_pos_m = mod26(init_pos_m - 1);
```

而 `trigger` 表示**右齿轮在第几个字符到达 notch**。
由于 `match_keyword` 中是「先判断 `pos_r == notch` 再 +1」，
要让第 `trigger` 个字符时 `pos_r == notch`，需令初始位置：

```c
init_pos_r = mod26(notch_pos(order[2]) - trigger);
```

`trigger` 的取值范围 `[mode, word_len-2+mode]` 保证两个事件都落在前 n 个字符内，
且彼此错开（mode=1 时双步进在 0、右 notch 在 ≥1；mode=0 时右 notch 在 `trigger`、双步进在 `trigger+1 ≤ n-1`）。

>这样，`init_pos_m` 和 `init_pos_r`（中、右齿轮的**真实初始位置**）就被约束条件**唯一确定**了，
>不再需要枚举，这正是剪枝的关键。

### 5.4 偏移枚举与快速预筛

真实位置定了，但「偏移」`off_*`（位置与 ring 之差，等价于 ring 设置）仍未知，需枚举 `off_l, off_m, off_r` 各 0~25。

为避免对每个 `off_l` 都跑完整的 n 字符比较，程序先用第 0 个字符做预筛：

```c
int cur_m = mod26(off_m + first_delta_m);   // 加密第 0 字符时的“当步偏移”
int cur_r = mod26(off_r + first_delta_r);   // = 初始偏移 + 第一步增量
...
int cur_l = mod26(off_l + first_delta_l);

if (enigma_char(order, cur_l, cur_m, cur_r, cipher[0]) != key_word[0])
    continue;                                // cipher[0] 都对不上，直接跳过

if (match_keyword(cipher, key_word, order, init_pos_m, init_pos_r, off_l, off_m, off_r))
    ... // 完整验证通过
```

`first_delta_*` 来自 `first_step_offset`，即「按键先转一步」后的偏移增量。
只有 `cipher[0]→key_word[0]` 这一关通过，才进入更贵的 `match_keyword`（验证全部 n 个字符）。

### 5.5 命中后的输出

```c
init_rotor[0] = '0' + order[0];   // 例如 order = {3,2,1} → "321"
init_rotor[1] = '0' + order[1];
init_rotor[2] = '0' + order[2];
init_rotor[3] = '\0';
decrypt_text(cipher, plain, order, init_pos_m, init_pos_r, off_l, off_m, off_r);
return;
```

题目保证解唯一，故第一个命中即为答案。
若所有组合都失败（异常情况），把 `init_rotor` 和 `plain` 置空串。

---

## 六、`main()` 与样例对照

```c
int main() {
    char cipher[0x100], key_word[0x100], init_rotor[0x20], plain[0x100];
    char init_plug[] = "AZ BY CX DW EV FU GT HS IR JQ KP LO MN";
    gets(cipher);                 // 读入密文
    gets(key_word);               // 读入首单词
    crack(cipher, key_word, init_plug, init_rotor, plain);
    printf("rotor:%s\n", init_rotor);
    printf("plain:%s",   plain);
    return 0;
}
```

样例 1：

```
输入: UWHGQCOOSKJTVPZKBVCSXOIVNJIQTAJUTTRWVNWZTWZMKMYQGHMNUXGGTXJPCEJSGM
      LADYBIRD
输出: rotor:321
      plain:LADYBIRDLADYBIRDFLYAWAYHOMEYOURHOUSEISONFIREANDYOURCHILDRENALLGONE
```

可见 `key_word = "LADYBIRD"`（n=8）确为明文开头，破解出齿轮排列 `321`。

---

## 七、复杂度分析

外层枚举量级：

- 齿轮排列：`5×4×3 = 60`
- `mode`：2
- `trigger`：≤ `n-1`（n ≤ 26）
- `off_m, off_r, off_l`：`26 × 26 × 26 = 17576`

理论上界约 `60 × 2 × 25 × 17576 ≈ 5.3×10⁷`，
但绝大多数 `off_l` 在 `cipher[0]` 预筛阶段即被淘汰（26 选 1 命中率约 1/26），
真正进入 `match_keyword` 的次数很少，实际运行近乎瞬时。

相比朴素暴力（还要枚举中右齿轮位置 26²、ring 26³），本算法把
「中、右齿轮真实位置」由约束条件直接定死，是性能的关键来源。

---

## 八、值得注意的点 / 潜在改进

1. **`gets()` 不安全**：可能缓冲区溢出，现代 C 已弃用，工程中应换 `fgets()`。
   此处因是题目固定模板、输入受控而保留。
2. **未使用的全局量**：`rotor[3]`、`ring[4]`、`key[4]` 是题目模板保留变量，
   本实现并未真正使用（破解信息通过参数与局部变量传递）。
3. **`pos` 与 `off` 双轨**：`pos_*` 管「是否到 notch」（控制转动），
   `off_*` 管「实际接线偏移」，二者相差 ring 常量，理解这点是读懂步进逻辑的关键。
4. **对合性**：因为 Enigma 加解密同构，`enigma_char` 既能加密也能解密，
   程序据此用「明文首单词」反推密钥。

---

*文档对应源码：`crack_enigma.c`*
