# LAB1

### MySQL 安装

>参考[Windows10 MYSQL Installer 安装（mysql-installer-community-5.7.19.0.msi） | 菜鸟教程](https://www.runoob.com/w3cnote/windows10-mysql-installer.html)

安装过程中，configurator卡在`Initializing database`，log提示`Failed to start process for MySQL Server 9.6.0.`，搜索后尝试

1. 系统设置 > 时间和语言 > 语言和区域 > Beta版：使用Unicode UTF-8提供全球语言支持
2. 删除后下载zip手动安装

均无效，最后下载了`Microsoft Visual C++ Redistributable v14`（[Latest supported Visual C++ Redistributable downloads | Microsoft Learn](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist?view=msvc-170#latest-supported-redistributable-version)）后解决。

![image-20260305195013727](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260305195013727.png)

### MySQL Workbench 安装

>参考[MySQL-Workbench使用 - 简书](https://www.jianshu.com/p/bba859635ae4)

一切顺利

### 熟悉MySQL

#### · 创建、删除、选择数据库

```mysql
CREATE DATABASE [IF NOT EXISTS] <database_name>
  [CHARACTER SET charset_name]
  [COLLATE collation_name];

mysqladmin -u <your username> -p create <database name> \
  --default-character-set=utf8mb4 \
  --default-collation=utf8mb4_general_ci
```

![image-20260305201152508](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260305201152508.png)

```mysql
DROP DATABASE [IF EXISTS] <database_name>;

mysqladmin -u <your_username> -p drop <your_database>
```

![image-20260305201040824](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260305201040824.png)

```mysql
USE database_name;
mysql -u <your_username> -p -D <your_database>
```

![image-20260305201249818](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260305201249818.png)

#### · 数据类型

##### 数值类型

| 类型         | 大小                                     | 范围（有符号）                                               | 范围（无符号）                                               | 用途            |
| :----------- | :--------------------------------------- | :----------------------------------------------------------- | :----------------------------------------------------------- | :-------------- |
| TINYINT      | 1 Bytes                                  | (-128，127)                                                  | (0，255)                                                     | 小整数值        |
| SMALLINT     | 2 Bytes                                  | (-32 768，32 767)                                            | (0，65 535)                                                  | 大整数值        |
| MEDIUMINT    | 3 Bytes                                  | (-8 388 608，8 388 607)                                      | (0，16 777 215)                                              | 大整数值        |
| INT或INTEGER | 4 Bytes                                  | (-2 147 483 648，2 147 483 647)                              | (0，4 294 967 295)                                           | 大整数值        |
| BIGINT       | 8 Bytes                                  | (-9,223,372,036,854,775,808，9 223 372 036 854 775 807)      | (0，18 446 744 073 709 551 615)                              | 极大整数值      |
| FLOAT        | 4 Bytes                                  | (-3.402 823 466 E+38，-1.175 494 351 E-38)，0，(1.175 494 351 E-38，3.402 823 466 351 E+38) | 0，(1.175 494 351 E-38，3.402 823 466 E+38)                  | 单精度 浮点数值 |
| DOUBLE       | 8 Bytes                                  | (-1.797 693 134 862 315 7 E+308，-2.225 073 858 507 201 4 E-308)，0，(2.225 073 858 507 201 4 E-308，1.797 693 134 862 315 7 E+308) | 0，(2.225 073 858 507 201 4 E-308，1.797 693 134 862 315 7 E+308) | 双精度 浮点数值 |
| DECIMAL      | 对DECIMAL(M,D) ，如果M>D，为M+2否则为D+2 | 依赖于M和D的值                                               | 依赖于M和D的值                                               | 小数值          |

##### 日期和时间类型

| 类型      | 大小 ( bytes) | 范围                                                         | 格式                | 用途                     |
| :-------- | :------------ | :----------------------------------------------------------- | :------------------ | :----------------------- |
| DATE      | 3             | 1000-01-01/9999-12-31                                        | YYYY-MM-DD          | 日期值                   |
| TIME      | 3             | '-838:59:59'/'838:59:59'                                     | HH:MM:SS            | 时间值或持续时间         |
| YEAR      | 1             | 1901/2155                                                    | YYYY                | 年份值                   |
| DATETIME  | 8             | '1000-01-01 00:00:00' 到 '9999-12-31 23:59:59'               | YYYY-MM-DD hh:mm:ss | 混合日期和时间值         |
| TIMESTAMP | 4             | '1970-01-01 00:00:01' UTC 到 '2038-01-19 03:14:07' UTC结束时间是第 **2147483647** 秒，北京时间 **2038-1-19 11:14:07**，格林尼治时间 2038年1月19日 凌晨 03:14:07 | YYYY-MM-DD hh:mm:ss | 混合日期和时间值，时间戳 |

##### 字符串类型

| 类型       | 大小                  | 用途                            |
| :--------- | :-------------------- | :------------------------------ |
| CHAR       | 0-255 bytes           | 定长字符串                      |
| VARCHAR    | 0-65535 bytes         | 变长字符串                      |
| TINYBLOB   | 0-255 bytes           | 不超过 255 个字符的二进制字符串 |
| TINYTEXT   | 0-255 bytes           | 短文本字符串                    |
| BLOB       | 0-65 535 bytes        | 二进制形式的长文本数据          |
| TEXT       | 0-65 535 bytes        | 长文本数据                      |
| MEDIUMBLOB | 0-16 777 215 bytes    | 二进制形式的中等长度文本数据    |
| MEDIUMTEXT | 0-16 777 215 bytes    | 中等长度文本数据                |
| LONGBLOB   | 0-4 294 967 295 bytes | 二进制形式的极大文本数据        |
| LONGTEXT   | 0-4 294 967 295 bytes | 极大文本数据                    |

##### 枚举与集合类型

- **ENUM**: 枚举类型，用于存储单一值，可以选择一个预定义的集合。
- **SET**: 集合类型，用于存储多个值，可以选择多个预定义的集合。

##### 空间数据类型

GEOMETRY, POINT, LINESTRING, POLYGON, MULTIPOINT, MULTILINESTRING, MULTIPOLYGON, GEOMETRYCOLLECTION: 用于存储空间数据（地理信息、几何图形等）。



#### · 创建、删除数据表

```mysql
CREATE TABLE table_name (
    column1 datatype,
    column2 datatype,
    ...
);
```

![image-20260305201733436](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260305201733436.png)

```mysql
DROP TABLE [IF EXISTS] table_name;

TRUNCATE TABLE table_name; -- 只清空表中的数据
```

![image-20260305201903516](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260305201903516.png)

#### · 插入、查询、更新、删除数据

```mysql
-- 插入
INSERT INTO table_name (column1, column2, column3, ...)
VALUES (value1, value2, value3, ...); -- 如果你要插入所有列的数据，可以省略列名
-- 查询
SELECT column1, column2, ...
FROM table_name
[WHERE condition]
[ORDER BY column_name [ASC | DESC]]
[LIMIT number];
-- 更新
UPDATE table_name
SET column1 = value1, column2 = value2, ...
WHERE condition;
-- 删除
DELETE FROM table_name
WHERE condition;
```

<img src="C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260305202756799.png" alt="image-20260305202756799" style="zoom:50%;" />