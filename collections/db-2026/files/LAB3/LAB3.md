# LAB3

## 1.定义三张表

```mysql
CREATE TABLE S (
    SID VARCHAR(10) PRIMARY KEY, -- 主键约束
    SNAME VARCHAR(50),
    AGE INT,
    SEX ENUM('f', 'm')
);
CREATE TABLE C (
    CID VARCHAR(10) PRIMARY KEY, -- 主键约束
    CNAME VARCHAR(100),
    TEACHER VARCHAR(50)
);
CREATE TABLE SC (
    SID VARCHAR(10),
    CID VARCHAR(10),
    GRADE INT,
    PRIMARY KEY (SID, CID), -- 主键约束
    FOREIGN KEY (SID) REFERENCES S(SID) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (CID) REFERENCES C(CID) ON DELETE CASCADE ON UPDATE CASCADE
);
```

![image-20260415173226590](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260415173226590.png)

## 2.完整性约束设置

### b) 为SC表添加外键，引用S的SID和C的CID，通过删除和修改SC表的数据测试on delete和on update的完整性；

```mysql
-- 插入测试数据
INSERT INTO S (SID, SNAME, AGE, SEX) VALUES ('001', '张三', 20, 'm');
INSERT INTO C (CID, CNAME, TEACHER) VALUES ('C01', '数据库', '李老师');
INSERT INTO SC (SID, CID, GRADE) VALUES ('001', 'C01', 85);
```

![image-20260415173613489](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260415173613489.png)

![image-20260415173624899](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260415173624899.png)

![image-20260415173636959](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260415173636959.png)

```mysql
-- 测试 ON UPDATE CASCADE
UPDATE S SET SID = '002' WHERE SID = '001';
SELECT * FROM SC;
```

![image-20260415173715042](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260415173715042.png)

```mysql
-- 测试 ON DELETE CASCADE
DELETE FROM S WHERE SID = '002';
SELECT * FROM SC;
```

![image-20260415173742548](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260415173742548.png)

### c) 测试 ENUM

```mysql
-- 正确插入
INSERT INTO S (SID, SNAME, AGE, SEX) VALUES ('003', '李四', 21, 'f');

-- 错误插入（会报错）
INSERT INTO S (SID, SNAME, AGE, SEX) VALUES ('004', '王五', 22, 'x');
```

![image-20260415173843969](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260415173843969.png)

![image-20260415173853319](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260415173853319.png)

### d) 测试 CHECK

```mysql
-- 添加 CHECK 约束
ALTER TABLE S ADD CONSTRAINT chk_age CHECK (AGE >= 0 AND AGE <= 200);

-- 正确插入
INSERT INTO S (SID, SNAME, AGE, SEX) VALUES ('005', '赵六', 25, 'm');

-- 错误插入（会报错）
INSERT INTO S (SID, SNAME, AGE, SEX) VALUES ('006', '孙七', -5, 'm');
```

![image-20260415174015350](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260415174015350.png)

![image-20260415174026043](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260415174026043.png)

### e) 定义 TRIGGER 实现年龄约束

```mysql
-- 删除之前的 CHECK
ALTER TABLE S DROP CONSTRAINT chk_age;

-- 创建触发器（BEFORE INSERT）
DELIMITER $$
CREATE TRIGGER trg_age_check_before_insert
BEFORE INSERT ON S
FOR EACH ROW
BEGIN
    IF NEW.AGE < 0 OR NEW.AGE > 200 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '年龄必须在 0 到 200 之间';
    END IF;
END$$

-- 创建触发器（BEFORE UPDATE）
CREATE TRIGGER trg_age_check_before_update
BEFORE UPDATE ON S
FOR EACH ROW
BEGIN
    IF NEW.AGE < 0 OR NEW.AGE > 200 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '年龄必须在 0 到 200 之间';
    END IF;
END$$
DELIMITER ;

-- 测试触发器
INSERT INTO S (SID, SNAME, AGE, SEX) VALUES ('007', '周八', 210, 'm'); -- 应报错
INSERT INTO S (SID, SNAME, AGE, SEX) VALUES ('008', '吴九', 30, 'f'); -- 正常
```

![image-20260415174154446](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260415174154446.png)

![image-20260415174206175](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260415174206175.png)

## 3.MySQL上的用户和权限的设置：

### a) root 创建用户并授权

```mysql
-- 创建用户
CREATE USER 'test1'@'localhost' IDENTIFIED BY 'password123';
CREATE USER 'test2'@'localhost' IDENTIFIED BY 'password123';

-- 授权（WITH GRANT OPTION 允许转授权）
GRANT UPDATE, INSERT ON C TO 'test1'@'localhost' WITH GRANT OPTION;
```

### b) 以 test1 登录并操作

```mysql
-- 查看权限
SHOW GRANTS;

-- 查询
SELECT * FROM C;

-- 授权给 test2
GRANT UPDATE ON C TO 'test2'@'localhost';
```

![image-20260415174658834](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260415174658834.png)

![image-20260415174754550](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260415174754550.png)

![image-20260415174812327](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260415174812327.png)

### c) root 撤销 test1 的 UPDATE 权限

```mysql
REVOKE UPDATE ON C FROM 'test1'@'localhost';

-- 查看 test2 权限
SHOW GRANTS FOR 'test2'@'localhost';
```

![image-20260415174858381](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260415174858381.png)

![image-20260415174909256](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260415174909256.png)

### d) root 删除 test2 用户

```mysql
DROP USER 'test2'@'localhost';
```

![image-20260415175006772](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260415175006772.png)

![image-20260415175050985](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260415175050985.png)