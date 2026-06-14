# PDF 实现对照清单

对照文件：`基于XML数据集成的集成教务系统示例.pdf`

## 已补齐

| PDF 要求 | 当前实现 |
| --- | --- |
| A/B/C 使用不同 DBMS | A=SQL Server、B=Oracle、C=MySQL，初始化脚本在 `database/` |
| 每院 50 学生、10 课程、每人 5 门课 | `database/sqlserver/init.sql`、`database/oracle/init.sql`、`database/mysql/init.sql` |
| 集成服务器负责共享课程、跨院选课、统计、退选 | `IntegrationController` 提供 `/api/integration/*` |
| 统一 XML 格式 | `academic-integration.xsd` 定义 `students`、`classes`、`choices`、`enrollmentRequests`、`withdrawRequests` |
| XML Schema 校验 | `XmlSchemaValidationService` 对统一 XML 和本地 XML 执行 XSD 校验 |
| XSLT 转换 | `XmlTransformService` + `backend/src/main/resources/xslt/` |
| PDF 表 3-16 的 XSL 文件 | 已提供 `formatClass/Student/ClassChoice.xsl`、`studentToA/B/C.xsl`、`classToA/B/C.xsl`、`choiceToA/B/C.xsl` |
| 本地格式 XSD | `backend/src/main/resources/schemas/local/` 下提供 A/B/C 的 student/class/choice XSD |
| 课程共享 XML 流程 | `/api/integration/shared-courses/xml?source=B&target=A` 先生成统一课程 XML，再用 `classToA.xsl` 转目标格式并校验 |
| 跨院选课 XML 流程 | `/api/integration/enrollments/xml` 先校验统一 XML，再转换成目标学院 choice XML 并校验，然后写入目标学院导入表 |
| 集成退选 XML 流程 | `/api/integration/withdrawals/xml` 校验 `withdrawRequests` 后执行退选 |
| GUI 和登录 | React 前端含登录页、学院数据页、集成服务器页、统计页 |

## 与 PDF 架构的说明

当前项目把 PDF 中的 `XMLClient`、`XMLServer` 和集成服务器收敛到同一个 Spring Boot 后端中实现：

- `SqlServerCollegeADataService` / `OracleCollegeBDataService` / `MySqlCollegeCDataService` 模拟各学院 XMLServer 的数据库读取与写回。
- `XmlExportService` 负责从适配器数据生成统一 XML。
- `XmlCourseSharingService`、`XmlImportService`、`XmlTransformService` 组合承担集成服务器的 XML 校验、XSLT 转换和目标学院写回。

这种实现保留了 PDF 的核心技术链路：异构库 → XML → XSD 校验 → XSLT 转换 → 目标库写回；部署形态上没有拆成多个独立 socket/server 进程，报告中可以说明为课程项目中的同进程模拟。

## 演示建议

1. 登录 `integration-admin / password`。
2. 进入“集成服务器”页，查看共享课程表和“XML 课程共享报文”。
3. 使用 XML 选课：A 学生选择 B 课程，检查 B 库 `B_IMPORTED_STUDENT` / `B_IMPORTED_SELECTION`。
4. 使用 XML 退选，刷新统计。
5. 运行 `mvn test` 展示 XSD、XSLT、接口契约测试均通过。
