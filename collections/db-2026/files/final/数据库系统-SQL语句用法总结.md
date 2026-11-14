# 数据库系统 SQL 语句用法总结

说明：本文件基于 `3.md`、`4.md`、`5.md` 的内容，总结常见 SQL 语句的作用、基本语法、典型用法和注意点。重点面向考试复习，因此不追求覆盖所有方言细节，而强调“这条语句是干什么的、怎么写、容易错在哪”。

## 1. SQL 基本规则

- SQL 关键字通常大小写不敏感，但复习和书写时建议统一大写。
- 一条 SQL 语句通常以分号 `;` 结尾。
- SQL 注释常见写法：
  - `/* comment */`
  - `-- comment`
- 不等号通常写作 `!=` 或 `<>`。

## 2. 表级定义语句（DDL）

### 2.1 `CREATE TABLE`

作用：创建新表，定义属性、类型和约束。

基本语法：

```sql
CREATE TABLE table_name (
    col1 type1,
    col2 type2,
    ...,
    constraint1,
    constraint2
);
```

常见用法：

- 定义列名和数据类型
- 定义主键 `PRIMARY KEY`
- 定义外键 `FOREIGN KEY ... REFERENCES ...`
- 定义非空约束 `NOT NULL`
- 定义唯一约束 `UNIQUE`
- 定义检查约束 `CHECK(...)`
- 定义默认值 `DEFAULT`

例子：

```sql
CREATE TABLE student (
    ID VARCHAR(10),
    name VARCHAR(20) NOT NULL,
    dept_name VARCHAR(20),
    tot_cred NUMERIC(3, 0) DEFAULT 0,
    PRIMARY KEY (ID)
);
```

注意：

- 声明主键后，该属性（组）自动具备唯一和非空性质。
- 主键可以是复合主键，不一定只有一个属性。

### 2.2 `DROP TABLE`

作用：删除整张表，包括表结构和表中数据。

语法：

```sql
DROP TABLE table_name;
```

注意：

- `DROP TABLE` 是删“表本身”。
- 与 `DELETE FROM table_name;` 不同，后者只是清空数据，不删表结构。

### 2.3 `ALTER TABLE`

作用：修改已有表结构。

常见语法：

```sql
ALTER TABLE table_name ADD column_name data_type;
ALTER TABLE table_name DROP column_name;
ALTER TABLE table_name ADD CONSTRAINT ...;
ALTER TABLE table_name DROP CONSTRAINT constraint_name;
```

常见用途：

- 增加列
- 删除列
- 增加约束
- 删除约束

注意：

- 有些数据库不支持 `DROP column_name`。
- 如果已有数据不满足新增约束，`ALTER TABLE ... ADD CONSTRAINT` 会失败。

### 2.4 `CREATE TABLE LIKE`

作用：按已有表的模式创建一张结构相同的新表。

语法：

```sql
CREATE TABLE new_table LIKE old_table;
```

用途：

- 快速创建结构一致的临时表/备份表。

### 2.5 `CREATE TABLE AS`

作用：根据查询结果创建新表。

语法：

```sql
CREATE TABLE new_table AS (
    SELECT ...
) WITH DATA;
```

用途：

- 保存查询结果
- 创建中间表

注意：

- `WITH DATA` 表示把查询结果也保存到新表中。
- 某些实现即使省略 `WITH DATA` 也会默认保存数据。

## 3. 基本查询语句

### 3.1 `SELECT`

作用：指定要输出哪些列或表达式。

基本语法：

```sql
SELECT col1, col2, ...
FROM table_name;
```

常见用法：

- 选定具体列
- 用 `*` 选全部列
- 写算术表达式
- 配合 `DISTINCT` 去重
- 配合聚合函数

例子：

```sql
SELECT ID, name, salary * 1.05
FROM instructor;
```

### 3.2 `SELECT DISTINCT`

作用：去除重复结果。

语法：

```sql
SELECT DISTINCT col1, col2
FROM table_name;
```

注意：

- SQL 默认允许重复结果。
- `DISTINCT` 可能增加代价。

### 3.3 `FROM`

作用：指定查询所涉及的表或关系。

语法：

```sql
SELECT ...
FROM r1, r2, ..., rn;
```

说明：

- 多个表放在 `FROM` 中，逻辑上先形成笛卡尔积，再由 `WHERE` 或 `JOIN` 过滤。
- 若不同表中有同名属性，应写成 `table_name.column_name`。

### 3.4 `WHERE`

作用：对行进行过滤。

语法：

```sql
SELECT ...
FROM ...
WHERE condition;
```

常见条件：

- 比较：`=`, `<>`, `!=`, `<`, `>`, `<=`, `>=`
- 逻辑：`AND`, `OR`, `NOT`
- 区间：`BETWEEN ... AND ...`
- 模式匹配：`LIKE`
- 空值判断：`IS NULL`, `IS NOT NULL`

例子：

```sql
SELECT name
FROM instructor
WHERE salary BETWEEN 90000 AND 100000;
```

注意：

- `BETWEEN a AND b` 是闭区间。
- `NOT BETWEEN a AND b` 对应开区间外侧：`x < a OR x > b`。
- 不能写 `= NULL`，应使用 `IS NULL`。

### 3.5 `AS`

作用：重命名列名或表名。

语法：

```sql
SELECT old_name AS new_name
FROM table_name AS t;
```

用途：

- 让输出列名更清晰
- 为表起别名，简化连接语句

例子：

```sql
SELECT name AS instructor_name, course_id
FROM instructor, teaches
WHERE instructor.ID = teaches.ID;
```

### 3.6 `ORDER BY`

作用：对结果排序。

语法：

```sql
SELECT ...
FROM ...
ORDER BY col1 [ASC|DESC], col2 [ASC|DESC];
```

用途：

- 按一个或多个属性排序
- 默认通常为升序

例子：

```sql
SELECT title
FROM course
WHERE department = 'CS'
ORDER BY credits DESC;
```

### 3.7 `LIMIT`

作用：限制返回结果的行数。

语法：

```sql
SELECT ...
FROM ...
ORDER BY ...
LIMIT n;
```

常见用途：

- 取前 `n` 行
- 结合排序实现“最大/最小”的查询

## 4. 连接语句

### 4.1 普通连接 `JOIN ... ON`

作用：按任意连接条件连接两个表。

语法：

```sql
SELECT ...
FROM r JOIN s
ON r.a = s.b;
```

特点：

- 最通用
- `ON` 中可以写任意布尔条件

例子：

```sql
SELECT *
FROM student JOIN takes
ON student.ID = takes.ID;
```

### 4.2 自然连接 `NATURAL JOIN`

作用：按所有同名属性自动相等连接。

语法：

```sql
SELECT ...
FROM r NATURAL JOIN s;
```

特点：

- 自动使用同名属性匹配
- 结果中只保留一份公共属性

注意：

- 虽然简洁，但容易因“同名但本不想连接”的属性导致歧义。

### 4.3 `JOIN ... USING`

作用：显式指定“用哪些同名属性连接”。

语法：

```sql
SELECT ...
FROM r JOIN s USING (attr_name);
```

用途：

- 比 `NATURAL JOIN` 更可控
- 比 `ON` 更简洁

### 4.4 外连接

作用：保留连接失败的一侧或双方记录。

语法：

```sql
SELECT ...
FROM r LEFT OUTER JOIN s ON condition;

SELECT ...
FROM r RIGHT OUTER JOIN s ON condition;

SELECT ...
FROM r FULL OUTER JOIN s ON condition;
```

区别：

- `LEFT OUTER JOIN`：保留左表全部行
- `RIGHT OUTER JOIN`：保留右表全部行
- `FULL OUTER JOIN`：保留两边全部行

注意：

- 外连接未匹配的一侧会用 `NULL` 填补。
- 在外连接中，`ON` 与 `WHERE` 的效果不完全一样。
  - `ON` 决定如何匹配
  - `WHERE` 会在连接结果形成后再过滤，有可能把原本保留下来的 `NULL` 行过滤掉

## 5. 分组、聚合与去重

### 5.1 聚合函数

常见聚合函数：

- `COUNT(*)`
- `COUNT(col)`
- `COUNT(DISTINCT col)`
- `SUM(col)`
- `AVG(col)`
- `MIN(col)`
- `MAX(col)`

例子：

```sql
SELECT dept_name, AVG(salary)
FROM instructor
GROUP BY dept_name;
```

注意：

- `SUM` 和 `AVG` 一般要求数值类型。
- 聚合函数不能直接放在 `WHERE` 中。

### 5.2 `GROUP BY`

作用：按指定列分组。

语法：

```sql
SELECT group_col, AGG(...)
FROM table_name
GROUP BY group_col;
```

注意：

- `SELECT` 中凡是不在聚合函数里的列，必须出现在 `GROUP BY` 中。

### 5.3 `HAVING`

作用：对分组后的结果再过滤。

语法：

```sql
SELECT group_col, AGG(...)
FROM table_name
GROUP BY group_col
HAVING condition_on_group;
```

与 `WHERE` 的区别：

- `WHERE`：分组前过滤行
- `HAVING`：分组后过滤组

例子：

```sql
SELECT title, COUNT(*) AS count
FROM course
GROUP BY title
HAVING COUNT(*) > 1;
```

## 6. 子查询

### 6.1 普通子查询

作用：在一个查询里嵌套另一个查询。

常见位置：

- `WHERE`
- `FROM`
- `SELECT`
- `HAVING`

### 6.2 `IN`

作用：判断某值是否属于子查询结果集。

语法：

```sql
SELECT ...
FROM ...
WHERE col IN (
    SELECT ...
);
```

### 6.3 `EXISTS`

作用：判断子查询是否返回至少一行。

语法：

```sql
SELECT ...
FROM ...
WHERE EXISTS (
    SELECT ...
);
```

特点：

- 常用于“是否存在匹配记录”的问题。

### 6.4 `ALL` / `SOME` / `ANY`

作用：与子查询返回的一组值比较。

例子：

```sql
SELECT dept_name
FROM instructor
GROUP BY dept_name
HAVING AVG(salary) >= ALL (
    SELECT AVG(salary)
    FROM instructor
    GROUP BY dept_name
);
```

### 6.5 标量子查询

作用：子查询只返回一个值。

常见位置：

- `SELECT`
- `WHERE`
- `HAVING`

例子：

```sql
SELECT dept_name,
       (SELECT COUNT(*) FROM instructor i2
        WHERE i2.dept_name = department.dept_name)
FROM department;
```

### 6.6 `WITH`

作用：定义公共表表达式（CTE），给复杂子查询命名。

语法：

```sql
WITH cte_name AS (
    SELECT ...
)
SELECT ...
FROM cte_name;
```

用途：

- 提高可读性
- 避免重复写同一个子查询

### 6.7 `WITH RECURSIVE`

作用：定义递归公共表表达式。

语法：

```sql
WITH RECURSIVE cte_name AS (
    base_query
    UNION [ALL]
    recursive_query
)
SELECT ...
FROM cte_name;
```

用途：

- 层次结构查询
- 递归展开

## 7. 数据修改语句（DML）

### 7.1 `INSERT INTO`

作用：插入新行。

常见语法 1：直接插值

```sql
INSERT INTO table_name
VALUES (...);
```

常见语法 2：指定列名

```sql
INSERT INTO table_name (col1, col2, ...)
VALUES (...);
```

常见语法 3：插入查询结果

```sql
INSERT INTO table_name
SELECT ...
FROM ...;
```

例子：

```sql
INSERT INTO instructor
SELECT ID, name, dept_name, 18000
FROM student;
```

### 7.2 `DELETE FROM`

作用：删除满足条件的行。

语法：

```sql
DELETE FROM table_name
WHERE condition;
```

若省略 `WHERE`：

```sql
DELETE FROM table_name;
```

表示清空整张表的数据，但不删除表本身。

### 7.3 `UPDATE`

作用：更新已有行。

语法：

```sql
UPDATE table_name
SET col1 = expr1,
    col2 = expr2
WHERE condition;
```

特点：

- 可结合子查询更新
- 若省略 `WHERE`，会更新整张表

例子：

```sql
UPDATE instructor
SET salary = (
    SELECT AVG(salary)
    FROM instructor
)
WHERE dept_name = 'History';
```

## 8. 视图

### 8.1 `CREATE VIEW`

作用：创建视图。

语法：

```sql
CREATE VIEW view_name AS
SELECT ...;
```

例子：

```sql
CREATE VIEW faculty AS
SELECT ID, name, dept_name
FROM instructor;
```

特点：

- 视图本质上保存的是定义，不一定保存结果。
- 和 `WITH` 不同，`CREATE VIEW` 创建的是可长期复用的数据库对象。

### 8.2 带列名的视图

语法：

```sql
CREATE VIEW view_name(col1, col2, ...)
AS
SELECT ...;
```

### 8.3 `WITH CHECK OPTION`

作用：防止通过视图插入/更新后，结果不再属于该视图定义范围。

语法：

```sql
CREATE VIEW view_name AS
SELECT ...
WHERE ...
WITH CHECK OPTION;
```

用途：

- 保证通过视图写入的数据仍满足视图条件。

## 9. 事务控制语句

### 9.1 `COMMIT`

作用：提交当前事务，使更新永久生效。

语法：

```sql
COMMIT;
```

或：

```sql
COMMIT WORK;
```

### 9.2 `ROLLBACK`

作用：回滚当前事务，撤销当前事务中的更新。

语法：

```sql
ROLLBACK;
```

或：

```sql
ROLLBACK WORK;
```

### 9.3 `SET AUTOCOMMIT OFF`

作用：关闭自动提交。

语法：

```sql
SET AUTOCOMMIT OFF;
```

用途：

- 让多条 SQL 语句组成一个完整事务

### 9.4 `BEGIN ATOMIC ... END`

作用：把多条语句当成一个事务块。

语法：

```sql
BEGIN ATOMIC
    ...
END
```

注意：

- 不是所有数据库都支持该语法。

## 10. 约束相关语句

### 10.1 `PRIMARY KEY`

作用：声明主键。

语法：

```sql
PRIMARY KEY (col1, col2, ...)
```

特点：

- 自动包含唯一和非空约束。

### 10.2 `FOREIGN KEY ... REFERENCES`

作用：声明外键。

语法：

```sql
FOREIGN KEY (col) REFERENCES other_table
```

或：

```sql
FOREIGN KEY (col) REFERENCES other_table(other_col)
```

扩展：

```sql
FOREIGN KEY (col) REFERENCES other_table(other_col)
    ON DELETE CASCADE
    ON UPDATE CASCADE
```

### 10.3 `NOT NULL`

作用：禁止空值。

语法：

```sql
col_name data_type NOT NULL
```

### 10.4 `UNIQUE`

作用：要求值或值组唯一。

语法：

```sql
UNIQUE (col1, col2, ...)
```

### 10.5 `CHECK`

作用：要求每个元组满足某个条件。

语法：

```sql
CHECK (predicate)
```

例子：

```sql
salary NUMERIC(8,2),
CONSTRAINT minsalary CHECK (salary > 29000)
```

### 10.6 `CONSTRAINT`

作用：给约束命名，方便删除或管理。

语法：

```sql
CONSTRAINT constraint_name CHECK (...)
```

配合删除：

```sql
ALTER TABLE instructor DROP CONSTRAINT minsalary;
```

## 11. 索引语句

### 11.1 `CREATE INDEX`

作用：创建索引。

语法：

```sql
CREATE INDEX index_name
ON table_name (col1, col2, ...);
```

若希望索引键唯一：

```sql
CREATE UNIQUE INDEX index_name
ON table_name (col1, col2, ...);
```

### 11.2 `DROP INDEX`

作用：删除索引。

语法：

```sql
DROP INDEX index_name;
```

## 12. 授权与权限管理

### 12.1 `GRANT`

作用：授予用户或角色权限。

语法：

```sql
GRANT privilege_list
ON object_name
TO user_or_role_list;
```

例子：

```sql
GRANT SELECT ON department TO Amit, Satoshi;
GRANT UPDATE(budget) ON department TO Amit, Satoshi;
```

### 12.2 `WITH GRANT OPTION`

作用：允许被授权者继续把该权限授予别人。

语法：

```sql
GRANT SELECT
ON department
TO Amit
WITH GRANT OPTION;
```

### 12.3 `REVOKE`

作用：撤销权限。

语法：

```sql
REVOKE privilege_list
ON object_name
FROM user_or_role_list;
```

例子：

```sql
REVOKE SELECT ON department FROM Amit, Satoshi RESTRICT;
```

### 12.4 角色相关 `GRANT`

作用：把权限授予角色，或把角色授予用户/其他角色。

例子：

```sql
GRANT SELECT ON takes TO instructor;
GRANT instructor TO dean;
GRANT dean TO Satoshi;
```

### 12.5 `REFERENCES` 权限

作用：允许他人在建表时引用该表的列作为外键。

例子：

```sql
GRANT REFERENCES(dept_name) ON department TO Mariano;
```

## 13. 函数与存储过程

### 13.1 `CREATE FUNCTION`

作用：定义函数，返回一个值或一张表。

典型语法：

```sql
CREATE FUNCTION function_name(param_name param_type)
RETURNS return_type
BEGIN
    ...
END;
```

用途：

- 封装重复逻辑
- 在查询中复用

### 13.2 `CREATE PROCEDURE`

作用：定义过程，执行一组操作，可有输入/输出参数。

典型语法：

```sql
CREATE PROCEDURE procedure_name(...)
BEGIN
    ...
END;
```

特点：

- 更强调执行动作，不一定返回单个值
- 适合批量逻辑、封装更新过程

## 14. 触发器

### 14.1 `CREATE TRIGGER`

作用：在指定事件发生时自动执行某段 SQL 逻辑。

典型语法：

```sql
CREATE TRIGGER trigger_name
{BEFORE | AFTER} {INSERT | DELETE | UPDATE}
ON table_name
FOR EACH ROW
BEGIN
    ...
END;
```

常见触发时机：

- `BEFORE INSERT`
- `AFTER INSERT`
- `BEFORE DELETE`
- `AFTER DELETE`
- `BEFORE UPDATE`
- `AFTER UPDATE`

还可以限定更新某个属性：

```sql
AFTER UPDATE OF grade ON takes
```

常见用途：

- 检查复杂约束
- 自动更新统计值/派生值
- 防止非法更新

注意：

- 触发器执行是自动的。
- 滥用触发器会使系统逻辑难以追踪。

## 15. SQL 与程序接口中的常见调用

这部分不算纯 SQL 语句，但经常和 SQL 用法一起考。

### 15.1 JDBC `executeQuery()`

作用：执行查询语句（通常是 `SELECT`），返回结果集。

### 15.2 JDBC `executeUpdate()`

作用：执行非查询语句，如：

- `INSERT`
- `UPDATE`
- `DELETE`
- `CREATE`
- `DROP`

返回值通常是受影响的行数。

### 15.3 `PreparedStatement`

作用：预备语句，使用占位符 `?`，防止 SQL 注入并提高重复执行效率。

例子：

```sql
INSERT INTO instructor VALUES(?, ?, ?, ?)
```

## 16. 高频易错点

- `DROP TABLE` 删除的是表本身；`DELETE FROM table` 删除的是数据。
- `WHERE` 过滤的是分组前的行；`HAVING` 过滤的是分组后的组。
- 在 `SELECT` 中，非聚合列必须出现在 `GROUP BY` 中。
- 不能用 `= NULL`，必须用 `IS NULL`。
- `JOIN ... ON` 最通用，`NATURAL JOIN` 最省写但也最容易误连。
- 外连接里 `ON` 与 `WHERE` 的效果不同。
- `INSERT INTO ... SELECT ...` 是批量插入查询结果的常见写法。
- `WITH` 创建的是临时命名结果；`CREATE VIEW` 创建的是持久数据库对象。
- `CHECK` 检查的是谓词；`FOREIGN KEY` 检查的是参照完整性。
- `CREATE INDEX` 是物理优化语句，不改变逻辑查询结果。
- `GRANT ... WITH GRANT OPTION` 允许权限继续传递。
- 预备语句里的参数占位符是 `?`，参数编号从 `1` 开始。

