# 统一 XML 契约与演示

契约文件：`backend/src/main/resources/academic-integration.xsd`

运行时校验：`XmlSchemaValidationService`（导出、导入前均会校验）

XSLT 转换：`backend/src/main/resources/xslt/`

本地格式 XSD：`backend/src/main/resources/schemas/local/`

## 文档根元素

| 根元素 | 用途 | 子元素 |
| --- | --- | --- |
| `students` | 学生列表导出 | `student` → `id`, `name`, `sex`, `major` |
| `classes` | 课程列表导出 | `class` → `id`, `name`, `time`, `score`, `teacher`, `location` |
| `choices` | 选课列表导出/导入 | `choice`（见下） |
| `enrollmentRequests` | 跨院选课请求 | `enrollmentRequest` → 四元组学院+学号/课号 |
| `withdrawRequests` | 集成退选请求 | `withdrawRequest` → `enrollmentId` |

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
    <studentId>202300000001</studentId>
    <courseCollege>B</courseCollege>
    <courseId>B0001</courseId>
  </choice>
</choices>
```

### 跨院选课请求

```xml
<enrollmentRequests>
  <enrollmentRequest>
    <studentCollege>A</studentCollege>
    <studentId>202300000001</studentId>
    <courseCollege>B</courseCollege>
    <courseId>B0001</courseId>
  </enrollmentRequest>
</enrollmentRequests>
```

`studentCollege` / `courseCollege` 取值限定为 `A`、`B`、`C`。
上面的编号来自真实数据库初始化脚本：A 学生 `202300000001` 选择 B 课程 `B0001`。

### 集成环境退选请求

```xml
<withdrawRequests>
  <withdrawRequest>
    <enrollmentId>B0001-202300000001</enrollmentId>
  </withdrawRequest>
</withdrawRequests>
```

## XSLT 与本地 XML 格式

PDF 表 3-16 中的 XSL 文件已放在 `backend/src/main/resources/xslt/`：

| XSL | 作用 |
| --- | --- |
| `formatClass.xsl` | A/B/C 本地课程 XML → 统一 `classes` |
| `formatStudent.xsl` | A/B/C 本地学生 XML → 统一 `students` |
| `formatClassChoice.xsl` | A/B/C 本地选课 XML → 统一 `choices` |
| `studentToA.xsl` / `studentToB.xsl` / `studentToC.xsl` | 统一学生 XML → 目标学院学生 XML |
| `classToA.xsl` / `classToB.xsl` / `classToC.xsl` | 统一课程 XML → 目标学院课程 XML |
| `choiceToA.xsl` / `choiceToB.xsl` / `choiceToC.xsl` | 统一选课 XML → 目标学院选课 XML |

对应本地 XSD 位于 `backend/src/main/resources/schemas/local/`，例如：

```xml
<Choices>
  <choice>
    <学生编号>202300000001</学生编号>
    <课程编号>B0001</课程编号>
    <得分>0</得分>
  </choice>
</Choices>
```

## HTTP 接口

### 导出（导出结果自动 XSD 校验）

```bash
curl -s http://127.0.0.1:8080/api/xml/A/students
curl -s http://127.0.0.1:8080/api/xml/B/courses
curl -s http://127.0.0.1:8080/api/xml/C/enrollments
```

### 课程共享 XML（统一格式 → 目标学院格式）

```bash
curl -s 'http://127.0.0.1:8080/api/integration/shared-courses/xml?source=B&target=A'
```

返回示例结构：

```xml
<Classes>
  <class>
    <课程编号>B0001</课程编号>
    <课程名称>数据库系统</课程名称>
    <课时>48</课时>
    <学分>3</学分>
    <授课老师>B教师01</授课老师>
    <授课地点>实验楼101</授课地点>
  </class>
</Classes>
```

### 导入（先 XSD 校验，再解析写库）

```bash
curl -s -X POST http://127.0.0.1:8080/api/integration/enrollments/xml \
  -H "Content-Type: application/xml" \
  -d @- <<'EOF'
<enrollmentRequests>
  <enrollmentRequest>
    <studentCollege>A</studentCollege>
    <studentId>202300000001</studentId>
    <courseCollege>B</courseCollege>
    <courseId>B0001</courseId>
  </enrollmentRequest>
</enrollmentRequests>
EOF
```

演示界面的“创建选课”按钮直接提交上面的 XML 报文。`POST /api/integration/enrollments` 的 JSON 接口仅保留为兼容/调试入口，不作为基于 XML 数据集成的主流程。

执行后可在 B 库检查跨院写回：

```sql
SELECT * FROM B_IMPORTED_STUDENT WHERE source_college = 'A' AND student_no = '202300000001';
SELECT * FROM B_IMPORTED_SELECTION WHERE source_college = 'A' AND student_no = '202300000001' AND course_no = 'B0001';
```

### XML 退选

```bash
curl -s -X POST http://127.0.0.1:8080/api/integration/withdrawals/xml \
  -H "Content-Type: application/xml" \
  -d @- <<'EOF'
<withdrawRequests>
  <withdrawRequest>
    <enrollmentId>B0001-202300000001</enrollmentId>
  </withdrawRequest>
</withdrawRequests>
EOF
```

## 自动化验证

```bash
cd backend
mvn test -Dtest=ApiContractTest#xmlExportForAllCollegesPassesXsd
mvn test -Dtest=ApiContractTest#sharedCoursesXmlEndpointTransformsUnifiedCoursesToTargetCollegeFormat
mvn test -Dtest=XmlSchemaValidationServiceTest
mvn test -Dtest=XmlTransformServiceTest
```

`ApiContractTest` 会对 A/B/C 三院的 students、courses、enrollments 导出结果执行 XSD 校验。
