-- 学院 A / SQL Server 初始化脚本
-- 数据库建议名: college_a
-- 依据课本示例表结构创建:
-- 1. 账户表
-- 2. 学生表
-- 3. 课程表
-- 4. 选课表
-- 并额外提供适配器视图，供后端统一读取。

IF DB_ID(N'college_a') IS NULL
BEGIN
    CREATE DATABASE college_a;
END;
GO

USE college_a;
GO

IF OBJECT_ID(N'dbo.vw_adapter_enrollments', N'V') IS NOT NULL DROP VIEW dbo.vw_adapter_enrollments;
IF OBJECT_ID(N'dbo.vw_adapter_courses', N'V') IS NOT NULL DROP VIEW dbo.vw_adapter_courses;
IF OBJECT_ID(N'dbo.vw_adapter_students', N'V') IS NOT NULL DROP VIEW dbo.vw_adapter_students;
GO

IF OBJECT_ID(N'dbo.A_IMPORTED_SELECTION', N'U') IS NOT NULL DROP TABLE dbo.A_IMPORTED_SELECTION;
IF OBJECT_ID(N'dbo.A_IMPORTED_STUDENT', N'U') IS NOT NULL DROP TABLE dbo.A_IMPORTED_STUDENT;
IF OBJECT_ID(N'dbo.A_SELECTION', N'U') IS NOT NULL DROP TABLE dbo.A_SELECTION;
IF OBJECT_ID(N'dbo.A_COURSE', N'U') IS NOT NULL DROP TABLE dbo.A_COURSE;
IF OBJECT_ID(N'dbo.A_STUDENT', N'U') IS NOT NULL DROP TABLE dbo.A_STUDENT;
IF OBJECT_ID(N'dbo.A_ACCOUNT', N'U') IS NOT NULL DROP TABLE dbo.A_ACCOUNT;
GO

-- 表 3-2: 院系 A 账户表结构[账户名，密码，权限]
CREATE TABLE dbo.A_ACCOUNT (
    account_name VARCHAR(10) NOT NULL PRIMARY KEY,
    password_code VARCHAR(6) NOT NULL,
    role_code CHAR(4) NOT NULL
);
GO

-- 表 3-3: 院系 A 学生表结构[学号，姓名，性别，院系，关联账户]
CREATE TABLE dbo.A_STUDENT (
    student_no VARCHAR(12) NOT NULL PRIMARY KEY,
    student_name NVARCHAR(10) NOT NULL,
    gender_name NVARCHAR(2) NOT NULL,
    department_name NVARCHAR(10) NOT NULL,
    linked_account VARCHAR(10) NOT NULL,
    CONSTRAINT FK_A_STUDENT_ACCOUNT
        FOREIGN KEY (linked_account) REFERENCES dbo.A_ACCOUNT (account_name)
);
GO

-- 表 3-4: 院系 A 课程表结构[课程编号，课程名称，学分，授课老师，授课地点，共享]
CREATE TABLE dbo.A_COURSE (
    course_no VARCHAR(8) NOT NULL PRIMARY KEY,
    course_name NVARCHAR(10) NOT NULL,
    credit_text VARCHAR(2) NOT NULL,
    teacher_name NVARCHAR(10) NOT NULL,
    teaching_place NVARCHAR(20) NOT NULL,
    shared_flag CHAR(1) NOT NULL,
    CONSTRAINT CK_A_COURSE_SHARED CHECK (shared_flag IN ('Y', 'N'))
);
GO

-- 表 3-5: 院系 A 选课表结构[课程编号，学生编号，成绩]
CREATE TABLE dbo.A_SELECTION (
    course_no VARCHAR(8) NOT NULL,
    student_no VARCHAR(12) NOT NULL,
    score_text VARCHAR(3) NOT NULL,
    CONSTRAINT UQ_A_SELECTION UNIQUE (course_no, student_no),
    CONSTRAINT FK_A_SELECTION_COURSE
        FOREIGN KEY (course_no) REFERENCES dbo.A_COURSE (course_no),
    CONSTRAINT FK_A_SELECTION_STUDENT
        FOREIGN KEY (student_no) REFERENCES dbo.A_STUDENT (student_no)
);
GO

-- 跨院选课导入的外院学生信息
CREATE TABLE dbo.A_IMPORTED_STUDENT (
    source_college CHAR(1) NOT NULL,
    student_no VARCHAR(12) NOT NULL,
    student_name NVARCHAR(40) NOT NULL,
    gender_name NVARCHAR(2) NOT NULL,
    major_name NVARCHAR(40) NOT NULL,
    imported_on DATE NOT NULL CONSTRAINT DF_A_IMPORTED_STUDENT_IMPORTED_ON DEFAULT (CONVERT(DATE, GETDATE())),
    CONSTRAINT PK_A_IMPORTED_STUDENT PRIMARY KEY (source_college, student_no),
    CONSTRAINT CK_A_IMPORTED_STUDENT_SOURCE CHECK (source_college IN ('A', 'B', 'C'))
);
GO

-- 跨院选课导入的选课信息
CREATE TABLE dbo.A_IMPORTED_SELECTION (
    course_no VARCHAR(8) NOT NULL,
    source_college CHAR(1) NOT NULL,
    student_no VARCHAR(12) NOT NULL,
    score_text VARCHAR(3) NOT NULL CONSTRAINT DF_A_IMPORTED_SELECTION_SCORE DEFAULT ('0'),
    enrolled_on DATE NOT NULL CONSTRAINT DF_A_IMPORTED_SELECTION_ENROLLED_ON DEFAULT (CONVERT(DATE, GETDATE())),
    status_code VARCHAR(12) NOT NULL CONSTRAINT DF_A_IMPORTED_SELECTION_STATUS DEFAULT ('ACTIVE'),
    CONSTRAINT PK_A_IMPORTED_SELECTION PRIMARY KEY (course_no, source_college, student_no),
    CONSTRAINT FK_A_IMPORTED_SELECTION_COURSE
        FOREIGN KEY (course_no) REFERENCES dbo.A_COURSE (course_no),
    CONSTRAINT FK_A_IMPORTED_SELECTION_STUDENT
        FOREIGN KEY (source_college, student_no) REFERENCES dbo.A_IMPORTED_STUDENT (source_college, student_no),
    CONSTRAINT CK_A_IMPORTED_SELECTION_STATUS CHECK (status_code IN ('ACTIVE', 'WITHDRAWN'))
);
GO

WITH numbers AS (
    SELECT 1 AS n
    UNION ALL
    SELECT n + 1
    FROM numbers
    WHERE n < 50
)
INSERT INTO dbo.A_ACCOUNT (account_name, password_code, role_code)
SELECT
    CONCAT('acc', RIGHT(CONCAT('0000000', n), 7)),
    '123456',
    'STU '
FROM numbers
OPTION (MAXRECURSION 50);
GO

WITH numbers AS (
    SELECT 1 AS n
    UNION ALL
    SELECT n + 1
    FROM numbers
    WHERE n < 50
)
INSERT INTO dbo.A_STUDENT (student_no, student_name, gender_name, department_name, linked_account)
SELECT
    CONCAT(
        CAST(2022 + (n % 3) AS VARCHAR(4)),
        RIGHT(CONCAT('00000000', n), 8)
    ),
    CONCAT(N'A', RIGHT(CONCAT('000000000', n), 9)),
    CASE WHEN n % 2 = 0 THEN N'女' ELSE N'男' END,
    N'学院A',
    CONCAT('acc', RIGHT(CONCAT('0000000', n), 7))
FROM numbers
OPTION (MAXRECURSION 50);
GO

INSERT INTO dbo.A_COURSE (course_no, course_name, credit_text, teacher_name, teaching_place, shared_flag)
VALUES
    ('A0000001', N'数据库系统', '3', N'A教师01', N'实验楼101', 'Y'),
    ('A0000002', N'数据集成', '4', N'A教师02', N'实验楼102', 'Y'),
    ('A0000003', N'软件工程', '2', N'A教师03', N'实验楼103', 'Y'),
    ('A0000004', N'计算机网络', '3', N'A教师04', N'实验楼104', 'Y'),
    ('A0000005', N'操作系统', '4', N'A教师05', N'实验楼105', 'Y'),
    ('A0000006', N'人工智能', '2', N'A教师06', N'实验楼106', 'Y'),
    ('A0000007', N'高等数学', '3', N'A教师07', N'教学楼201', 'N'),
    ('A0000008', N'大学英语', '4', N'A教师08', N'教学楼202', 'N'),
    ('A0000009', N'信息安全', '2', N'A教师09', N'实验楼203', 'N'),
    ('A0000010', N'Web开发', '3', N'A教师10', N'实验楼204', 'N');
GO

WITH students AS (
    SELECT ROW_NUMBER() OVER (ORDER BY student_no) AS student_seq, student_no
    FROM dbo.A_STUDENT
),
course_offsets AS (
    SELECT 0 AS offset_no
    UNION ALL SELECT 1
    UNION ALL SELECT 2
    UNION ALL SELECT 3
    UNION ALL SELECT 4
)
INSERT INTO dbo.A_SELECTION (course_no, student_no, score_text)
SELECT
    CONCAT('A', RIGHT(CONCAT('0000000', (((student_seq + offset_no - 1) % 10) + 1)), 7)),
    student_no,
    CAST(70 + ((student_seq + offset_no) % 25) AS VARCHAR(3))
FROM students
CROSS JOIN course_offsets;
GO

CREATE INDEX IX_A_SELECTION_STUDENT_NO ON dbo.A_SELECTION (student_no);
CREATE INDEX IX_A_SELECTION_COURSE_NO ON dbo.A_SELECTION (course_no);
CREATE INDEX IX_A_IMPORTED_SELECTION_STUDENT_NO ON dbo.A_IMPORTED_SELECTION (student_no);
CREATE INDEX IX_A_IMPORTED_SELECTION_COURSE_NO ON dbo.A_IMPORTED_SELECTION (course_no);
GO

CREATE VIEW dbo.vw_adapter_students
AS
SELECT
    student_no AS id,
    'A' AS college,
    student_name AS name,
    gender_name AS gender,
    department_name AS major,
    CAST(LEFT(student_no, 4) AS INT) AS grade
FROM dbo.A_STUDENT;
GO

CREATE VIEW dbo.vw_adapter_courses
AS
SELECT
    course_no AS id,
    'A' AS college,
    course_name AS name,
    CAST(CAST(credit_text AS TINYINT) * 16 AS TINYINT) AS hours,
    CAST(credit_text AS DECIMAL(3, 1)) AS credits,
    teacher_name AS teacher,
    teaching_place AS location,
    CAST(CASE WHEN shared_flag = 'Y' THEN 1 ELSE 0 END AS BIT) AS shared
FROM dbo.A_COURSE;
GO

CREATE VIEW dbo.vw_adapter_enrollments
AS
SELECT
    CONCAT(course_no, '-', student_no) AS id,
    'A' AS studentCollege,
    student_no AS studentId,
    'A' AS courseCollege,
    course_no AS courseId,
    DATEADD(DAY, ROW_NUMBER() OVER (ORDER BY student_no, course_no) - 1, CONVERT(DATE, '2026-03-01')) AS enrolledAt,
    'ACTIVE' AS status,
    score_text AS score
FROM dbo.A_SELECTION
UNION ALL
SELECT
    CONCAT(course_no, '-', student_no) AS id,
    source_college AS studentCollege,
    student_no AS studentId,
    'A' AS courseCollege,
    course_no AS courseId,
    enrolled_on AS enrolledAt,
    status_code AS status,
    score_text AS score
FROM dbo.A_IMPORTED_SELECTION;
GO

SELECT
    (SELECT COUNT(*) FROM dbo.A_ACCOUNT) AS account_count,
    (SELECT COUNT(*) FROM dbo.A_STUDENT) AS student_count,
    (SELECT COUNT(*) FROM dbo.A_COURSE) AS course_count,
    (SELECT COUNT(*) FROM dbo.A_SELECTION) AS selection_count;
GO
