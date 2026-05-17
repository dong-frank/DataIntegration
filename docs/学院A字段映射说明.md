# 学院 A 字段映射说明

本说明对应 `database/sqlserver/init.sql`，按 PDF 中学院 A 的四张基础表设计，并补充统一 JSON 模型、统一 XML 格式以及跨院写回到学院 A 时的适配规则。

## 1. 设计思路

- 学院 A 保留 PDF 里的 4 张基础表：账户表、学生表、课程表、选课表。
- 统一 JSON 模型服务于后端接口和前端页面。
- 统一 XML 按 PDF 表 3-13、3-14、3-15 输出。
- 外院学生选 A 课程时，不直接写入 `A_STUDENT`，而是通过扩展导入表完成写回，避免破坏原始本院外键结构。

## 2. 课本表结构对应关系

| 课本表 | 本地表名 |
| --- | --- |
| 院系 A 账户表 | `dbo.A_ACCOUNT` |
| 院系 A 学生表 | `dbo.A_STUDENT` |
| 院系 A 课程表 | `dbo.A_COURSE` |
| 院系 A 选课表 | `dbo.A_SELECTION` |

## 3. 跨院写回扩展表

| 扩展表 | 作用 |
| --- | --- |
| `dbo.A_IMPORTED_STUDENT` | 保存外院导入到 A 的学生基本信息 |
| `dbo.A_IMPORTED_SELECTION` | 保存外院学生选择 A 课程后的写回选课记录 |

## 4. 学生表映射

本地表：`dbo.A_STUDENT`

| 本地字段 | 含义 | 统一 JSON 字段 | 转换规则 |
| --- | --- | --- | --- |
| `student_no` | 学号 | `id` | 直接映射 |
| 常量 `'A'` | 学院标识 | `college` | 适配视图固定为 `A` |
| `student_name` | 姓名 | `name` | 直接映射 |
| `gender_name` | 性别 | `gender` | 直接映射，值为 `男/女` |
| `department_name` | 院系 | `major` | 直接映射 |
| `student_no` 前 4 位 | 入学年份 | `grade` | 从学号前 4 位派生 |

对应统一 JSON 模型：

```java
StudentRecord(id, college, name, gender, major, grade)
```

对应统一 XML 学生格式：

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
| `credit_text` | 学分 | `hours` | A 原表没有课时字段，约定按 `学分 * 16` 派生 |
| `teacher_name` | 授课老师 | `teacher` | 直接映射 |
| `teaching_place` | 授课地点 | `location` | 直接映射 |
| `shared_flag` | 共享标记 | `shared` | `Y -> true`，`N -> false` |

对应统一 JSON 模型：

```java
CourseRecord(id, college, name, hours, credits, teacher, location, shared)
```

对应统一 XML 课程格式：

| 统一 XML 元素 | 来源 | 说明 |
| --- | --- | --- |
| `id` | `course_no` | 课程编号 |
| `name` | `course_name` | 课程名称 |
| `time` | `credit_text * 16` | PDF 中为课时 |
| `score` | `credit_text` | PDF 中课程 XML 的 `score` 表示学分 |
| `teacher` | `teacher_name` | 授课老师 |
| `location` | `teaching_place` | 授课地点 |

## 6. 选课表映射

本地表：`dbo.A_SELECTION`

| 本地字段 | 含义 | 统一 JSON 字段 | 转换规则 |
| --- | --- | --- | --- |
| `course_no + '-' + student_no` | 组合标识 | `id` | 适配视图拼接生成 |
| 常量 `'A'` | 学生所属学院 | `studentCollege` | 本院学生固定为 `A` |
| `student_no` | 学生学号 | `studentId` | 直接映射 |
| 常量 `'A'` | 课程所属学院 | `courseCollege` | A 课程固定为 `A` |
| `course_no` | 课程编号 | `courseId` | 直接映射 |
| 行号派生日期 | 选课日期 | `enrolledAt` | A 原表无日期字段，按初始化顺序派生 |
| 常量 `'ACTIVE'` | 选课状态 | `status` | A 原表无状态字段，统一输出 `ACTIVE` |
| `score_text` | 成绩 | `score` | 直接映射 |

对应统一 JSON 模型：

```java
EnrollmentRecord(id, studentCollege, studentId, courseCollege, courseId, enrolledAt, status, score)
```

对应统一 XML 选课格式：

| 统一 XML 元素 | 来源 |
| --- | --- |
| `sid` | `student_no` |
| `cid` | `course_no` |
| `score` | `score_text` |

## 7. 跨院写回规则

目标：外院学生选择 A 的共享课程后，A 侧能把学生信息和选课信息写入本院数据库。

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
| `score_text` | 成绩，初始写 `0` |
| `enrolled_on` | 选课写回日期 |
| `status_code` | 状态，当前约定为 `ACTIVE/WITHDRAWN` |

### 7.3 统一输出策略

- `vw_adapter_students` 只输出 A 本院学生
- `vw_adapter_courses` 输出 A 课程以及派生课时和授课地点
- `vw_adapter_enrollments` 合并：
  `A_SELECTION` 中的本院学生选课
  `A_IMPORTED_SELECTION` 中的外院学生选 A 课程记录

## 8. 适配器建议查询

```sql
SELECT * FROM dbo.vw_adapter_students;
SELECT * FROM dbo.vw_adapter_courses;
SELECT * FROM dbo.vw_adapter_enrollments;
```

## 9. 初始化数据约定

- 账户数：50
- 学生数：50
- 课程数：10
- 本院选课记录数：250
- 跨院导入扩展表初始化为空，留给后续联调写回使用
- 共享课程：前 6 门课程标记为共享课程
