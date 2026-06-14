# 数据库初始化说明

第一阶段先提供三套 DBMS 的初始化脚本入口和连接配置模板。课本 P74-P76 的异构表结构补齐后，各成员在对应脚本中替换表定义，并保持后端统一适配器接口不变。

## 对应关系

| 学院 | DBMS | 初始化脚本 | 负责人 |
| --- | --- | --- | --- |
| 学院 A | SQL Server | `sqlserver/init.sql` | 成员 2 |
| 学院 B | Oracle | `oracle/init.sql` | 成员 3 |
| 学院 C | MySQL | `mysql/init.sql` | 成员 4 |

## 学院 A 适配视图迁移

如果已经建过 `college_a` 数据库，拉取新版后看到类似错误：

- `Invalid column name 'hours'`
- `Invalid column name 'score'`

说明 SQL Server 中的 `dbo.vw_adapter_courses` / `dbo.vw_adapter_enrollments`
还是旧视图定义。不要为了这个直接重跑会清空数据的 `sqlserver/init.sql`，可以执行增量迁移：

```bash
docker cp database/sqlserver/migrate_20260517_adapter_views.sql college-sqlserver:/tmp/migrate_20260517_adapter_views.sql
docker exec -it college-sqlserver \
/opt/mssql-tools18/bin/sqlcmd \
-S localhost \
-U sa \
-P 'DataInt_2026!' \
-C \
-i /tmp/migrate_20260517_adapter_views.sql
```

执行完成后，脚本末尾会分别查询 `vw_adapter_courses` 和
`vw_adapter_enrollments` 的前 5 行，用于确认已经输出 `hours/location/score`。

## 学院 A 中文问号和选课为 0 的修复

如果学院 A 页面出现课程名/教师/地点为 `????`，且有效选课为 `0`，原因通常是旧版
`database/sqlserver/init.sql` 使用了 `VARCHAR` 存中文，并且选课生成 CTE 使用了
`offsets` 这个在 SQL Server 中容易触发语法错误的名字。

不想清库重建时，可以执行增量修复脚本：

```bash
docker cp database/sqlserver/fix_20260521_unicode_and_selections.sql college-sqlserver:/tmp/fix_20260521_unicode_and_selections.sql

docker exec -it college-sqlserver \
/opt/mssql-tools18/bin/sqlcmd \
-S localhost \
-U sa \
-P 'DataInt_2026!' \
-C \
-i /tmp/fix_20260521_unicode_and_selections.sql
```

执行后脚本末尾应显示 `student_count=50`、`course_count=10`、`selection_count=250`。

## 数据量要求

- 每个学院 50 名学生。
- 每个学院 10 门课程。
- 每个学生选择 5 门课，即每院 250 条初始选课记录。
- A/B/C 学生集合不重叠。
- 课程信息按学院学科方向特色化命名，`shared`/`Share` 标记表示课程是否开放给外院学生跨院选修。

## 学生姓名增量更新

当前初始化脚本已将学生姓名从编号占位值改为三字中文姓名。若本地容器已初始化过，
不想清空选课数据重建，可以只执行姓名增量脚本：

```bash
docker cp database/sqlserver/update_20260529_student_names.sql college-sqlserver:/tmp/update_20260529_student_names.sql
docker exec college-sqlserver /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P 'DataInt_2026!' -C -i /tmp/update_20260529_student_names.sql

docker cp database/mysql/update_20260529_student_names.sql college-mysql:/tmp/update_20260529_student_names.sql
docker exec college-mysql mysql -uroot -pDataInt_2026! --default-character-set=utf8mb4 college_c -e 'source /tmp/update_20260529_student_names.sql'

docker cp database/oracle/update_20260529_student_names.sql college-oracle:/tmp/update_20260529_student_names.sql
docker exec college-oracle sqlplus -S 'college_b/DataInt_2026!@//localhost:1521/XEPDB1' @/tmp/update_20260529_student_names.sql
```

## 环境变量

后端读取 `backend/.env` 中的 JDBC 配置。正式运行时复制为本机环境变量或 IDE 运行配置。

## SQLServer
docker run \
  --platform linux/amd64 \
  --name college-sqlserver \
  -e ACCEPT_EULA=Y \
  -e MSSQL_SA_PASSWORD='DataInt_2026!' \
  -p 1433:1433 \
  -d mcr.microsoft.com/mssql/server:2022-latest

docker cp database/sqlserver/init.sql college-sqlserver:/tmp/init.sql

docker exec -it college-sqlserver \
/opt/mssql-tools18/bin/sqlcmd \
-S localhost \
-U sa \
-P 'DataInt_2026!' \
-C \
-i /tmp/init.sql

## MySQL
docker run \
  --name college-mysql \
  -e MYSQL_ROOT_PASSWORD='DataInt_2026!' \
  -e MYSQL_DATABASE='college_c' \
  -e MYSQL_USER='college_c' \
  -e MYSQL_PASSWORD='DataInt_2026!' \
  -p 3306:3306 \
  -d mysql:8.4

docker cp database/mysql/init.sql college-mysql:/tmp/init.sql

docker exec -it college-mysql \
mysql -uroot -pDataInt_2026! \
--default-character-set=utf8mb4 \
college_c \
-e "source /tmp/init.sql"

后端连接本地 MySQL 8 Docker 时，JDBC URL 需要带上
`allowPublicKeyRetrieval=true`，否则可能出现
`Public Key Retrieval is not allowed`：

```bash
COLLEGE_C_JDBC_URL='jdbc:mysql://localhost:3306/college_c?useSSL=false&allowPublicKeyRetrieval=true&serverTimezone=Asia/Shanghai'
```

## Oracle

如果之前启动失败，先清理同名容器：

```bash
docker rm -f college-oracle 2>/dev/null || true
```

启动 Oracle XE 后需要等数据库初始化完成，`gvenzl/oracle-xe` 首次启动可能需要数分钟：

```bash
docker run \
  --platform linux/amd64 \
  --name college-oracle \
  -e ORACLE_PASSWORD='DataInt_2026!' \
  -p 1521:1521 \
  -d gvenzl/oracle-xe:21-slim

until docker exec college-oracle healthcheck.sh >/dev/null 2>&1; do
  echo 'waiting for Oracle...'
  sleep 5
done
```

创建或重建学院 B 用户：

```bash
docker exec -i college-oracle sqlplus -S /nolog <<'SQL'
CONNECT sys/"DataInt_2026!"@//localhost:1521/XEPDB1 AS SYSDBA
BEGIN
  EXECUTE IMMEDIATE 'DROP USER college_b CASCADE';
EXCEPTION
  WHEN OTHERS THEN
    IF SQLCODE != -1918 THEN
      RAISE;
    END IF;
END;
/
CREATE USER college_b IDENTIFIED BY "DataInt_2026!"
  DEFAULT TABLESPACE USERS
  TEMPORARY TABLESPACE TEMP
  QUOTA UNLIMITED ON USERS;

GRANT CREATE SESSION, CREATE TABLE, CREATE VIEW TO college_b;
EXIT;
SQL
```

导入学院 B 初始化脚本：

```bash
docker cp database/oracle/init.sql college-oracle:/tmp/init.sql

docker exec -i college-oracle sqlplus -S /nolog <<'SQL'
CONNECT college_b/"DataInt_2026!"@//localhost:1521/XEPDB1
@/tmp/init.sql
EXIT;
SQL
```
