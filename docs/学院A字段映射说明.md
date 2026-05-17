# 学院 A 字段映射说明

本说明对应 [database/sqlserver/init.sql](f:/shujujicheng/DataIntegration/database/sqlserver/init.sql:1)，按 PDF 中学院 A 的基础表结构设计，并补充统一 XML 导出与跨院写回所需的适配层约定。

## 1. 设计思路

- 学院 A 保留 PDF 里的 4 张基础表：账户表、学生表、课程表、选课表。
- 为了不破坏课本原表结构，统一接口所需的附加信息优先放在适配视图或扩展表中处理。
- 统一 JSON 领域模型和统一 XML 格式不是一回事：
  `StudentRecord / CourseRecord / EnrollmentRecord` 服务于后端与前端接口。
  `/api/xml/**` 导出则按 PDF 的统一 XML 字段格式输出。
- 学院 A 适配器准备额外补了跨院写回扩展表，支持“外院学生选 A 课程后，把学生信息和选课信息写入 A 库”。

## 2. 课本表结构对应关系

| 课本表 | 本地表名 |
| --- | --- |
| 院系 A 账户表 | `dbo.A_ACCOUNT` |
| 院系 A 学生表 | `dbo.A_STUDENT` |
| 院系 A 课程表 | `dbo.A_COURSE` |
| 院系 A 选课表 | `dbo.A_SELECTION` |

## 3. 适配器扩展表

为了满足 PDF 中“目标院系接收外院学生信息和选课信息”的流程，学院 A 在基础表之外增加两张适配层扩展表：

| 扩展表 | 作用 |
| --- | --- |
| `dbo.A_IMPORTED_STUDENT` | 保存外院导入到 A 的学生基本信息 |
| `dbo.A_IMPORTED_SELECTION` | 保存外院学生选择 A 课程后的写回选课记录 |

这样做的原因是：

- `A_SELECTION` 的 `student_no` 外键依赖 `A_STUDENT`
- 外院学生不应直接塞进本院原始学生表
- 适配层可以单独管理跨院导入数据，不污染课本原表

## 4. 学生表映射

本地表：`dbo.A_STUDENT`

| 本地字段 | 含义 | 统一 JSON 字段 | 转换规则 |
| --- | --- | --- | --- |
| `student_no` | 学号 | `id` | 直接映射，12 位字符串 |
| 常量 `'A'` | 学院标识 | `college` | 适配视图固定为 `A` |
| `student_name` | 姓名 | `name` | 直接映射 |
| `gender_name` | 性别 | `gender` | 直接映射，值为 `男/女` |
| `department_name` | 院系 | `major` | 直接映射 |
| `student_no` 前 4 位 | 入学年份 | `grade` | 从学号前 4 位派生 |
| `linked_account` | 关联账户 | - | 本地认证关联，不进入统一学生模型 |

对应统一 JSON 模型：

```java
StudentRecord(id, college, name, gender, major, grade)
```

统一 XML 学生格式：

| 统一 XML 元素 | 来源 |
| --- | --- |
| `id` | `student_no` |
| `name` | `student_name` |
| `sex` | `gender_name` |
| `major` | `department_name` |

## 5. 课程表映射

本地表：`dbo.A_COURSE`

| 本地字段 | 含义 | 统一 JSON 字段 | 转换规则 |
| --- | --- | --- | --- |
| `course_no` | 课程编号 | `id` | 直接映射 |
| 常量 `'A'` | 开课学院 | `college` | 适配视图固定为 `A` |
| `course_name` | 课程名称 | `name` | 直接映射 |
| `credit_text` | 学分 | `credits` | `varchar(2)` 转为 `DECIMAL(3,1)` |
| `credit_text` | 学分 | `hours` | A 原表没有课时，适配视图按 `学分 * 16` 派生 |
| `teacher_name` | 授课老师 | `teacher` | 直接映射 |
| `teaching_place` | 授课地点 | `location` | 直接映射 |
| `shared_flag` | 共享标记 | `shared` | `Y -> true`，`N -> false` |

对应统一 JSON 模型：

```java
CourseRecord(id, college, name, hours, credits, teacher, location, shared)
```

统一 XML 课程格式：

| 统一 XML 元素 | 来源 | 说明 |
| --- | --- | --- |
| `id` | `course_no` | 课程编号 |
| `name` | `course_name` | 课程名称 |
| `time` | `credit_text * 16` | A 原表无课时，采用派生值 |
| `score` | `credit_text` | PDF 统一课程 XML 中该元素表示学分 |
| `teacher` | `teacher_name` | 授课老师 |
| `location` | `teaching_place` | 授课地点 |

## 6. 选课表映射

本地表：`dbo.A_SELECTION`

| 本地字段 | 含义 | 统一 JSON 字段 | 转换规则 |
| --- | --- | --- | --- |
| `course_no + '-' + student_no` | 本地组合标识 | `id` | 适配视图拼接生成 |
| 常量 `'A'` | 学生所属学院 | `studentCollege` | 本院学生固定为 `A` |
| `student_no` | 学生学号 | `studentId` | 直接映射 |
| 常量 `'A'` | 课程所属学院 | `courseCollege` | A 课程固定为 `A` |
| `course_no` | 课程编号 | `courseId` | 直接映射 |
| 行号派生日期 | 选课日期 | `enrolledAt` | A 原表无日期字段，初始化视图按 `2026-03-01` 顺序派生 |
| 常量 `'ACTIVE'` | 状态 | `status` | A 原表无状态字段，第一阶段统一输出 `ACTIVE` |
| `score_text` | 成绩 | `score` | 直接映射 |

对应统一 JSON 模型：

```java
EnrollmentRecord(id, studentCollege, studentId, courseCollege, courseId, enrolledAt, status, score)
```

统一 XML 选课格式：

| 统一 XML 元素 | 来源 |
| --- | --- |
| `sid` | `student_no` |
| `cid` | `course_no` |
| `score` | `score_text` |

## 7. 跨院写回映射

目标：外院学生选择 A 的共享课程后，A 侧能够接收并持久化该学生及其选课信息。

### 7.1 外院学生信息

本地表：`dbo.A_IMPORTED_STUDENT`

| 字段 | 含义 |
| --- | --- |
| `source_college` | 学生来源学院 |
| `student_no` | 外院学号 |
| `student_name` | 外院学生姓名 |
| `gender_name` | 外院学生性别 |
| `major_name` | 外院学生专业/院系 |
| `imported_on` | 导入日期 |

### 7.2 外院选课信息

本地表：`dbo.A_IMPORTED_SELECTION`

| 字段 | 含义 |
| --- | --- |
| `course_no` | A 院课程编号 |
| `source_college` | 学生来源学院 |
| `student_no` | 外院学号 |
| `score_text` | 成绩，初始可写 `0` |
| `enrolled_on` | 选课导入日期 |
| `status_code` | 选课状态，当前约定为 `ACTIVE/WITHDRAWN` |

### 7.3 统一输出策略

- `vw_adapter_students` 仍只输出 A 本院学生
- `vw_adapter_courses` 输出 A 课程及其共享标记、地点、派生课时
- `vw_adapter_enrollments` 会合并：
  `A_SELECTION` 中的本院学生选课
  `A_IMPORTED_SELECTION` 中的外院学生选 A 课程记录

这样后续如果成员 1 接 A 适配器，A 库已经具备“本院数据 + 外院写回数据”两种落库通道。

## 8. 适配器建议查询

后端实现学院 A 适配器时，建议优先直接查询以下视图：

```sql
SELECT * FROM dbo.vw_adapter_students;
SELECT * FROM dbo.vw_adapter_courses;
SELECT * FROM dbo.vw_adapter_enrollments;
```

如果后续需要支持跨院写回，建议写入顺序如下：

1. 先校验 `course_no` 是否存在于 `A_COURSE`
2. 若学生来自外院，先把学生信息写入 `A_IMPORTED_STUDENT`
3. 再把选课信息写入 `A_IMPORTED_SELECTION`
4. 本院学生仍写入 `A_SELECTION`

## 9. 初始化数据约定

- 账户数：50
- 学生数：50
- 课程数：10
- 本院选课记录数：250
- 跨院导入扩展表初始化为空，留给后续联调写回使用
- 共享课程：前 6 门课程标记为共享课程
- 课程名称与后端当前 Mock 数据保持一致，便于后续共享课程统计演示
