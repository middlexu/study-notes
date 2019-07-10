### MySQL的安装

MySQL版本：
	5.x:
	5.0-5.1:早期产品的延续，升级维护
	5.4 - 5.x :  MySQL整合了三方公司的新存储引擎 （**推荐5.7**）



#### RPM包安装

安装前，我们可以检测系统是否自带安装 MySQL:

`rpm -qa | grep mysql`

如果你系统有安装，那可以选择进行卸载:

```shell
rpm -e mysql　　// 普通删除模式
rpm -e --nodeps mysql　　// 强力删除模式，如果使用上面命令删除时，提示有依赖的其它文件，则用该命令可以对其进行强力删除
```



下载地址
	https://dev.mysql.com/get/Downloads/MySQL-5.5/mysql-5.5.58-1.el6.x86_64.rpm-bundle.tar

自己已经在坚果云上保存了



参考这个网站的安装https://www.cnblogs.com/subtract/p/6473207.html

安装：`rpm -ivh rpm软件名`
如果安装时 与某个软件  xxx冲突，则需要将冲突的软件卸载掉：
	yum -y remove xxx
安装时 有日志提示我们可以修改密码：`/usr/bin/mysqladmin -u root password 'new-password'`

注意： 
	如果提示“GPG keys...”安装失败，解决方案：
		`rpm -ivh rpm软件名  --force --nodeps`
	
验证：
`mysqladmin --version`

启动mysql应用： `service mysql start`
关闭： `service mysql stop`
重启： `service mysql restart`

在计算机reboot后（reboot之后才能给管理员增加密码） 登陆MySQL :  mysql
可能会报错：   "/var/lib/mysql/mysql.sock不存在"  

--原因：是Mysql服务没有启动
解决 ：  启动服务： 1.每次使用前 手动启动服务   /etc/init.d/mysql start
	  	 2.开机自启   chkconfig mysql on     ,  chkconfig mysql off    

​	检查开机是否自动启动： ntsysv		
​	
给mysql 的超级管理员root 增加密码：`/usr/bin/mysqladmin -u root password root`
​				
登陆：
`mysql -u root -p`



#### MySQL的配置

数据库存放目录：
ps -ef|grep mysql  可以看到：
	数据库目录：     datadir=/var/lib/mysql 
	pid文件目录： --pid-file=/var/lib/mysql/bigdata01.pid



MySQL核心目录：
	/var/lib/mysql :mysql 安装目录
	/usr/share/mysql:  配置文件
	/usr/bin：命令目录（mysqladmin、mysqldump等）
	/etc/init.d/mysql启停脚本

MySQL配置文件
	my-huge.cnf	高端服务器  1-2G内存
	my-large.cnf   中等规模
	my-medium.cnf  一般
	my-small.cnf   较小
	但是，以上配置文件mysql默认不能识别，默认只能识别 /etc/my.cnf
	采用 my-huge.cnf ：
	cp /usr/share/mysql/my-huge.cnf /etc/my.cnf
	注意：mysql5.5默认配置文件/etc/my.cnf；Mysql5.6 默认配置文件/etc/mysql-default.cnf
		
默认端口3306
mysql字符编码：
	sql  :  show variables like '%char%' ;
	可以发现部分编码是 latin,**需要统一设置为utf-8**
	设置编码：

```shell
vim /etc/my.cnf      ###增加下面配置
[mysql]
default-character-set=utf8
[client]
default-character-set=utf8

[mysqld]
character_set_server=utf8
character_set_client=utf8
collation_server=utf8_general_ci
```



添加远程访问

```mysql
mysql> GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' IDENTIFIED BY 'root' WITH GRANT OPTION; 
Query OK, 0 rows affected (0.00 sec)
```



重启Mysql:  `service mysql restart`
	sql  :  show variables like '%char%' ;
注意事项：修改编码 只对“之后”创建的数据库生效，因此 我们**建议在mysql安装完毕后，第一时间统一编码**。

mysql:清屏    ctrl+L    , system clear





### 数据库的操作



#### 查看各种信息

```mysql
mysql> show databases;###查看数据库
+--------------------+
| Database           |
+--------------------+
| information_schema |
| mysql              |
| performance_schema |
| test               |
+--------------------+
4 rows in set (0.00 sec)

mysql> use mysql;###切换到mysql数据库，之后的操作在这个数据库中
Database changed
mysql> show tables;###查看所有表
...  #数据太多省略
24 rows in set (0.00 sec)

mysql> show columns from user#显示数据表的属性，属性类型，主键信息 ，是否为 NULL，默认值等其他信息。
...
42 rows in set (0.00 sec)

mysql> show index from user;###显示数据表的详细索引信息
...
2 rows in set (0.00 sec)

mysql> describe user;###获取表结构信息

mysql> show table status from mysql;###该命令将输出mysql数据库管理系统的性能及统计信息。
#这里的mysql指的是数据库的名字，不是表名
mysql> SHOW TABLE STATUS from mysql LIKE 'time%';     # 表名以runoob开头的表的信息
mysql> SHOW TABLE STATUS from mysql LIKE 'time%'\G;   # 加上\G，查询结果按列打印
```

**加上\G，查询结果按列打印**



#### MySQL用户设置

如果你需要添加 MySQL 用户，你只需要在 mysql 数据库中的 user 表添加新用户即可。

以下为添加用户的的实例，用户名为guest，密码为guest123，并授权用户可进行 SELECT, INSERT 和 UPDATE操作权限：

```sql
[root@localhost ~]# mysql -u root -p
Enter password:*******
mysql> use mysql;
Database changed

mysql> INSERT INTO user 
          (host, user, password, 
           select_priv, insert_priv, update_priv) 
           VALUES ('localhost', 'guest', 
           PASSWORD('guest123'), 'Y', 'Y', 'Y');
Query OK, 1 row affected (0.20 sec)

mysql> FLUSH PRIVILEGES;
Query OK, 1 row affected (0.01 sec)

mysql> SELECT host, user, password FROM user WHERE user = 'guest';
+-----------+---------+------------------+
| host      | user    | password         |
+-----------+---------+------------------+
| localhost | guest | 6f8c114b58f2ce9e |
+-----------+---------+------------------+
1 row in set (0.00 sec)
```



另外一种添加用户的方法为通过SQL的 GRANT 命令，以下命令会给指定数据库TUTORIALS添加用户 zara ，密码为 zara123 。

```sql
[root@localhost ~]# mysql -u root -p
Enter password:*******
mysql> use mysql;
Database changed

mysql> GRANT SELECT,INSERT,UPDATE,DELETE,CREATE,DROP
    -> ON TUTORIALS.*
    -> TO 'zara'@'localhost'
    -> IDENTIFIED BY 'zara123';
```





#### 创建数据库

```sql
mysql> create DATABASE RUNOOB;
```



#### 删除数据库

```sql
mysql> drop database RUNOOB;
```



#### 选择数据库

```sql
mysql> drop database RUNOOB;
```









### 数据表的操作



#### 表的创建

```sql
CREATE TABLE IF NOT EXISTS `runoob_tbl`(
   `runoob_id` INT UNSIGNED AUTO_INCREMENT,
   `runoob_title` VARCHAR(100) NOT NULL,
   `runoob_author` VARCHAR(40) NOT NULL,
   `submission_date` DATE,
   PRIMARY KEY ( `runoob_id` )     ###最后没有逗号
)ENGINE=InnoDB DEFAULT CHARSET=utf8;
```



```sql
create table demo.ChineseCharInfo
(
    ID        int     not null     auto_increment,
    Hanzi     varchar(10)     not null,
    primary key (ID)
)
engine=innodb auto_increment=1 default charset=utf8 collate=utf8_general_ci;

create table demo.ChinesePinyinInfo
(
    ID     int     not null     auto_increment,
    CharID     int     null,
    Pinyin varchar(10)     null,
    Tone tinyint unsigned     null,
    primary key (ID),
    


-- 方式一：不指定外键名称，数据库自动生成
foreign key (CharID) references ChineseCharInfo(ID) on delete cascade on update cascade 

-- 方式二：指定外键名称为(FK_Name)
-- constraint FK_Name foreign key (CharID) references ChineseCharInfo(ID) on delete cascade on update cascade 


)
engine=innodb auto_increment=1 default charset=utf8 collate=utf8_general_ci;
```





#### 表的删除

```sql
DROP TABLE runoob_tbl;
```



#### 表的修改

##### 字段的删除

```sql
mysql> ALTER TABLE testalter_tbl  DROP i;
```

##### 字段的添加

```sql
mysql> ALTER TABLE testalter_tbl ADD i INT;
```

如果你需要指定新增字段的位置，可以使用MySQL提供的关键字 FIRST (设定位第一列)， AFTER 字段名（设定位于某个字段之后）。

```sql
ALTER TABLE testalter_tbl DROP i;
ALTER TABLE testalter_tbl ADD i INT FIRST;
ALTER TABLE testalter_tbl DROP i;
ALTER TABLE testalter_tbl ADD i INT AFTER c;
```

##### 修改字段类型及名称

```sql
mysql> ALTER TABLE testalter_tbl MODIFY c CHAR(10);
```

使用 CHANGE 子句, 语法有很大的不同。 在 CHANGE 关键字之后，紧跟着的是你要修改的字段名，然后指定新字段名及类型。

```sql
mysql> ALTER TABLE testalter_tbl CHANGE i j BIGINT;
```

对字段做其它设定

```sql
mysql> ALTER TABLE testalter_tbl  MODIFY j BIGINT NOT NULL DEFAULT 100;
```

如果你不设置默认值，MySQL会自动设置该字段默认为 NULL。

```sql
mysql> ALTER TABLE testalter_tbl ALTER i SET DEFAULT 1000;
```

##### 修改表名

```sql
mysql> ALTER TABLE testalter_tbl RENAME TO alter_tbl;
```



##### 建立索引

```sql
1.添加PRIMARY KEY（主键索引） 
mysql>ALTER TABLE `table_name` ADD PRIMARY KEY ( `column` ) 
2.添加UNIQUE(唯一索引) 
mysql>ALTER TABLE `table_name` ADD UNIQUE ( `column` ) 
3.添加INDEX(普通索引) 
mysql>ALTER TABLE `table_name` ADD INDEX index_name ( `column` ) 
4.添加FULLTEXT(全文索引) 
mysql>ALTER TABLE `table_name` ADD FULLTEXT ( `column`) 
5.添加多列索引 
mysql>ALTER TABLE `table_name` ADD INDEX index_name ( `column1`, `column2`, `column3` )
```



##### 显示索引信息

```sql
mysql> SHOW INDEX FROM table_name; \G
```



##### 建立外键

```sql
-- 为表(demo.ChinesePinyinInfo)中字段(CharID)添加外键，并指定外键名为(FK_Name)
alter table demo.ChinesePinyinInfo add constraint FK_Name foreign key (CharID) references ChineseCharInfo(ID);

-- 为表(demo.ChinesePinyinInfo)中字段(CharID)添加外键，不指定外键名，由数据库自动生成外键名
alter table demo.ChinesePinyinInfo add foreign key (CharID) references ChineseCharInfo(ID) on delete cascade on update cascade;
```

##### 删除外键

```sql
-- 删除表(demo.ChinesePinyinInfo)中的名称为(FK_Name)的外键
alter table demo.ChinesePinyinInfo drop foreign key FK_Name;
```

##### 主外键关系的约束

如果子表试图创建一个在主表中不存在的外键值，数据库会拒绝任何insert或update操作。

如果主表试图update或者delete任何子表中存在或匹配的外键值，最终动作取决于外键约束定义中的on delete和on update选项。

on delete和on update都有下面四种动作。

- cascade：主表删除或更新相应的数据行，则子表同时删除或更新与主表相匹配的行，即级联删除、更新。
- set null：主表删除或更新相应的数据和，则子表同时将与主表相匹配的行的外键列置为null。当外键列被设置为not null时无效。
- no action：数据库拒绝删除或更新主表。
- restrict：数据库拒绝删除或更新主表。如果未指定on delete或on update的动作，则on delete或on update的默认动作就为restrict。





### 数据的操作

#### 插入数据

```sql
INSERT INTO table_name ( field1, field2,...fieldN )
                       VALUES
                       ( value1, value2,...valueN );
```



```sql
INSERT INTO table_name  (field1, field2,...fieldN)  VALUES  (valueA1,valueA2,...valueAN),(valueB1,valueB2,...valueBN),(valueC1,valueC2,...valueCN)......;
```





如果所有的列都要添加数据可以不规定列进行添加数据：

```sql
mysql> INSERT INTO runoob_tbl
    -> VALUES
    -> (0, "JAVA 教程", "RUNOOB.COM", '2016-05-06');
```

第一列如果没有设置主键自增（PRINARY KEY AUTO_INCREMENT）的话添加第一列数据比较容易错乱，要不断的查询表看数据。

如果添加过主键自增（PRINARY KEY AUTO_INCREMENT）第一列在增加数据的时候，可以写为0或者null，这样添加数据可以自增， 从而可以添加全部数据，而不用特意规定那几列添加数据。





#### 删除数据

```sql
删除 id 为 3 的行: delete from students where id=3;
删除所有年龄小于 21 岁的数据: delete from students where age<20;
删除表中的所有数据: delete from students;
```



#### delete，drop，truncate 区别

- delete 和 truncate 仅仅删除表数据，drop 连表数据和表结构一起删除
- delete 是 DML 语句，操作完以后如果没有不想提交事务还可以回滚，truncate 和 drop 是 DDL 语句，操作完马上生效，不能回滚
- 执行的速度上，drop>truncate>delete
- delete会保留自增的序号，truncate重头开始计数

```sql
mysql> select * from students;
+----+--------+
| id | name   |
+----+--------+
|  1 | 张三   |
|  2 | 李四   |
+----+--------+
2 rows in set (0.00 sec)

mysql> delete from students;
Query OK, 2 rows affected (0.00 sec)

mysql> insert into students values(null,'王五');
Query OK, 1 row affected (0.00 sec)

mysql> select * from students;
+----+--------+
| id | name   |
+----+--------+
|  3 | 王五   |
+----+--------+
1 row in set (0.00 sec)

mysql> truncate students;
Query OK, 0 rows affected (0.00 sec)

mysql> select * from students;
Empty set (0.00 sec)

mysql> insert into students values (null,'赵六');
Query OK, 1 row affected (0.01 sec)

mysql> select * from students;
+----+--------+
| id | name   |
+----+--------+
|  1 | 赵六   |
+----+--------+
1 row in set (0.00 sec)

```





#### 更改数据

```sql
UPDATE table_name SET field1=new-value1, field2=new-value2 [WHERE Clause]
```

```sql
将所有人的年龄增加 1: update students set age=age+1;
```





#### 查询数据

查询数据通用的 SELECT 语法：

```sql
SELECT column_name,column_name
FROM table_name
[WHERE Clause]
GROUP BY ...
HAVING ...
[LIMIT N][ OFFSET M]
```





#### LIKE匹配

like 匹配/模糊匹配，会与 **%** 和 **_** 结合使用。

```
'%a'     //以a结尾的数据
'a%'     //以a开头的数据
'%a%'    //含有a的数据
'_a_'    //三位且中间字母是a的
'_a'     //两位且结尾字母是a的
'a_'     //两位且开头字母是a的
```

查询以 java 字段开头的信息。

```sql
SELECT * FROM position WHERE name LIKE 'java%';
```

查询包含 java 字段的信息。

```sql
SELECT * FROM position WHERE name LIKE '%java%';
```

查询以 java 字段结尾的信息。

```sql
SELECT * FROM position WHERE name LIKE '%java';
```





#### UNION

将两个表的数据 上下叠放在一起

列数和字段类型要匹配不匹配的最好转化下



**UNION 语句**：用于将不同表中相同列中查询的数据展示出来；（不包括重复数据）

**UNION ALL 语句**：用于将不同表中相同列中查询的数据展示出来；（包括重复数据）

使用形式如下：

```sql
SELECT 列名称 FROM 表名称 UNION SELECT 列名称 FROM 表名称 ORDER BY 列名称；
SELECT 列名称 FROM 表名称 UNION ALL SELECT 列名称 FROM 表名称 ORDER BY 列名称；
```





#### JOIN

- **INNER JOIN**：如果表中有至少一个匹配，则返回行（join就是指inner join）
- **LEFT JOIN**：即使右表中没有匹配，也从左表返回所有的行
- **RIGHT JOIN**：即使左表中没有匹配，也从右表返回所有的行
- **FULL JOIN**：只要其中一个表中存在匹配，则返回行



```sql
SELECT Websites.name, access_log.count, access_log.date
FROM Websites
INNER JOIN access_log
ON Websites.id=access_log.site_id
ORDER BY access_log.count;
```





#### ORDER BY

```sql
SELECT field1, field2,...fieldN table_name1, table_name2...
ORDER BY field1, [field2...] [ASC [DESC]]
```





#### GROUP BY

```sql
SELECT column_name, function(column_name)
FROM table_name
WHERE column_name operator value
GROUP BY column_name;
```





#### exists和not exists

**exists**       （sql       返回结果集，为真）

**not exists**       (sql       不返回结果集，为真） 



```sql
表A 
ID   NAME
1       A1 
2       A2 
3       A3 

表B 
ID   AID   NAME 
1       1       B1 
2       2       B2 
3       2       B3 

表A和表B是１对多的关系   A.ID   =>   B.AID 
```



```sql
mysql-> SELECT   ID,NAME   FROM   A   WHERE   EXIST   (SELECT   *   FROM   B   WHERE   A.ID=B.AID) 
执行结果为 
1       A1 
2       A2 

原因可以按照如下分析 
SELECT   ID,NAME   FROM   A   WHERE   EXISTS   (SELECT   *   FROM   B   WHERE   B.AID=１) 
---> SELECT   *   FROM   B   WHERE   B.AID=１有值，返回真，所以有数据

SELECT   ID,NAME   FROM   A   WHERE   EXISTS   (SELECT   *   FROM   B   WHERE   B.AID=2) 
---> SELECT   *   FROM   B   WHERE   B.AID=２有值，返回真，所以有数据

SELECT   ID,NAME   FROM   A   WHERE   EXISTS   (SELECT   *   FROM   B   WHERE   B.AID=3) 
---> SELECT   *   FROM   B   WHERE   B.AID=３无值，返回假，所以没有数据

NOT   EXISTS   就是反过来 
SELECT   ID,NAME   FROM   A   WHERE　NOT   EXIST   (SELECT   *   FROM   B   WHERE   A.ID=B.AID) 
执行结果为 
3       A3 
```

EXISTS   =   IN,意思相同不过语法上有点点区别，好像使用IN效率要差点，应该是不会执行索引的原因 
`SELECT   ID,NAME   FROM   A　   WHERE　ID   IN   (SELECT   AID   FROM   B) `

NOT   EXISTS   =   NOT   IN   ,意思相同不过语法上有点点区别 
`SELECT   ID,NAME   FROM   A   WHERE　ID　NOT   IN   (SELECT   AID   FROM   B) `





#### 聚合函数

- AVG                       求平均值
- COUNT                 检索到的数目
- MIN / MAX           最小/最大值
-  SUM                     求和





#### 控制流程函数

常见的控制流程函数如下：

- CASE 
- IF
- while
- IFNULL
- NULLIF



```mysql
CASE (value) WHEN [compare-value1] THEN result1 
[WHEN [compare-value2] THEN result2] [ELSE result3] END 
```

解释：用value值来匹配，如果value1和value匹配，则返回result1 ，如果value2和value匹配，则返回result2，以此类推；否则，返回ELSE后的result3。；如果没有ELSE部分的值，则返回值为NULL。这种句型类似于Java当中的switch···case···default···。




```mysql
IF(expr1,expr2,expr3) 

-- 或者
if 条件 then
    sql语句
[elseif 条件 then
    sql语句]
[else
 sql语句]
end if;
```

解释：如果表达式expr1是TRUE ，则 IF()的返回值为expr2; 否则返回值则为 expr3。类似于三目运算符。



```mysql
while 条件 do
    sql语句
end while;

-- 或者
循环名:while 条件 do
    sql语句;
    leave/iterate 循环名;
end while;
```

在mysql的循环结构中，使用leave来代替break,使用iterate来代替continue，但它们的使用语法是:leave\iterate 循环名










```mysql
IFNULL(expr1,expr2) 
```

解释：假如expr1不为NULL，则函数返回值为 expr1; 否则，如果如expr1为NULL，函数返回值为expr2。



```mysql
NULLIF(expr1,expr2)
```

解释：如果expr1 = expr2成立，那么返回值为NULL，否则返回值为expr1



```mysql
mysql> select * from teachers;
+----+--------+--------+------+--------+------------+
| id | name   | gender | age  | job    | createDate |
+----+--------+--------+------+--------+------------+
|  1 | java   | M      |   22 | NULL   | 2014-10-14 |
|  2 | python | F      |   23 | class1 | 2014-10-14 |
|  3 | shell  | M      |   22 | class2 | 2014-10-13 |
+----+--------+--------+------+--------+------------+
3 rows in set (0.00 sec)

mysql> select case 1 when 1 then '男' when 2 then '女' else '人妖' end as result;
+--------+
| result |
+--------+
| 男     |
+--------+
1 row in set (0.01 sec)

mysql> select if (1>2, 'yes', 'no');
+-----------------------+
| if (1>2, 'yes', 'no') |
+-----------------------+
| no                    |
+-----------------------+
1 row in set (0.00 sec)

mysql> select ifnull(job, 0) from teachers;
+----------------+
| ifnull(job, 0) |
+----------------+
| 0              |
| class1         |
| class2         |
+----------------+
3 rows in set (0.00 sec)

mysql> select nullif('yes','no');
+--------------------+
| nullif('yes','no') |
+--------------------+
| yes                |
+--------------------+
1 row in set (0.00 sec)
```





#### NULL值的处理

关于 NULL 的条件比较运算是比较特殊的。你不能使用 = NULL 或 != NULL 在列中查找 NULL 值 。

在 MySQL 中，NULL 值与任何其它值的比较（即使是 NULL）永远返回 false，即 NULL = NULL 返回false 。

MySQL 中处理 NULL 使用 **IS NULL** 和 **IS NOT NULL** 运算符。

```sql
mysql> select * from teachers where job is null;
+----+------+--------+------+------+------------+
| id | name | gender | age  | job  | createDate |
+----+------+--------+------+------+------------+
|  1 | java | M      |   22 | NULL | 2014-10-14 |
+----+------+--------+------+------+------------+
1 row in set (0.01 sec)
```



```MYSLQ
以下全是错的

NULL = NULL

NULL !=  NULL

NULL IN (SELECT NULL FROM BIAO)

NULL NOT IN (SELECT NULL FROM BIAO)

Char(0) IS NULL
```







#### 正则表达式

MySQL可以通过 **LIKE ...%** 来进行模糊匹配。

MySQL 同样也支持其他正则表达式的匹配， MySQL中使用 **REGEXP** 操作符来进行正则表达式匹配。

```sql
mysql> select * from teachers where name regexp '^py';
+----+--------+--------+------+--------+------------+
| id | name   | gender | age  | job    | createDate |
+----+--------+--------+------+--------+------------+
|  2 | python | F      |   23 | class1 | 2014-10-14 |
+----+--------+--------+------+--------+------------+
1 row in set (0.00 sec)
```







### 变量

#### 系统变量

- 系统变量就是系统已经提前定义好了的变量
- **系统变量一般都有其特殊意义。**比如某些变量代表字符集、某些变量代表某些mysql文件位置
- 系统变量中包括会话级变量（当次会话连接生效的变量，如names），以及全局变量（一直生效的变量） 【系统变量中全局变量和会话变量其实是使用一套变量，不同的是会话变量仅当次会话生效。】
- - 会话变量的赋值：set 变量名 = 值;  【比如常用的set names ="utf8";】或者set @@变量名=值
  - 全局变量的赋值：set global 变量名 = 值;



查看系统变量

`show variables;`

系统变量的调用

`select @@变量名;`



#### 用户变量

- 用户变量就是用户自己定义的变量。
- 系统为了区别系统变量跟自定义变量，规定用户自定义变量必须使用一个@符号
- 变量的定义方式：
  - `set @变量名=1;` 或者 `set @变量名:=1;`
  - `select @变量名:=值;`
  - `select 值 into @变量名;`
- 用户变量可以不声明定义，就可以直接使用，不过默认是null值
- 用户变量都是会话级的变量，仅在当次连接中生效。



#### 局部变量

- 由于局部变量是用户自定义的，可以认为局部变量也是用户变量【但有所不同，局部中不需要使用@】

- 局部变量一般用在sql语句块中，比如存储过程块、触发器块等

- 局部变量的定义方法：

- - 先使用declare声明局部变量,其中可选项default后面可以跟一个付给变量的默认值：【**非常重要的一步，不然会设置成用户变量】【注意：变量声明语句要在其他语句如select语句之前】**

  - - 示例：declare myq int;
    - 示例：declare myq int default 666;

  - 设置变量的值：

  - - set 变量名= 值；

  - 获取变量的值：

  - - select 变量名;

```mysql
create procedure myset() -- 存储过程
begin 
    declare mya int;
    declare myq int default 777;
    select mya,myq;
    set myq=6;
    set mya=666;
    select mya,myq;
end;

call myset();
```

```mysql
declare @var1 int = case when A>5 then 1 else 0 end
```







### 自定义函数

函数**只会返回一个值**，不允许返回一个结果集

```mysql
-- Not allowed to return a result set from a function
create function myf()returns int 
begin
select * from student;
return 100;
end;
```





#### 基本语法

```mysql
create function 函数名([参数列表]) returns 数据类型
begin
 sql语句;
 return 值;
end;

-- 如果没有返回值，就是过程。关键字function改成procedure就行
```

示例

```mysql
-- 最简单的仅有一条sql的函数
create function myselect2() returns int return 666;
select myselect2(); -- 调用函数

--
create function myselect3() returns int
begin 
    declare c int;
    select id from class where cname="python" into c;
    return c;
end;
select myselect3();
-- 带传参的函数
create function myselect5(name varchar(15)) returns int
begin 
    declare c int;
    select id from class where cname=name into c;
    return c;
end;
select myselect5("python");
```





#### 函数的调用

- 直接使用函数名()就可以调用【**虽然这么说，但返回的是一个结果，sql中不使用select的话任何结果都无法显示出来（所以单纯调用会报错），】**

- 如果想要传入参数可以使用函数名(参数)

- 调用方式【下面调用的函数都是上面中创建的。】：

  ```mysql
  -- 无参调用
  select myselect3();
  -- 传参调用
  select myselect5("python");
  select * from class where id=myselect5("python");
  ```

 



#### 函数的查看

- 查看函数创建语句：`show create function 函数名;`
- 查看所有函数：`show function status [like 'pattern'];`





#### 函数的修改

- 函数的修改只能修改一些如comment的选项，不能修改内部的sql语句和参数列表。
- alter function 函数名 选项；



#### 函数的删除

`drop function 函数名;`







### 存储过程

和函数差不多

基本语法：

```mysql
CREATE PROCEDURE sp_name ([proc_parameter[,...]]) 
　　[characteristic ...] routine_body  
```

```
Sp_name:存储过程的名称，默认在当前数据库中创建。这个名称应当尽量避免与MySQL的内置函数相同的名称

Proc_parameter:存储过程的参数列表
     格式 [IN|OUT|INOUT] param_name type
     Param_name为参数名，type为参数的数据类型。多个参数彼此间用逗号分隔。
     输入参数、输出参数和输入/输出参数，分别用in/out/inout标识。参数的取名不要与数据表的列名相同。

Characteristic:存储过程的某些特征设定，分别介绍
     1 COMMENT'string':用于对存储过程的描述，其中string为描述内容,comment为关键字。
     2 LANGUAGE SQL:指明编写这个存储过程的语言为SQL语言。这个选项可以不指定。
     3 DETERMINISTIC:表示存储过程对同样的输入参数产生相同的结果;NOT DETERMINISTIC，则表示会产生不确定的结果（默认）。
     4 contains sql | no sql | reads sql data | modifies sql data Contains sql表示存储过程包含读或写数据的语句（默认）
        No sql表示不包含sql语句
        Reads sql data表示存储过程只包含读数据的语句
        Modifies sql data 表示存储过程只包含写数据的语句
     5 sql security:这个特征用来指定存储过程使用创建该存储过程的用户(definer)的许可来执行，还是使用调用者(invoker)的许可来执行。默认是definer
    Routine_body:存储过程的主体部分，包含了在过程调用的时候必须执行的sql语句。以begin开始，以end结束。如果存储过程体中只有一条sql语句,可以省略begin-end标志。
```

案例：

```mysql
-- 准备表
CREATE TABLE
 t_user 
 ( 
  USER_ID INT NOT NULL AUTO_INCREMENT, 
  USER_NAME CHAR(30) NOT NULL, 
  USER_PASSWORD CHAR(10) NOT NULL, 
  USER_EMAIL CHAR(30) NOT NULL, 
  PRIMARY KEY (USER_ID), 
  INDEX IDX_NAME (USER_NAME) 
 ) 
 ENGINE=InnoDB DEFAULT CHARSET=utf8; 
```

写入准备的数据
```
USER_ID     USER_NAME     USER_PASSWORD    USER_EMAIL
1	        张三	         12345	          zhansan@qq.com
2	        李四	         67890	          lisi@qq.com
```

```mysql
DELIMITER $
-- 创建存储过程。 带IN的存储过程
CREATE PROCEDURE SP_SEARCH(IN p_name CHAR(20)) 
BEGIN
IF p_name is null or p_name='' THEN
SELECT * FROM t_user; 
ELSE
SELECT * FROM t_user WHERE USER_NAME LIKE p_name; 
END IF; 
END $

DELIMITER ;


-- 调用并输出结果 
CALL SP_SEARCH("") -- 结果是张三那一行
```

```mysql
DELIMITER $
-- 带OUT返回的 
CREATE PROCEDURE SP_SEARCH2(IN p_name CHAR(20),OUT p_int INT) 
BEGIN
IF p_name is null or p_name='' THEN
SELECT * FROM t_user; 
ELSE
SELECT * FROM t_user WHERE USER_NAME LIKE p_name; 
END IF; 
SELECT FOUND_ROWS() INTO p_int; 
END $

DELIMITER ;

CALL SP_SEARCH2('张%',@p_num); -- 返回张三那一行
SELECT @p_num; -- 返回1
```

```mysql
-- 带INOUT的存储过程 
DELIMITER $
CREATE PROCEDURE sp_inout(INOUT p_num INT) 
BEGIN
SET p_num=p_num*10; 
END $

DELIMITER ;
-- 调用并输出结果 
SET @p_num=2; 
call sp_inout(@p_num); 
SELECT @p_num;     -- 返回20
```



**存储过程与存储函数的区别**

1. 存储函数和存储过程统称为存储例程(store routine),存储函数的限制比较多,例如不能用临时表,只能用表变量,而存储过程的限制较少,存储过程的实现功能要复杂些,而函数的实现功能针对性比较强
2. 返回值不同
   存储函数必须有返回值,且仅返回一个结果值
   存储过程可以没有返回值,但是能返回结果集(out,inout)
3. 调用时的不同
   存储函数嵌入在SQL中使用,可以在select 存储函数名(变量值);
   存储过程通过call语句调用 call 存储过程名
4. 参数的不同
   存储函数的参数类型类似于IN参数
   存储过程的参数类型有三种
   - in 数据只是从外部传入内部使用(值传递),可以是数值也可以是变量
   - out 只允许过程内部使用(不用外部数据),给外部使用的(引用传递:外部的数据会被先清空才会进入到内部),只能是变量
   - inout 外部可以在内部使用,内部修改的也可以给外部使用,典型的引用 传递,只能传递变量







### 创建临时表

```mysql
CREATE TEMPORARY TABLE SalesSummary (...............);
```

- 临时表在建立连接时可见，关闭时会清除空间，删除临时表； 

- show tables 不会列出临时表；
- 不能使用rename重命名临时表。但是，你可以alter table代替：只能使用alter table old_tp_table_name rename new_tp_table_name;







### 复制表

只复制表结构到新表

```sql
create table 新表 select * from 旧表 where 1=2
或者
create table 新表 like 旧表 
```



复制表结构及数据到新表

```sql
create table 新表 select * from 旧表 
```





### 处理重复数据

可以在MySQL数据表中设置指定的字段为 PRIMARY KEY（主键） 或者 UNIQUE（唯一） 索引来保证数据的唯一性。



**INSERT IGNORE INTO**与INSERT INTO的区别就是INSERT IGNORE会忽略数据库中已经存在的数据，如果数据库没有数据，就插入新的数据，如果有数据的话就跳过这条数据。这样就可以保留数据库中已经存在数据，达到在间隙中插入数据的目的。

```mysql
mysql> INSERT IGNORE INTO person_tbl (last_name, first_name)
    -> VALUES( 'Jay', 'Thomas');
Query OK, 1 row affected (0.00 sec)
mysql> INSERT IGNORE INTO person_tbl (last_name, first_name)
    -> VALUES( 'Jay', 'Thomas');
Query OK, 0 rows affected (0.00 sec)
```



#### 删除重复数据

如果你想删除数据表中的重复数据，你可以使用以下的SQL语句：

```mysql
mysql> CREATE TABLE tmp SELECT last_name, first_name, sex FROM person_tbl  GROUP BY (last_name, first_name, sex);
mysql> DROP TABLE person_tbl;
mysql> ALTER TABLE tmp RENAME TO person_tbl;
```


当然你也可以在数据表中添加 INDEX（索引） 和 PRIMAY KEY（主键）这种简单的方法来删除表中的重复记录。方法如下：

```mysql
mysql> ALTER IGNORE TABLE person_tbl
    -> ADD PRIMARY KEY (last_name, first_name);
```







### 游标

游标实际上是一种**能从包括多条数据记录的结果集中每次提取一条记录的机制**。

游标充当指针的作用。

尽管游标能遍历结果中的所有行，但他一次只指向一行。

游标的作用就是用于对查询数据库所返回的记录进行遍历，以便进行相应的操作。



语法

- 1.定义游标：declare 游标名 cursor for select语句;
- 2.打开游标：open 游标名;
- 获取结果：fetch 游标名 into 变量名[,变量名];
- 关闭游标:close 游标名;



**在MySql中，造成游标溢出时会引发mysql预定义的NOT FOUND错误，所以在上面使用下面的代码指定了当引发not found错误时定义一个continue 的事件，指定这个事件发生时修改flag变量的值。**

```mysql
create procedure p3()
begin
    declare id int;
    declare name varchar(15);
    declare flag int default 0;
    -- 声明游标
    declare mc cursor for select * from class;
    declare continue handler for not found set flag = 1;
    -- 打开游标
    open mc;
    -- 获取结果
    l2:loop 
    
    fetch mc into id,name;
    if flag=1 then -- 当无法fetch会触发handler continue
        leave l2;
    end if;
    -- 这里是为了显示获取结果
    insert into class2 values(id,name);
    -- 关闭游标
    end loop;
    close mc;
end;


call p3();-- 不报错
select * from class2;
```





### 触发器(trigger)

触发器(trigger)：监视某种情况，并触发某种操作。

触发器创建语法四要素：

1. 监视地点(table) 

2. 监视事件(insert/update/delete) 

3. 触发时间(after/before) 

4. 触发事件



```mysql
CREATE TRIGGER trigger_name trigger_time trigger_event ON tbl_name 
    FOR EACH ROW trigger_stmt
```

```
trigger_name：触发器的名称

tirgger_time：触发时机，为BEFORE或者AFTER

trigger_event：触发事件，为INSERT、DELETE或者UPDATE
　　 insert ：将新行插入表时激活触发程序，例如，通过insert、load data和replace语句。
　　 update：更改某一行时激活触发程序，例如，通过update语句。
　   delete ：从表中删除某一行时激活触发程序，例如，通过delete和replace语句。

tb_name：表示建立触发器的表明，就是在哪张表上建立触发器

trigger_stmt：触发器的程序体，可以是一条SQL语句或者是用BEGIN和END包含的多条语句

所以可以说MySQL创建以下六种触发器：
BEFORE INSERT,BEFORE DELETE,BEFORE UPDATE
AFTER INSERT,AFTER DELETE,AFTER UPDATE
```



**NEW和OLD的使用:**

| 触发器类型     | NEW和OLD的使用                                               |
| -------------- | ------------------------------------------------------------ |
| INSERT型触发器 | NEW表示将要或者已经新增的数据                                |
| DELETE型触发器 | OLD表示将要或者已经删除的数据                                |
| UPDATE型触发器 | OLD表示将要或者已经删除的数据，NEW表示将要或者已经修改的数据 |



案例一

```mysql
drop table if exists users;
CREATE TABLE `users` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(255) CHARACTER SET utf8mb4 DEFAULT NULL,
  `add_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `name` (`name`(250)) USING BTREE
) ENGINE=MyISAM AUTO_INCREMENT=1000001 DEFAULT CHARSET=latin1;


drop table if exists logs;
CREATE TABLE `logs` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `log` varchar(255) DEFAULT NULL COMMENT '日志说明',
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='日志表';


-- 创建触发器
DELIMITER $
CREATE TRIGGER user_log AFTER INSERT ON users FOR EACH ROW
BEGIN
DECLARE s1 VARCHAR(40)character set utf8;
DECLARE s2 VARCHAR(20) character set utf8; -- 后面发现中文字符编码出现乱码，这里设置字符集
SET s2 = " is created";
SET s1 = CONCAT(NEW.name,s2);     -- 函数CONCAT可以将字符串连接
INSERT INTO logs(log) values(s1);
END $
DELIMITER ;


insert into users(name,add_time) values('周伯通',now());

-- 删除触发器
DROP TRIGGER user_log
```

结果
```
users表
id      name  add_time
1000001	周伯通	2019-07-10 12:52:38

logs表
id  log
1	周伯通 is created
```



案例二：统计总积分

```mysql
-- 创建表
drop table if exists table3;
create table table3(
id int primary key auto_increment comment 'id',
num int  comment '积分'
)engine=myisam  default charset=utf8 comment='单独积分表';

-- 创建用函数变量接收的触发器
drop trigger if exists insert_on_table3;
create trigger insert_on_table3
before insert on table3
for each row 
set @sum=@sum+new.num;

-- 触发器触发
set @sum=0;
insert into table3 values(1,2),(2,3),(3,3),(4,3);
select @sum;
```

结果

```
@sum=11
```







### 事务

- **SET AUTOCOMMIT=0** 禁止自动提交
- **SET AUTOCOMMIT=1** 开启自动提交

mysql默认开启自动提交



- **BEGIN** 或者 **START TRANSACTION**开始一个事务
- 创建回滚点：savepoint 回滚点名;
- 回滚到回滚点：rollback to 回滚点名;
- **ROLLBACK** 事务回滚
- **COMMIT** 事务确认



**事务的ACID特性**：

- **原子性**(ATomicity): 一个事务中所有操作全部完成或失败
- **一致性**(Consistency): 事务开始和结束之后数据完整性没有被破坏(举例：转账总钱数不变)
- **隔离性**(Isolation): 允许多个事务同时对数据库修改和读写
- **持久性**(Durability): 事务结束之后，修改是永久的不会丢失(持久化到硬盘)



**事务并发控制(隔离性)问题：** 

- **脏读**：指一个线程中的事务读取到了另外一个线程中未提交的数据。
- **不可重复读**(虚读): 指一个线程中的事务读取到了另外一个线程中提交的update的数据。（针对其他提交前后，读取数据本身的对比）(一个事务重复读两次得到不同结果)
- **幻读**: 指一个线程中的事务读取到了另外一个线程中提交的insert的数据。（针对其他提交前后，读取数据条数的对比）(一次事务第二次查出现第一次没有的结果)
- **丢失数据**: 并发写入造成其中一些修改丢失



为了解决并发控制异常，定义到了**4种事务隔离级别**

- **读未提交**: 别的事务可以读取到未提交改变
- **读已提交**: 只能读取已经提交的数据
- **可重复读**: 同一个事务先后查询结果一样（MySQL默认是可重复读级别）
- **串行化**: 事务完全串行化的执行，隔离级别最高，执行效率最低





### 引擎

**InnoDB** vs **MyISAM** 两种常见引擎的区别

MyISAM不支持事务      InnoDB支持事务

MyISAM不支持外键      InnoDB支持外键

MyISAM只支持表锁      InnoDB支持行锁和表锁







### SQL优化

编写过程：
		select dinstinct  ..from  ..join ..on ..where ..group by ...having ..order by ..limit ..

解析过程：			
		from .. on.. join ..where ..group by ....having ...select dinstinct ..order by limit ...



```sql
mysql> select * from students;   -- 只有id是主键primary key
+----+--------+
| id | name   |
+----+--------+
|  1 | 赵六   |
|  2 | middle |
+----+--------+
2 rows in set (0.06 sec)

mysql> explain select * from students\G
*************************** 1. row ***************************
           id: 1
  select_type: SIMPLE
        table: students
         type: ALL
possible_keys: NULL
          key: NULL
      key_len: NULL
          ref: NULL
         rows: 2
        Extra: 
1 row in set (0.00 sec)

mysql> explain select name from students where id=1\G
*************************** 1. row ***************************
           id: 1
  select_type: SIMPLE
        table: students
         type: const
possible_keys: PRIMARY
          key: PRIMARY
      key_len: 4
          ref: const
         rows: 1
        Extra: 
1 row in set (0.00 sec)

```



type:索引类型、类型
	system>const>eq_ref>ref>range>index>all   ，要对type进行优化的前提：有索引

其中：system,const只是理想情况；实际能达到 ref>range



#### 优化案例一

PASS

```
select * from A
inner join B on B.name = A.name
left join C on C.name = B.name
left join D on D.id = C.id
where C.status>1 and D.status=1;
```

Great

```
select * from A
inner join B on B.name = A.name
left join C on C.name = B.name and C.status>1
left join D on D.id = C.id and D.status=1
```

从上面例子可以看出，**尽可能满足ON的条件，而少用Where的条件**。从执行性能来看第二个显然更加省时。



#### 优化案例二

由于客户数据量越来越大，在实践中让我发现mysql的**exists**与**inner join** 和 **not exists**与 **left join** 性能差别惊人。

我们一般在做数据插入时，想插入不重复的数据，或者盘点数据在一个表，另一个表否有存在相同的数据会用not exists和exists，例如：

```sql
insert into t1(a1) select b1 from t2 where not exists(select 1 from t1 where t1.id = t2.r_id);  

替换为

insert into t1(a1) 
select b1 from t2
left join (select distinct t1.id from t1 ) t1 on t1.id = t2.r_id
where t1.id is null;  



select * from t1 where exists(select 1 from t2 where t1.id=t2.r_id);  

替换为

select t1.* from t1
inner join (select distinct r_id from t2) t2 on t1.id= t2.r_id   
```





#### 优化案例三

**exist**和**in**

```sql
select ..from table where exist (子查询) ;
select ..from table where 字段 in  (子查询) ;
```

**如果主查询的数据集大，则使用In,效率高。**
**如果子查询的数据集大，则使用exist,效率高。**	





#### 优化案例四

最佳左前缀原则，小表驱动大表

详见SQL优化.txt

https://mp.weixin.qq.com/s/fXJ-25w7MDUA7O20VX53-w

https://mp.weixin.qq.com/s/BJyyUloEAJqsz-UzK5GqpA







### information_schema

information_schema数据库中的表都是**只读**的，不能进行更新、删除和插入等操作，也不能加触发器，因为它们**实际只是一个视图**，不是基本表，没有关联的文件。

**information_schema.tables**存储了数据表的元数据信息，下面对常用的字段进行介绍：

- **table_schema**: 记录数据库名；
- **table_name**: 记录数据表名；
- engine : 存储引擎；
- table_rows: 关于表的粗略行估计；
- data_length : 记录表的大小（单位字节）；
- index_length : 记录表的索引的大小；
- row_format: 可以查看数据表是否压缩过；



```mysql
mysql> select table_schema, table_name from information_schema.tables where table_schema='test';
+--------------+------------+
| table_schema | table_name |
+--------------+------------+
| test         | students   |
| test         | teachers   |
+--------------+------------+
2 rows in set (0.00 sec)
```








### 其他

锁、主从复制

详见SQL优化.txt



其他未尽事宜

<https://www.cnblogs.com/progor/p/8886362.html>

