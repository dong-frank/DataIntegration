# 学院 A 字段映射说明

本说明对应 `database/sqlserver/init.sql`，按课本截图中的学院 A 四张基础表设计，并说明后端适配器如何把本地字段映射为项目统一领域模型字段。

## 1. 设计思路

- 学院 A 按pdf示例使用 4 张基础表：账户表、学生表、课程表、选课表。
- 本地字段命名尽量贴近示例含义，同时使用英文字段名便于 SQL Server 编写和后端 JDBC 映射。
- 适配层通过视图 `dbo.vw_adapter_students`、`dbo.vw_adapter_courses`、`dbo.vw_adapter_enrollments` 输出统一字段。
- 后端如果替换当前 `MockAcademicDataService`，可以优先直接查询这三个视图，减少业务层转换成本。

## 2. 课本表结构对应关系

| 课本表 | 本地表名 |
| --- | --- |
| 院系 A 账户表 | `dbo.A_ACCOUNT` |
| 院系 A 学生表 | `dbo.A_STUDENT` |
| 院系 A 课程表 | `dbo.A_COURSE` |
| 院系 A 选课表 | `dbo.A_SELECTION` |

## 3. 账户表说明

本地表：`dbo.A_ACCOUNT`

| 本地字段 | 对应课本字段 | 含义 |
| --- | --- | --- |
| `account_name` | 账户名 | 学生登录账号，主键 |
| `password_code` | 密码 | 当前初始化统一使用 `123456` |
| `role_code` | 权限 | 当前初始化统一使用 `STU ` |

账户表当前不直接映射到统一 `StudentRecord / CourseRecord / EnrollmentRecord`，但供学院 A 本地认证或学生账号关联使用。

## 4. 学生表映射

本地表：`dbo.A_STUDENT`

| 本地字段 | 含义 | 统一字段 | 转换规则 |
| --- | --- | --- | --- |
| `student_no` | 学号 | `id` | 直接映射，12 位字符串 |
| 常量 `'A'` | 学院标识 | `college` | 视图中固定为 `A` |
| `student_name` | 姓名 | `name` | 直接映射 |
| `gender_name` | 性别 | `gender` | 直接映射，值为 `男/女` |
| `department_name` | 院系 | `major` | 直接映射，当前统一模型中作为专业/院系字段使用 |
| `student_no` 前 4 位 | 学号前缀 | `grade` | 课本学生表没有单独“年级”字段，因此适配器约定从学号前 4 位派生，例如 `2023` |
| `linked_account` | 关联账户 | - | 不进入统一学生模型，保留给本地认证关联 |

对应统一模型：

```java
StudentRecord(id, college, name, gender, major, grade)
```

## 5. 课程表映射

本地表：`dbo.A_COURSE`

| 本地字段 | 含义 | 统一字段 | 转换规则 |
| --- | --- | --- | --- |
| `course_no` | 课程编号 | `id` | 直接映射，8 位字符串 |
| 常量 `'A'` | 开课学院 | `college` | 视图中固定为 `A` |
| `course_name` | 课程名称 | `name` | 直接映射 |
| `credit_text` | 学分 | `credits` | 课本字段类型是 `varchar(2)`，适配器中转为 `DECIMAL(3,1)` |
| `teacher_name` | 授课老师 | `teacher` | 直接映射 |
| `shared_flag` | 共享 | `shared` | `Y -> true`，`N -> false` |
| `teaching_place` | 授课地点 | - | 当前统一课程模型中没有该字段，保留在本地表中 |

对应统一模型：

```java
CourseRecord(id, college, name, credits, teacher, shared)
```

## 6. 选课表映射

本地表：`dbo.A_SELECTION`

| 本地字段 | 含义 | 统一字段 | 转换规则 |
| --- | --- | --- | --- |
| `course_no + '-' + student_no` | 组合主标识 | `id` | 课本选课表没有单独记录号，适配器以“课程编号-学号”拼接生成 |
| 常量 `'A'` | 学生所属学院 | `studentCollege` | 视图中写死为 `A` |
| `student_no` | 学生编号 | `studentId` | 直接映射 |
| 常量 `'A'` | 课程所属学院 | `courseCollege` | 视图中写死为 `A` |
| `course_no` | 课程编号 | `courseId` | 直接映射 |
| 行号派生日期 | 选课时间 | `enrolledAt` | 课本选课表没有日期字段，初始化适配视图按 `2026-03-01` 起顺序生成 |
| 常量 `'ACTIVE'` | 选课状态 | `status` | 课本选课表没有状态字段，第一阶段统一映射为 `ACTIVE` |
| `score_text` | 成绩 | - | 当前统一选课模型中没有成绩字段，保留在本地表中 |

对应统一模型：

```java
EnrollmentRecord(id, studentCollege, studentId, courseCollege, courseId, enrolledAt, status)
```

## 7. 适配器建议查询

后端实现学院 A 适配器时，建议直接查询以下视图：

```sql
SELECT * FROM dbo.vw_adapter_students;
SELECT * FROM dbo.vw_adapter_courses;
SELECT * FROM dbo.vw_adapter_enrollments;
```

如果后续需要支持跨院选课写回，建议补充一层写入规则：

- 新增选课时：向 `A_SELECTION` 插入 `(course_no, student_no, score_text)`，`score_text` 初值可约定为 `'0'` 或空成绩占位
- 退课时：课本原表无状态字段，若后续要支持真实退课，建议新增退课日志表或状态扩展表，而不是直接删除记录
- 学院 A 当前所有本地数据均归属本院，因此 `studentCollege` 与 `courseCollege` 固定为 `A`

## 8. 初始化数据约定

- 账户数：50
- 学生数：50
- 课程数：10
- 选课记录数：250，每名学生 5 门课
- 共享课程：前 6 门课程标记为共享课程
- 课程名称与当前后端 Mock 数据保持一致，方便后续替换时继续展示跨院共享课程统计
- 学号格式为“入学年份 4 位 + 顺序号 8 位”，用于从学号派生统一模型中的 `grade`
