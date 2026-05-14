# 教务数据集成系统

本仓库是小组作业第一阶段框架：React 前端 + Spring Boot 后端 + XML 数据集成契约 + 三院数据库脚本模板。

## 技术栈

- 后端：Spring Boot 3.3、Java 17、Jackson XML、JUnit 5。
- 前端：React 18、Vite、TypeScript、Recharts、lucide-react。
- 数据库目标：学院 A / SQL Server，学院 B / Oracle，学院 C / MySQL。
- 集成方式：学院适配器导出/导入统一 XML，集成服务器负责共享课程、跨院选课、退课和统计。

## 环境准备

本机使用 SDKMAN 管理 Java 和 Maven 时，先执行：

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
- 数据库说明：`database/README.md`
- XML 契约：`backend/src/main/resources/academic-integration.xsd`
