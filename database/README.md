# 数据库初始化说明

第一阶段先提供三套 DBMS 的初始化脚本入口和连接配置模板。课本 P74-P76 的异构表结构补齐后，各成员在对应脚本中替换表定义，并保持后端统一适配器接口不变。

## 对应关系

| 学院 | DBMS | 初始化脚本 | 负责人 |
| --- | --- | --- | --- |
| 学院 A | SQL Server | `sqlserver/init.sql` | 成员 2 |
| 学院 B | Oracle | `oracle/init.sql` | 成员 3 |
| 学院 C | MySQL | `mysql/init.sql` | 成员 4 |

## 数据量要求

- 每个学院 50 名学生。
- 每个学院 10 门课程。
- 每个学生选择 5 门课，即每院 250 条初始选课记录。
- A/B/C 学生集合不重叠。
- 课程信息需要设计部分重叠，用于展示共享课程和集成统计。

## 环境变量

后端读取 `backend/.env` 中的 JDBC 配置。正式运行时复制为本机环境变量或 IDE 运行配置。


docker run \
  --platform linux/amd64 \
  --name college-sqlserver \
  -e ACCEPT_EULA=Y \
  -e MSSQL_SA_PASSWORD='DataInt_2026!' \
  -p 1433:1433 \
  -d mcr.microsoft.com/mssql/server:2022-latest

docker exec -it college-sqlserver \
/opt/mssql-tools18/bin/sqlcmd \
-S localhost \
-U sa \
-P 'DataInt_2026!' \
-C \
-i /tmp/init.sql