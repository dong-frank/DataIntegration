# 学院 A SQL Server 后端适配说明

## 当前状态

后端已经完成学院 A 的 SQL Server 读取适配。默认启动仍使用 mock 数据；当 `APP_DATA_MODE=database` 时，后端会把学院 A 的学生、课程、选课查询切到 SQL Server，学院 B/C 暂时继续使用 mock 数据。

## 关键代码

| 文件 | 作用 |
| --- | --- |
| `AcademicDataService` | 后端统一数据服务接口，供学院端、集成端、XML 导出共同使用 |
| `MockAcademicDataService` | 默认 mock 实现，保留原来的 50/10/250 示例数据 |
| `SqlServerCollegeADataService` | 查询 SQL Server 中学院 A 的三个适配视图 |
| `RoutedAcademicDataService` | `APP_DATA_MODE=database` 时启用，学院 A 走 SQL Server，B/C 走 mock |
| `CollegeAJdbcConfig` | 根据 `application.yml` 和环境变量创建学院 A 的 `JdbcTemplate` |

## 当前字段口径

学院 A 现在对外暴露的统一 JSON 字段如下：

- 学生：`id, college, name, gender, major, grade`
- 课程：`id, college, name, hours, credits, teacher, location, shared`
- 选课：`id, studentCollege, studentId, courseCollege, courseId, enrolledAt, status, score`

统一 XML 则按 PDF 输出：

- 学生：`id, name, sex, major`
- 课程：`id, name, time, score, teacher, location`
- 选课：`sid, cid, score`

## 使用步骤

1. 在 SQL Server 中执行 `database/sqlserver/init.sql`。
2. 确认脚本最后统计结果为 50 名学生、10 门课程、250 条选课。
3. 设置环境变量并启动后端：

```bash
cd backend
source ~/.sdkman/bin/sdkman-init.sh
APP_DATA_MODE=database \
COLLEGE_A_JDBC_URL='jdbc:sqlserver://localhost:1433;databaseName=college_a;encrypt=true;trustServerCertificate=true' \
COLLEGE_A_DB_USER='sa' \
COLLEGE_A_DB_PASSWORD='ChangeMe_123' \
mvn spring-boot:run
```

4. 打开前端，用 `college-a / password` 登录，学院 A 页面会读取 SQL Server。

## 验证接口

```bash
curl http://127.0.0.1:8080/api/college/A/students
curl http://127.0.0.1:8080/api/college/A/courses
curl http://127.0.0.1:8080/api/college/A/enrollments
curl http://127.0.0.1:8080/api/xml/A/students
```

## 后续给 Oracle/MySQL 成员的要求

Oracle 和 MySQL 最好也提供等价适配视图，字段名保持一致：

- 学生：`id, college, name, gender, major, grade`
- 课程：`id, college, name, hours, credits, teacher, location, shared`
- 选课：`id, studentCollege, studentId, courseCollege, courseId, enrolledAt, status, score`

这样后端只需要补 `OracleCollegeBDataService` 和 `MySqlCollegeCDataService`，不用再改前端和统一 API。

## 跨院写回说明

为了满足 PDF 中“目标院系接收外院学生信息和选课信息”的流程，学院 A 在本地原始四张表之外补了两张扩展表：

- `A_IMPORTED_STUDENT`
- `A_IMPORTED_SELECTION`

当外院学生选择 A 课程时：

1. 集成层先根据源学院查到该学生信息
2. A 适配器把学生写入 `A_IMPORTED_STUDENT`
3. 再把选课信息写入 `A_IMPORTED_SELECTION`

这样不会破坏 `A_SELECTION -> A_STUDENT` 的原始外键约束，同时 A 的统一选课视图仍能看到这些跨院写回记录。
