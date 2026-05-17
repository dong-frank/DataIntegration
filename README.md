# 数据集成

## 技术栈

- 后端：Spring Boot 3.3、Java 17、Jackson XML、JUnit 5。
- 前端：React 18、Vite、TypeScript、Recharts、lucide-react。
- 数据库目标：学院 A / SQL Server，学院 B / Oracle，学院 C / MySQL。
- 集成方式：学院适配器导出/导入统一 XML，集成服务器负责共享课程、跨院选课、退课和统计。

## 环境准备

如果使用 SDKMAN 管 Java/Maven，先执行：

```bash
source ~/.sdkman/bin/sdkman-init.sh
```

确认版本：

```bash
java -version
mvn -version
node -v
npm -v
```

## 启动后端

```bash
cd backend
source ~/.sdkman/bin/sdkman-init.sh
mvn spring-boot:run
```

后端默认端口：`http://127.0.0.1:8080`

默认数据模式是 `mock`，所有学院都使用内存示例数据。学院 A 的 SQL Server 适配器已经接入；想让学院 A 读取真实 SQL Server 时，先执行 `database/sqlserver/init.sql`，再用以下方式启动：

也可以在 `backend/.env` 中填写连接配置；后端会自动读取这个文件，真实密码不要提交到 Git。

```bash
cd backend
source ~/.sdkman/bin/sdkman-init.sh
mvn spring-boot:run
```

`APP_DATA_MODE=database` 当前行为：

- 学院 A：读取 SQL Server 视图 `dbo.vw_adapter_students`、`dbo.vw_adapter_courses`、`dbo.vw_adapter_enrollments`。
- 学院 B/C：暂时继续读取 mock 数据，等待 Oracle/MySQL 适配器接入。

常用接口：

- `GET /api/health`
- `POST /api/auth/login`
- `GET /api/college/A/students`
- `GET /api/integration/stats`
- `GET /api/xml/A/students`

## 启动前端

```bash
cd frontend
npm install
npm run dev
```

前端默认端口：`http://127.0.0.1:5173`

演示账号密码：

| 用户名 | 密码 | 角色 |
| --- | --- | --- |
| `college-a` | `password` | 学院 A |
| `college-b` | `password` | 学院 B |
| `college-c` | `password` | 学院 C |
| `integration-admin` | `password` | 集成服务器管理员 |

## 测试

后端：

```bash
cd backend
source ~/.sdkman/bin/sdkman-init.sh
mvn test
```

前端：

```bash
cd frontend
npm test
npm run build
```

## 作业文档

- 分工计划：`docs/分工计划.md`
- 流程图草稿：`docs/流程图草稿.md`
- 学院 A SQL Server 适配：`docs/学院A-SQLServer后端适配说明.md`
- 数据库说明：`database/README.md`
- XML 契约：`backend/src/main/resources/academic-integration.xsd`
