# MiniSQL —— 精简型单用户 SQL 引擎（C++）

MiniSQL 是一个从零实现的精简型单用户关系型数据库引擎。用户通过字符界面（或重定向脚本）输入 SQL，
完成数据库/表/索引的建立与删除、记录的插入/删除/修改/查找。整体对标 **CMU 15-445 / BusTub** 的分层架构，
强调对 DBMS 底层技术（缓冲池、B+ 树、记录存储、并发与恢复）的理解与实现。

>**状态：核心需求 + 全部 Bonus 均已实现，13 个单元测试全部通过。**
>完整验收脚本（3 个数据库、10 万条 `insert` 及各类 `select/delete/update/index` 操作）端到端跑通，约 3.4 秒。

---

## 1. 功能需求覆盖

| 需求 | 说明 | 覆盖位置 |
|------|------|----------|
| 数据类型 | `integer` / `char(n)` / `float` 三种 | `src/common/value.h` |
| 多数据库 | `create/drop/use database`、`show databases/tables`，每库独立文件 | `src/api/database_engine.*` |
| 表定义 | 单表 ≤ 32 属性；属性可声明 `unique`；支持单属性主键 | `src/catalog/` |
| 索引 | 主键/`unique` 列自动建 B+ 树索引；`create/drop index` 显式建删（单属性单值） | `src/storage/index/` |
| 数据操作 | 多条件 `AND` 查询（等值 + 区间）；插入；删除；**修改 (`update`)** | `src/api/`、`src/storage/` |
| 约束 | 主键唯一、`unique` 列唯一，借索引在插入/更新时强制 | `src/api/execute_engine.cpp` |
| 持久化 | 数据、元数据、索引根、库清单均落盘，重启后恢复 | 全栈 |

---

## 2. 系统架构

```
                ┌────────────────────────────┐
                │   main.cpp  (REPL / 批处理)  │   按 ';' 切分语句
                └──────────────┬─────────────┘
                               │ SQL 文本
                ┌──────────────▼─────────────┐
   parser/      │  Interpreter  (SQL → AST)   │   手写词法 + 递归下降
                └──────────────┬─────────────┘
                               │ Statement
   api/         ┌──────────────▼─────────────┐
                │  ExecuteEngine (语句派发)    │   类型强制 / where 过滤 / 索引同步
                └──────────────┬─────────────┘
                               │ 作用于「当前库」
   api/         ┌──────────────▼─────────────┐
                │  DatabaseEngine (多库管理)   │   每库一套存储栈 + databases.meta
                └───┬───────────┬─────────┬───┘
                    │           │         │
   catalog/  ┌──────▼─────┐  ┌──▼──────┐  │
             │  Catalog   │  │  Index  │  │
             │  Manager   │  │ Manager │  │  storage/index/  (B+Tree)
             └──────┬─────┘  └──┬──────┘  │
                    │           │         │
   storage/  ┌──────▼───────────▼─────────▼───┐
   record/   │  TableHeap / Record (记录存储)  │
             └──────────────┬─────────────────┘
                            │ 页请求
   storage/  ┌──────────────▼─────────────────┐
   buffer/   │  BufferPoolManager (+Replacer)  │  ← LRU / Clock(Bonus)
             └──────────────┬─────────────────┘
                            │ 页读写
   storage/  ┌──────────────▼─────────────────┐
   disk/     │  DiskManager (+空闲页回收)       │  ← 数据库文件 + .free 旁车
             └─────────────────────────────────┘

   Bonus 自包含模块（不在单用户执行路径上）：
     concurrency/  LockManager + Transaction    (2PL + wound-wait 死锁预防)
     recovery/     LogManager + RecoveryManager  (WAL / REDO-UNDO 崩溃恢复)
```

**分层铁律**：上层只通过 `BufferPoolManager` 的 `Fetch/New/Unpin` 访问页，
任何模块都**不直接**调用 `DiskManager`。这是存储层解耦的核心约定。

---

## 3. 模块 → 代码位置映射

| 模块 | 代码位置 | 职责 | 单元测试 |
|----------|----------|------|------|
| #1 Disk & Buffer Pool | `src/storage/disk/`、`src/storage/buffer/` | 按页读写磁盘；缓冲池；LRU/Clock 置换 | `disk_manager_test`、`buffer_pool_manager_test`、`lru_replacer_test`、`clock_replacer_test` |
| #2 Record Manager | `src/storage/record/` | 记录定长序列化、数据页内增删查、堆表 | `table_heap_test` |
| #3 Index Manager | `src/storage/index/` | B+ 树（分裂/合并/借位/根塌缩）、点查/区间 | `b_plus_tree_test`、`index_manager_test` |
| #4 Catalog Manager | `src/catalog/` | 表/属性/索引元数据管理与单页持久化 | `catalog_test` |
| 多库管理 | `src/api/database_engine.*` | 多数据库生命周期与切换 | （经 `execute_engine_test`） |
| SQL 解释器 | `src/parser/` | 词法 + 递归下降解析 | `interpreter_test` |
| 执行引擎 | `src/api/execute_engine.*` | 语句派发、类型强制、约束、索引同步 | `execute_engine_test`（端到端） |
| #6 Recovery (Bonus) | `src/recovery/` | WAL 日志、REDO 全部 / UNDO 失败事务 | `recovery_test` |
| #7 Lock Manager (Bonus) | `src/concurrency/` | 共享/排他锁、2PL、wound-wait 死锁预防 | `lock_manager_test` |
| 磁盘空闲页回收 (Bonus) | `src/storage/disk/`、DROP 路径 | free list + `.free` 持久化，DROP 真正回收页 | `disk_reclaim_test` |
| 入口 | `src/main.cpp` | REPL / 批处理 | — |

---

## 4. 目录结构

```
proj/
├── CMakeLists.txt          # 构建脚本（递归收集 src 下所有 .cpp；test 下每个 .cpp 一个测试）
├── README.md
├── docs/
│   ├── prompts/            # 各模块的 AI 实现 prompt 存档（00..09）
│   └── 实验报告.md          # 设计与实现报告
├── src/
│   ├── main.cpp                        # REPL / 批处理入口
│   ├── common/        config.h rid.h exception.h value.h
│   ├── parser/        statement.h interpreter.*
│   ├── api/           database_engine.* execute_engine.*
│   ├── catalog/       column.h schema.h catalog_manager.*
│   ├── concurrency/   transaction.h lock_manager.*         # Bonus
│   ├── recovery/      log_record.h log_manager.* recovery_manager.*   # Bonus
│   └── storage/
│       ├── disk/      disk_manager.*
│       ├── page/      page.h
│       ├── buffer/    replacer.h lru_replacer.* clock_replacer.* buffer_pool_manager.*
│       ├── record/    row.h table_heap.*
│       └── index/     b_plus_tree.* index_manager.*
└── test/              每个模块一个不依赖框架的 assert 测试
```

---

## 5. 构建与运行

依赖：CMake ≥ 3.15，支持 C++17 的编译器（GCC / Clang / MSVC；本项目在 Windows + MinGW g++13 下开发）。

```bash
cmake -S . -B build
cmake --build build
ctest --test-dir build --output-on-failure   # 运行全部 13 个单元测试
```

**交互式 REPL**：

```bash
./build/minisql            # Windows: ./build/minisql.exe
```
```
minisql> create database school;
minisql> use school;
minisql> create table student (id int, name char(20), gpa float, primary key (id));
minisql> create index idx_name on student (name);
minisql> insert into student values (1, "alice", 3.8);
minisql> select * from student where id = 1 and gpa > 3.0;
minisql> update student set gpa = 4.0 where id = 1;
minisql> delete from student where id = 1;
minisql> exit;
```

**批处理**（重定向 SQL 脚本）：

```bash
./build/minisql < script.sql
```

>运行时会在工作目录生成 `<db>.db`（数据）、`databases.meta`（库清单）、`<db>.db.free`（空闲页），
>这些均已被 `.gitignore` 忽略。

---

## 6. 支持的 SQL 子集

| 类别 | 语句 |
|------|------|
| 数据库 | `create database <d>;` / `drop database <d>;` / `use <d>;` / `show databases;` / `show tables;` |
| 建表 | `create table <t> (<col> <type> [unique], ..., primary key (<col>));` |
| 删表 | `drop table <t>;` |
| 索引 | `create index <name> on <t> (<col>);` / `drop index <name>;` |
| 插入 | `insert into <t> values (<v1>, <v2>, ...);` |
| 删除 | `delete from <t> [where <cond> and ...];` |
| 修改 | `update <t> set <col> = <v>, ... [where <cond> and ...];` |
| 查询 | `select * \| <col>, ... from <t> [where <cond> and ...];` |

- 类型：`int` / `char(n)` / `float`；字符串字面量用双引号。
- 条件 `<cond>` 形如 `col = v` / `<>` / `<` / `>` / `<=` / `>=`，多个条件仅用 `AND` 连接。
- 词法支持 `--` 行注释、关键字大小写不敏感。
- 值会按列类型强制（如整数字面量写入 `float` 列）。

>未实现：`or` / `join` / 聚合 / 子查询（超出需求范围）。

---

## 7. 实现要点与优化

- **定长记录 + 槽位堆表**：每数据页 `[next_page_id | slot_count]` 页头 + 「状态字节 + 定长记录」槽；
  删除按槽标记，空间可复用。
- **堆表尾页缓存**：插入直接追加到缓存的尾页（O(1) 摊还），避免每次从链表头扫描（曾导致 10 万插入 O(n²) 超时）。
- **B+ 树**：递归实现分裂/合并/借位/根塌缩；节点页为「先插入后分裂」的临时溢出各预留 1 槽（否则溢出键越界）。
- **缓冲池**：`BUFFER_POOL_SIZE=1024`（约 4MB/库），使工作集常驻、减少换出刷盘。
- **目录持久化**：表名/schema/`first_page_id`/索引根序列化到 0 号目录页；索引根随插入变化在 flush 时回填。
- **空间回收**：`DropTable`/`DropIndex` 经 `TableHeap::FreeAllPages` 与 `BPlusTree::Destroy` 把页归还
  DiskManager 空闲表（`.free` 旁车文件持久化）。

---

## 8. 测试

每个模块配一个不依赖第三方框架的 `assert` 单元测试，`ctest` 统一运行：

```
b_plus_tree_test         buffer_pool_manager_test   catalog_test
clock_replacer_test      disk_manager_test          disk_reclaim_test
execute_engine_test      index_manager_test         interpreter_test
lock_manager_test        lru_replacer_test          recovery_test
table_heap_test
                                         → 13/13 全部通过
```

`execute_engine_test` 为端到端测试（经 Interpreter + ExecuteEngine + 多库存储栈，含关库/重开的持久化验证）。

---

## 9. 实现路线（按依赖顺序，均已完成）

```
DiskManager → BufferPoolManager(+LRUReplacer) → TableHeap/Record → CatalogManager
                                                       │
                                                       ▼
                                              BPlusTree / IndexManager → 回填主键/唯一索引
                                                       │
                                                       ▼
                          Interpreter → DatabaseEngine + ExecuteEngine + main 接线
                                                       │
              Bonus: ClockReplacer / 空闲页回收 / LockManager / WAL Recovery
```

详细设计与实现过程见 [`docs/实验报告.md`](docs/实验报告.md)，各模块的 AI 实现 prompt 见 `docs/prompts/`（未收录）。
