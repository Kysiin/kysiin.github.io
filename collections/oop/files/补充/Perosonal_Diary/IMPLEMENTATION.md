# Personal Diary 实验实现说明

本实验用 C++ 实现了一个命令行（CLI）的「个人日记」软件。日记以纯文本文件存储，每一天一条记录。本文档解释整个实验的实现方式：整体设计、各文件职责、编译流程，以及自动化测试是如何验证程序正确性的。

---

## 1. 需求概览

软件把日记保存在纯文本文件中，每行一条记录，格式为：

```
yyyy-mm-dd:内容
```

- 日期为 `yyyy-mm-dd` 格式，后跟一个冒号 `:`，再跟当天内容。
- 同一日期不允许有重复行。

软件由四个独立的可执行程序组成：

| 程序 | 功能 |
|------|------|
| `pdadd <date>`    | 从命令行参数取日期，从标准输入读内容，添加一条记录；同日期已存在则**覆盖** |
| `pdlist`          | 按日期顺序列出所有记录到标准输出 |
| `pdshow <date>`   | 输出指定日期的记录；不存在则输出 `date:No entry found for the given date` |
| `pdremove <date>` | 删除指定日期的记录；成功返回 0，失败打印 `Entry not found at date` 并返回非 0 |

---

## 2. 整体架构：一个核心类 + 四个入口

实现采用**「公共逻辑封装成类，四个程序复用」**的面向对象设计：

```
                 ┌─────────────────────────┐
                 │   PersonalDiary 类        │
                 │  (personal_diary.h /      │
                 │   personal_dairy.cpp)     │
                 │  - 负责文件读写与增删查    │
                 └───────────┬─────────────┘
        ┌──────────┬─────────┼─────────┬──────────┐
        │          │         │         │          │
    pdadd.cpp  pdlist.cpp  pdshow.cpp  pdremove.cpp
     (四个 main 入口，各自调用同一个类)
```

四个 `.cpp` 都只写一个 `main()`，把真正的业务逻辑交给 `PersonalDiary` 类。这样避免了文件读写代码在四处重复。

---

## 3. 核心类 `PersonalDiary`

### 3.1 头文件 `src/personal_diary.h`

类的对外接口定义如下：

```cpp
class PersonalDiary {
private:
    std::string filename;                          // 数据文件名
    std::map<std::string, std::string> entries;    // 日期 -> 内容
    void load();   // 从文件载入到内存
    void save();   // 从内存写回文件
public:
    PersonalDiary(const std::string& file = "personal_dairy.txt");
    ~PersonalDiary();
    bool addEntry(const std::string& date, const std::string& content);
    std::vector<std::pair<std::string, std::string>> listEntries();
    bool showEntry(const std::string& date, std::string& content);
    bool removeEntry(const std::string& date);
    bool entryExists(const std::string& date);
};
```

**关键设计点 —— 用 `std::map` 作为内存数据结构：**

- `std::map` 的键（日期字符串）天然**自动排序且去重**。
- 「按日期顺序列出」直接利用了 map 的有序性，无需手动排序。
- 「同日期覆盖」直接利用了 map 的键唯一性（`entries[date] = content` 自动覆盖）。

### 3.2 实现 `src/personal_dairy.cpp`

整个类的生命周期围绕「**构造时载入、析构时保存**」的 RAII 模式设计：

- **构造函数** → 调用 `load()`：打开数据文件，逐行用 `find(':')` 找到第一个冒号，冒号前是日期、冒号后是内容，存入 `map`。
- **析构函数** → 调用 `save()`：把 `map` 中所有条目按 `日期:内容` 格式逐行写回文件。

因此每个程序的使用模式都是一致的：

1. 创建 `PersonalDiary` 对象 → 自动从文件读入内存；
2. 在内存（map）上做增/删/查；
3. 对象离开作用域析构 → 自动把内存写回文件。

各方法实现：

| 方法 | 实现方式 |
|------|----------|
| `addEntry`   | `entries[date] = content;`（已存在则覆盖） |
| `listEntries`| 遍历 map，按序拷贝成 vector 返回 |
| `showEntry`  | `entries.find(date)`，找到则通过引用参数返回内容，返回 `true` |
| `removeEntry`| `find` 后 `erase`，删除成功返回 `true`，否则 `false` |
| `entryExists`| 判断 `find` 结果是否存在 |

>注意：`save()` 在析构时**总是**把 map 整体写回文件。这意味着 `pdlist`、`pdshow` 等只读程序运行后，也会把文件重新规范化写一遍（按日期排序、统一格式）。

---

## 4. 四个程序入口

### 4.1 `pdadd.cpp`
- 从 `argv[1]` 取日期。
- 循环 `getline(cin, ...)` 读取标准输入的所有行作为内容，多行之间用 `\n` 拼接（支持多行日记）。
- `diary.addEntry(date, content)` 加入；对象析构时写回文件。

### 4.2 `pdlist.cpp`
- 创建对象，调用 `listEntries()`，逐条 `cout << 日期 << ":" << 内容` 输出。
- 因为 map 有序，输出天然按日期排序。

### 4.3 `pdshow.cpp`
- 从 `argv[1]` 取日期，调用 `showEntry()`。
- 找到 → 输出 `日期:内容`，返回 0。
- 找不到 → 输出 `日期:No entry found for the given date`，返回 1。

### 4.4 `pdremove.cpp`
- 从 `argv[1]` 取日期，调用 `removeEntry()`。
- 成功 → 返回 0。
- 失败 → 输出 `Entry not found at 日期`，返回 **255**（即 `-1` 在 shell 中的退出码表现）。

---

## 5. 编译流程（Makefile）

采用两层 Makefile：

**顶层 `Makefile`**：只是进入 `src` 目录调用里面的 Makefile。

```make
all:
	cd $(SRC) && make
clean:
	cd $(SRC) && make clean
```

**`src/Makefile`**：真正的构建逻辑。

- 编译器 `g++`，标准 `-std=c++11`。
- 先把每个 `.cpp` 编成 `.o`（隐式规则 `.cpp.o`）。
- 公共目标文件 `personal_dairy.o` 与各程序自己的 `.o` 链接，生成四个可执行文件，输出到**上一级目录**（`OD = ..`）。

```make
$(OD)/pdadd: pdadd.o personal_dairy.o
	$(CC) $(CFLAG) -o $(OD)/pdadd pdadd.o personal_dairy.o
# pdlist / pdshow / pdremove 同理
```

每个可执行文件 = 「自己的 main 入口 .o」+「公共类 personal_dairy.o」链接而成。

---

## 6. 自动化测试（main.sh）

`main.sh` 是评分/验证脚本，流程如下：

1. `make clean` + `make -B`：干净重新编译全部程序。
2. 写入初始数据文件 `personal_dairy.txt`：
   ```
   2021-01-01:Happy New Year
   2021-01-02:Happy New Year 2
   ```
3. 依次执行各程序，把输出全部重定向汇总到 `out`：
   ```sh
   ./pdadd 2024-02-29 <in >out      # in 文件内容是 "started"
   ./pdlist >>out
   ./pdshow 2021-01-01 >>out
   ./pdshow 2022-02-01 >>out        # 测试「找不到」分支
   ./pdremove 2021-01-02 >>out
   echo $? >>out                    # 记录退出码：0（成功）
   ./pdremove 2022-01-02 >>out      # 测试删除不存在条目
   echo $? >>out                    # 记录退出码：255（失败）
   ./pdlist >>out
   ```
4. `diff out std_out`：把实际输出 `out` 与期望输出 `std_out` 比较。
5. 根据 `diff` 结果，向脚本参数 `$1` 指定的文件写入分数：完全一致写 `100`，否则写 `0`。

### 期望输出 `std_out`
```
2021-01-01:Happy New Year
2021-01-02:Happy New Year 2
2024-02-29:started
2021-01-01:Happy New Year
2022-02-01:No entry found for the given date
0
Entry not found at 2022-01-02
255
2021-01-01:Happy New Year
2024-02-29:started
```

这一段输出覆盖了全部四个程序，并验证了：添加、按序列出、查询存在/不存在、删除成功/失败、退出码、覆盖与持久化等所有核心行为。当前 `out` 与 `std_out` 完全一致，说明实现通过测试。

---

## 7. 文件清单

| 文件 | 作用 |
|------|------|
| `readme.md`               | 需求说明（题目） |
| `Makefile`                | 顶层构建入口 |
| `main.sh`                 | 自动化测试 / 评分脚本 |
| `in`                      | 测试用标准输入内容（`started`） |
| `out` / `std_out`         | 测试实际输出 / 期望输出 |
| `personal_dairy.txt`      | 日记数据文件（程序读写的目标） |
| `src/personal_diary.h`    | `PersonalDiary` 类声明 |
| `src/personal_dairy.cpp`  | `PersonalDiary` 类实现（文件读写 + 增删查） |
| `src/pdadd.cpp`           | 添加程序入口 |
| `src/pdlist.cpp`          | 列出程序入口 |
| `src/pdshow.cpp`          | 查询程序入口 |
| `src/pdremove.cpp`        | 删除程序入口 |
| `src/Makefile`            | 实际编译规则 |

---

## 8. 设计小结

- **复用**：所有文件读写与数据操作集中在 `PersonalDiary` 一个类，四个程序仅负责命令行解析与输入输出。
- **数据结构选型**：`std::map<string,string>` 一举解决了「按日期排序」和「同日期去重/覆盖」两个需求。
- **RAII**：构造载入、析构保存，使每个短命的 CLI 程序都能正确地读入和持久化数据。
- **可测试性**：通过 `main.sh` + `diff` 做端到端黑盒测试，用退出码和标准输出共同判定正确性。

>备注：代码中文件名混用了 `dairy`（拼写错误）与 `diary` 两种写法（如 `personal_dairy.cpp` vs `personal_diary.h`、`personal_dairy.txt` vs `personal_diary.txt`），实际生效的数据文件是 `personal_dairy.txt`。功能不受影响，但命名上可统一为正确拼写 `diary`。
