# 统一 XML 契约与演示

契约文件：`backend/src/main/resources/academic-integration.xsd`

运行时校验：`XmlSchemaValidationService`（导出、导入前均会校验）

## 文档根元素

| 根元素 | 用途 | 子元素 |
| --- | --- | --- |
| `students` | 学生列表导出 | `student` → `id`, `name`, `sex`, `major` |
| `classes` | 课程列表导出 | `class` → `id`, `name`, `time`, `score`, `teacher`, `location` |
| `choices` | 选课列表导出/导入 | `choice`（见下） |
| `enrollmentRequests` | 跨院选课请求 | `enrollmentRequest` → 四元组学院+学号/课号 |

### choice 两种格式（XSD `xs:choice`）

**导出（本院）** — 与三院适配器 PDF 表 3-15/3-19 一致：

```xml
<choices>
  <choice>
    <sid>A-S001</sid>
    <cid>A-C001</cid>
    <score>85</score>
  </choice>
</choices>
```

**导入（跨院）** — 对应 JSON `EnrollmentCreateRequest`：

```xml
<choices>
  <choice>
    <studentCollege>A</studentCollege>
    <studentId>A-S001</studentId>
    <courseCollege>B</courseCollege>
    <courseId>B-C001</courseId>
  </choice>
</choices>
```

### 跨院选课请求

```xml
<enrollmentRequests>
  <enrollmentRequest>
    <studentCollege>A</studentCollege>
    <studentId>A-S001</studentId>
    <courseCollege>B</courseCollege>
    <courseId>B-C001</courseId>
  </enrollmentRequest>
</enrollmentRequests>
```

`studentCollege` / `courseCollege` 取值限定为 `A`、`B`、`C`。

## HTTP 接口

### 导出（导出结果自动 XSD 校验）

```bash
curl -s http://127.0.0.1:8080/api/xml/A/students
curl -s http://127.0.0.1:8080/api/xml/B/courses
curl -s http://127.0.0.1:8080/api/xml/C/enrollments
```

### 导入（先 XSD 校验，再解析写库）

```bash
curl -s -X POST http://127.0.0.1:8080/api/integration/enrollments \
  -H "Content-Type: application/xml" \
  -d @- <<'EOF'
<enrollmentRequests>
  <enrollmentRequest>
    <studentCollege>A</studentCollege>
    <studentId>A-S001</studentId>
    <courseCollege>B</courseCollege>
    <courseId>B-C001</courseId>
  </enrollmentRequest>
</enrollmentRequests>
EOF
```

JSON 选课仍使用：`POST /api/integration/enrollments` + `Content-Type: application/json`。

## 自动化验证

```bash
cd backend
mvn test -Dtest=ApiContractTest#xmlExportForAllCollegesPassesXsd
mvn test -Dtest=XmlSchemaValidationServiceTest
```

`ApiContractTest` 会对 A/B/C 三院的 students、courses、enrollments 导出结果执行 XSD 校验。
