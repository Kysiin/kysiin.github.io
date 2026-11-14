# LAB2

## 1.建立数据库

```mysql
CREATE DATABASE school;
```

---

## 2.数据的定义

### 使用 `CREATE TABLE`命令创建数据表。

```mysql
CREATE TABLE S(
	SID varchar(10),  	#学号是变长字符串
    SNAME varchar(20), 	#学生姓名是变长字符串
    AGE int,	#年龄是数字
    SEX varchar(1)
);

CREATE TABLE SC(
	SID varchar(10),
    CID varchar(10),
    GRADE int
);

CREATE TABLE C(
	CID varchar(10),
    CNAME varchar(30),
    TEACHER varchar(20)
);
```

![image-20260325194535382](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260325194535382.png)

### 使用`ALTER`命令增加主键和外键

```mysql
ALTER TABLE S
ADD PRIMARY KEY (SID);

ALTER TABLE SC
ADD PRIMARY KEY (SID,CID); 	#复合主键

ALTER TABLE C
ADD PRIMARY KEY (CID);

ALTER TABLE SC
ADD FOREIGN KEY (SID)
REFERENCES S (SID);	#SID来自表S
ALTER TABLE SC
ADD FOREIGN KEY (CID)
REFERENCES C (CID);	#CID来自表C
```

![image-20260325194550325](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260325194550325.png)

### 用`INSERT`命令插入数据

```mysql
INSERT INTO S
VALUES
	('S1' , 'Wang feng', 20 , 'M'),
	('S2' , 'Liu fang' , 19 , 'M'),
	('S3' , 'Chen yun' , 22 , 'M'),
	('S4' , 'Wu kai' , 19 , 'M'),
	('S5' , 'Liu li' , 21 , 'F'),
	('S6' , 'Dong qing' , 18 , 'F');

INSERT INTO C
VALUES
	('C2' , 'maths' , 'Ma'),
	('C4' , 'physics' , 'Shi'),
	('C3' , 'chemisitry' , 'Zhou'),
	('C1' , 'DB' , 'Li'),
	('C5' , 'OS' , 'Wen');

INSERT INTO SC
VALUES
	('S1' , 'C1' , 70),
	('S2' , 'C1' , 81),
	('S3' , 'C1' , 92),
	('S4' , 'C1' , 85),
	('S1' , 'C2' , 65),
	('S2' , 'C3' , 57),
	('S3' , 'C5' , 87);
```

![image-20260325195328293](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260325195328293.png)

---

## 3.数据查询

### 单表查询

#### a) 查询全体学生的姓名、年龄；

```mysql
SELECT SNAME , AGE
FROM S;
```

![image-20260325195620643](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260325195620643.png)

#### b) 查询所有选修过课的学生的学号；

```mysql
SELECT SID
FROM S
WHERE SID IN (
	SELECT SID
    FROM SC
);	#选择所有SID在 SC的SID 中出现过的学生的学号
```

![image-20260325200307029](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260325200307029.png)

#### c) 查询考试成绩低于60分的学生的学号；

```mysql
SELECT SID
FROM S
WHERE SID IN (
	SELECT SID
    FROM SC
    WHERE GRADE < 60
);	#查询所有在 SC中GRADE低于60的SID 中出现过的 SID
```

![image-20260325200626901](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260325200626901.png)

#### d) 查询年龄在20至23之间的学生姓名、性别和年龄；

```mysql
SELECT SNAME , SEX , AGE
FROM S
WHERE AGE BETWEEN 20 AND 23;
```

![image-20260325200923816](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260325200923816.png)

#### e) 查询所有姓liu的学生的学号、姓名和年龄；

```mysql
SELECT SID , SNAME , AGE
FROM S
WHERE SNAME LIKE 'Liu%';	#第一个字为'Liu'
```

![image-20260325201150702](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260325201150702.png)

#### f) 查询学习C1课程的学生最高分数；

```mysql
SELECT GRADE
FROM SC
WHERE GRADE >= ALL (
	SELECT GRADE
    FROM SC
);	#选择 大于等于所有GRADE 的GRADE
```

![image-20260325201535573](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260325201535573.png)

#### g) 查询各个课程号与相应的选课人数；

```mysql
SELECT CID ，COUNT(SID) AS S_COUNT
FROM SC
GROUP BY CID;	#根据课程ID分组
```

![image-20260325202702335](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260325202702335.png)

#### h) 查询选修C3课程的学生的姓名；

```mysql
SELECT SNAME
FROM S
WHERE SID IN (
	SELECT SID
    FROM SC
    WHERE CID = 'C3'
);
```

![image-20260325202829659](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260325202829659.png)

#### i) 查询选修C1课程且成绩在90分以上的所有学生姓名。

```mysql
SELECT SNAME
FROM S
WHERE SID IN (
	SELECT SID
    FROM SC
    WHERE CID = 'C1' AND GRADE > 90
);
```

![image-20260325202957025](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260325202957025.png)

#### j) 查询每一门课程的平均成绩

```mysql
SELECT AVG(GRADE) AS AVG_GRADE
FROM SC
GROUP BY CID;
```

![image-20260325203207904](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260325203207904.png)

#### k) 查询授课教师名字中包括i的课程名

```mysql
SELECT CID
FROM C
WHERE TEACHER LIKE '%i%'; #'任意字符i任意字符'
```

![image-20260325203306762](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260325203306762.png)

#### l) 查询课程成绩在80～90的学生编号、课程编号

```mysql
SELECT SID , CID
FROM SC
WHERE GRADE BETWEEN 80 AND 90;
```

![image-20260325203405577](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260325203405577.png)

### 多表查询

#### m) 查询最高成绩为80以上的课程名、最高成绩

```mysql
SELECT C.CNAME , MAX(SC.GRADE) AS HIGHEST_GRADE
FROM SC
JOIN C ON SC.CID = C.CID
GROUP BY C.CID , C.NAME
HAVING MAX(SC.GRADE) > 80;
```

![image-20260325203733475](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260325203733475.png)

### 嵌套查询

#### n） 查询c1课程在平均分以上的学生信息

```mysql
SELECT S.*, SC.GRADE
FROM S
JOIN SC ON S.SID = SC.SID
WHERE SC.CID = 'C1'
  AND SC.GRADE > (
    SELECT AVG(GRADE)
    FROM SC
    WHERE CID = 'C1'
  );
```

![image-20260325203934198](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260325203934198.png)

---

## 4.视图使用

### 创建视图

```mysql
CREATE VIEW S_C_SC AS
SELECT S.SID AS 学号,
       S.SNAME AS 姓名,
       C.CNAME AS 课程名,
       SC.GRADE AS 成绩
FROM S
JOIN SC ON S.SID = SC.SID
JOIN C ON SC.CID = C.CID;
```

### 查询姓Wu的各门课程成绩

```mysql
SELECT 学号, 姓名, 课程名, 成绩
FROM S_C_SC
WHERE 姓名 LIKE 'Wu%';
```

![image-20260325204605776](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260325204605776.png)

### 修改视图中的数据观察视图和原关系表中的变化

```mysql
UPDATE S_C_SC
SET 成绩 = 100
WHERE 学号 = 'S1' AND 课程名 = 'DB';
```

![image-20260325204833490](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260325204833490.png)

![image-20260325204906258](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260325204906258.png)

可以看到原关系表中学号'S1'的同学的'DB'课程成绩也被修改为了100，说明修改视图中的数据会直接影响原表

### 删除视图

使用`DROP VIEW S_C_SC;`指令删除视图

---

## 5.索引的使用

```mysql
CREATE INDEX INDEX_CID ON C(CID);	#创建索引

SELECT CID
FROM C
WHERE TEACHER LIKE '%i%'; #'任意字符i任意字符';

DROP INDEX INDEX_CID ON C;
```

数据库太小，每个查询都是0.000sec的Duration和Fetch，但理论上，索引会加快查询的速度。

---

## 6.数据更新

### a) 用update命令修改c表中课程号为C3的课程的课程号修改为C6

```mysql
#UPDATE C
#SET CID = 'C6'
#WHERE CID = 'C3';
```

由于`C.CID`是`SC.CID`的`parent row`，直接修改会报错。

![image-20260325211150588](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260325211150588.png)

```mysql
ALTER TABLE SC DROP FOREIGN KEY SC_ibfk_2;	#删除外键

ALTER TABLE SC
ADD FOREIGN KEY (CID) REFERENCES C(CID)
ON UPDATE CASCADE;	#重新添加带有级联更新的外键约束

UPDATE C
SET CID = 'C6'
WHERE CID = 'C3';
```

修改成功

![image-20260325211332368](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260325211332368.png)

### b) 用update命令修改sc表中课由“Li”任课的课程号为由“Wen”任课的课程号

```mysql
SET @li_cid = (SELECT CID FROM C WHERE TEACHER = 'Li' LIMIT 1);
SET @wen_cid = (SELECT CID FROM C WHERE TEACHER = 'Wen' LIMIT 1);

UPDATE SC
SET CID = @wen_cid
WHERE CID = @li_cid;
```

由于该行为会导致表中出现两个`S3-C5`，且`(SID,CID)`是复合主键，因此会报错`Duplicate entry 'S3-C5' for key 'sc.PRIMARY'`

可以保留原记录

```mysql
UPDATE SC
SET CID = CASE
    WHEN CID = @li_cid AND EXISTS (
        SELECT 1 FROM (SELECT SID, CID FROM SC) AS SC2
        WHERE SC2.SID = SC.SID AND SC2.CID = @wen_cid
    ) THEN CID		#如果原来有一样的则保留原来的
    WHEN CID = @li_cid THEN @wen_cid
    ELSE CID
END
WHERE CID = @li_cid OR CID = @wen_cid;
```

![image-20260327130519010](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260327130519010.png)

### c) 用delete命令删除表sc中分数在60以下的记录

```mysql
DELETE FROM SC
WHERE (SID, CID) IN (
    SELECT SID, CID FROM (SELECT SID, CID FROM SC WHERE GRADE < 60) AS temp
);
```

![image-20260327131117988](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260327131117988.png)

### d) 用delete命令删除表sc中课程名为“OS”的记录。

```mysql
DELETE FROM SC
WHERE CID IN (SELECT CID FROM C WHERE CNAME = 'OS');
```

![image-20260327131221942](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260327131221942.png)

---

## 7.删除三张关系表和数据库

![image-20260327131331110](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260327131331110.png)
