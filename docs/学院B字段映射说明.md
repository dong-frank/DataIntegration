# 学院 B 字段映射说明

本说明对应 `database/oracle/init.sql`，按 PDF 中学院 B 的四张基础表设计，
并补充统一 JSON 模型、统一 XML 格式以及跨院写回到学院 B 时的适配规则。

## 1. 设计思路

- 学院 B 保留 PDF 里的 4 张基础表：账户表、学生表、课程表、选课表。
- 数据库使用 Oracle，类型为 `VARCHAR2`、`NUMBER`、`CHAR`，体现与 A（SQL Server）和 C（MySQL）的异构性。
- 统一 JSON 模型服务于后端接口和前端页面。
- 统一 XML 按 PDF 表 3-13、3-14、3-15 输出。
- 外院学生选 B 课程时，不直接写入 `B_STUDENT`，而通过扩展导入表完成写回，避免破坏原始外键结构。

## 2. 课本表结构对应关系

| 课本表       | 本地表名       |
|--------------|----------------|
| 院系 B 账户表 | `B_ACCOUNT`    |
| 院系 B 学生表 | `B_STUDENT`    |
| 院系 B 课程表 | `B_COURSE`     |
| 院系 B 选课表 | `B_SELECTION`  |

## 3. 异构性说明（B 与 A/C 的差异）

| 维度          | 学院 A (SQL Server)         | 学院 B (Oracle)                    | 学院 C (MySQL)        |
|---------------|-----------------------------|------------------------------------|----------------------|
| 学号长度      | VARCHAR(12)                 | VARCHAR2(9)                        | VARCHAR(9)           |
| 密码存储位置  | 账户表 (`A_ACCOUNT`)         | 学生表 (`B_STUDENT`) + 账户表 (`B_ACCOUNT`) 各自存储 | 学生表 (`C_STUDENT`) |
| 账户-学生关系 | 学生表 FK → 账户表 (学生指向账户) | 账户表 FK → 学生表 (账户指向学生) | 无关联表              |
| 课时字段      | 无（按学分×16 推导）         | `class_hours VARCHAR2(2)` 直接存储 | `Ctm INTEGER`        |
| 成绩字段名    | `score_text VARCHAR(3)`     | `score_text VARCHAR2(3)`           | `Grd INTEGER`        |
| 课程编号格式  | A0000001~A0000010 (8位)     | B0001~B0010 (5位)                  | C001~C010 (4位)      |

## 4. 跨院写回扩展表

| 扩展表                | 作用                                         |
|-----------------------|----------------------------------------------|
| `B_IMPORTED_STUDENT`  | 保存写入 B 的外院学生基本信息                |
| `B_IMPORTED_SELECTION`| 保存外院学生选择 B 课程后的写回选课记录      |

## 5. 学生表映射

本地表：`B_STUDENT` (PDF 表 3-7)

| 本地字段        | PDF 字段 | 含义     | 统一 JSON 字段 | 转换规则                       |
|-----------------|----------|----------|----------------|-------------------------------|
| `student_no`    | 学号     | 学号     | `id`           | 直接映射                       |
| 常量 `'B'`      | —        | 学院标识 | `college`      | 适配视图固定为 `B`             |
| `student_name`  | 姓名     | 姓名     | `name`         | 直接映射                       |
| `gender`        | 性别     | 性别     | `gender`       | 直接映射，值为 `男/女`；Oracle DDL 使用 `VARCHAR2(2 CHAR)` 避免中文按字节超长 |
| `major`         | 专业     | 专业     | `major`        | 直接映射                       |
| `student_no` 前 4 位 | —  | 入学年份 | `grade`        | `TO_NUMBER(SUBSTR(student_no,1,4))` 派生 |

对应统一 JSON 模型：

```java
StudentRecord(id, college, name, gender, major, grade)
```

对应统一 XML 学生格式（PDF 表 3-18）：

| 统一 XML 元素 | B 系统 XML 元素 | B 数据库底层字段      |
|---------------|-----------------|----------------------|
| `id`          | 学号            | `B_STUDENT.student_no`    |
| `name`        | 姓名            | `B_STUDENT.student_name`  |
| `sex`         | 性别            | `B_STUDENT.gender`        |
| `major`       | 专业            | `B_STUDENT.major`         |

## 6. 课程表映射

本地表：`B_COURSE` (PDF 表 3-8)

| 本地字段      | PDF 字段 | 含义     | 统一 JSON 字段 | 转换规则                                                     |
|---------------|----------|----------|----------------|-------------------------------------------------------------|
| `course_no`   | 编号     | 课程编号 | `id`           | 直接映射                                                     |
| 常量 `'B'`    | —        | 开课学院 | `college`      | 适配视图固定为 `B`                                           |
| `course_name` | 名称     | 课程名称 | `name`         | 直接映射                                                     |
| `class_hours` | 课时     | 课时     | `hours`        | `TO_NUMBER(class_hours)` 转整数（B 直接存储，非推导）        |
| `credit_pts`  | 学分     | 学分     | `credits`      | `CAST(TO_NUMBER(credit_pts) AS NUMBER(3,1))` 转小数         |
| `teacher`     | 老师     | 授课老师 | `teacher`      | 直接映射                                                     |
| `location`    | 地点     | 授课地点 | `location`     | 直接映射                                                     |
| `shared`      | 共享     | 共享标记 | `shared`       | `'Y'→1`，`'N'→0`（Oracle 无 BOOLEAN，用 NUMBER 1/0 代替） |

对应统一 JSON 模型：

```java
CourseRecord(id, college, name, hours, credits, teacher, location, shared)
```

对应统一 XML 课程格式（PDF 表 3-17）：

| 统一 XML 元素 | B 系统 XML 元素 | B 数据库底层字段         |
|---------------|-----------------|--------------------------|
| `id`          | 编号            | `B_COURSE.course_no`     |
| `name`        | 名称            | `B_COURSE.course_name`   |
| `time`        | 课时            | `B_COURSE.class_hours`   |
| `score`       | 学分            | `B_COURSE.credit_pts`    |
| `teacher`     | 老师            | `B_COURSE.teacher`       |
| `location`    | 地点            | `B_COURSE.location`      |

## 7. 选课表映射

本地表：`B_SELECTION` (PDF 表 3-9)

| 本地字段      | PDF 字段 | 含义       | 统一 JSON 字段  | 转换规则                         |
|---------------|----------|------------|-----------------|----------------------------------|
| `course_no || '-' || student_no` | — | 组合标识 | `id` | 适配视图拼接生成             |
| 常量 `'B'`    | —        | 学生所属学院 | `studentCollege` | 本院学生固定为 `B`            |
| `student_no`  | 学号     | 学生学号   | `studentId`     | 直接映射                         |
| 常量 `'B'`    | —        | 课程所属学院 | `courseCollege` | B 课程固定为 `B`              |
| `course_no`   | 课程编号 | 课程编号   | `courseId`      | 直接映射                         |
| 行号派生日期  | —        | 选课日期   | `enrolledAt`    | 按初始化顺序从 2026-03-01 顺延   |
| 常量 `'ACTIVE'` | —      | 选课状态   | `status`        | B 原表无状态字段，统一输出 `ACTIVE` |
| `score_text`  | 得分     | 成绩       | `score`         | 直接映射（VARCHAR2 字符串）      |

对应统一 JSON 模型：

```java
EnrollmentRecord(id, studentCollege, studentId, courseCollege, courseId,
                 enrolledAt, status, score)
```

对应统一 XML 选课格式（PDF 表 3-19）：

| 统一 XML 元素 | B 系统 XML 元素 | B 数据库底层字段              |
|---------------|-----------------|-------------------------------|
| `sid`         | 学生编号        | `B_SELECTION.student_no`      |
| `cid`         | 课程编号        | `B_SELECTION.course_no`       |
| `score`       | 得分            | `B_SELECTION.score_text`      |

## 8. 字段映射汇总（对应 PDF 表 3-17/3-18/3-19）

| 统一格式 XML 元素 | B 系统 XML 元素 | B 数据库底层字段              |
|-------------------|-----------------|-------------------------------|
| id (学生)         | 学号            | `B_STUDENT.student_no`        |
| name (学生)       | 姓名            | `B_STUDENT.student_name`      |
| sex               | 性别            | `B_STUDENT.gender`            |
| major             | 专业            | `B_STUDENT.major`             |
| id (课程)         | 编号            | `B_COURSE.course_no`          |
| name (课程)       | 名称            | `B_COURSE.course_name`        |
| time / 课时       | 课时            | `B_COURSE.class_hours`        |
| score / credits   | 学分            | `B_COURSE.credit_pts`         |
| teacher           | 老师            | `B_COURSE.teacher`            |
| location          | 地点            | `B_COURSE.location`           |
| sid               | 学生编号        | `B_SELECTION.student_no`      |
| cid               | 课程编号        | `B_SELECTION.course_no`       |
| score (成绩)      | 得分            | `B_SELECTION.score_text`      |

## 9. 跨院写回规则

目标：外院学生选择 B 的共享课程后，B 侧能把学生信息和选课信息写入本院数据库。

### 9.1 外院学生信息

本地表：`B_IMPORTED_STUDENT`

| 字段            | 含义                 |
|-----------------|----------------------|
| `source_college`| 学生来源学院 (A/C)   |
| `student_no`    | 外院学号（最长 12 位）|
| `student_name`  | 外院学生姓名         |
| `gender`        | 外院学生性别         |
| `major`         | 外院学生专业/院系    |
| `imported_on`   | 导入日期             |

### 9.2 外院选课信息

本地表：`B_IMPORTED_SELECTION`

| 字段            | 含义                                   |
|-----------------|----------------------------------------|
| `course_no`     | B 院课程编号                           |
| `source_college`| 学生来源学院 (A/C)                     |
| `student_no`    | 外院学号                               |
| `score_text`    | 成绩，初始写 `'0'`                     |
| `enrolled_on`   | 选课写回日期                           |
| `status_code`   | 状态，`ACTIVE` 或 `WITHDRAWN`          |

### 9.3 统一输出策略

- `vw_adapter_students` 只输出 B 本院学生
- `vw_adapter_courses` 输出 B 课程（包含直接存储的 `hours` 和 `credits`）
- `vw_adapter_enrollments` 合并：
  - `B_SELECTION` 中的本院学生选课
  - `B_IMPORTED_SELECTION` 中的外院学生选 B 课程记录

## 10. 适配器建议查询

```sql
SELECT * FROM vw_adapter_students    ORDER BY id;
SELECT * FROM vw_adapter_courses     ORDER BY id;
SELECT * FROM vw_adapter_enrollments ORDER BY id;
```

## 11. 初始化数据约定

- 账户数：50
- 学生数：50
- 课程数：10
- 本院选课记录数：250
- 跨院导入扩展表初始化为空，留给后续联调写回使用
- 共享课程：前 6 门课程标记为共享课程（B0001~B0006）

## 12. 数据库连接信息

- 数据库：Oracle XE (XEPDB1)
- 用户名：`college_b`
- JDBC URL：`jdbc:oracle:thin:@localhost:1521/XEPDB1`
- 后端读取入口：统一访问 `vw_adapter_students` / `vw_adapter_courses` / `vw_adapter_enrollments` 三张视图，底层表保持 PDF 异构原貌。
