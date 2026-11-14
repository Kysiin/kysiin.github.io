# HW6

## 5.6

```sql
create view branch_cust as
    select branch_name, customer_name
    from depositor, account
    where depositor.account_number = account.account_number
```

### 触发器 for `depositor` 表插入

当向 `depositor` 表插入新记录时，如果对应的 `account` 存在，则向物化视图插入一行。

```sql
create trigger maintain_branch_cust_on_depositor_insert
after insert on depositor
for each row
begin
    insert into branch_cust (branch_name, customer_name)
    select branch_name, new.customer_name
    from account
    where account.account_number = new.account_number;
end;
```

### 触发器 for `account` 表插入

当向 `account` 表插入新记录时，如果对应的 `depositor` 存在，则向物化视图插入一行。

```sql
create trigger maintain_branch_cust_on_account_insert
after insert on account
for each row
begin
    insert into branch_cust (branch_name, customer_name)
    select new.branch_name, customer_name
    from depositor
    where depositor.account_number = new.account_number;
end;
```

## 5.15

### 函数 `avg_salary`

```sql
create function avg_salary(c_name varchar(20))
returns numeric(10,2)
deterministic
reads sql data
begin
    declare avg_sal numeric(10,2);

    select avg(salary) into avg_sal
    from works
    where company_name = c_name;

    return avg_sal;
end;
```

### 查询：找出平均工资高于 "First Bank" 的公司

```sql
select distinct company_name
from works
group by company_name
having avg(salary) > avg_salary('First Bank');
```

## 5.19

```sql
create trigger cascade_delete_from_s
after delete on s
for each row
begin
    delete from r
    where r.B = old.A;
end;
```

- 触发器在 `s` 表的每一行被删除后执行。
- `old.A` 包含被删除行的主键值。
- 删除 `r` 表中所有 `B = old.A` 的行，即引用被删除主键的外键行。
