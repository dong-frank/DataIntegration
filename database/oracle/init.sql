-- 学院 B / Oracle 初始化脚本
-- 用户建议名: college_b  数据库: XEPDB1 (Oracle XE 18c/21c)
-- 依据课本 PDF 表 3-6 ~ 3-9 创建:
--   1. 账户表  (PDF 表 3-6)
--   2. 学生表  (PDF 表 3-7)
--   3. 课程表  (PDF 表 3-8)
--   4. 选课表  (PDF 表 3-9)
-- 并补充跨院写回扩展表，在底表之上提供适配器视图供后端统一读取。
-- 包含 50 名学生、10 门课程、250 条选课记录。
--
-- ============================================================
-- 前置操作：以 SYSDBA 连接 XEPDB1 后执行一次：
--
--   CREATE USER college_b IDENTIFIED BY ChangeMe_123
--       DEFAULT TABLESPACE USERS
--       TEMPORARY TABLESPACE TEMP
--       QUOTA UNLIMITED ON USERS;
--   GRANT CREATE SESSION, CREATE TABLE, CREATE VIEW TO college_b;
--
-- 然后以 college_b 用户连接，再执行本脚本。
-- ============================================================

-- ============================================================
-- 第一步：清理已有对象（可重复执行）
-- ============================================================

BEGIN EXECUTE IMMEDIATE 'DROP VIEW vw_adapter_enrollments'; EXCEPTION WHEN OTHERS THEN NULL; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP VIEW vw_adapter_courses';     EXCEPTION WHEN OTHERS THEN NULL; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP VIEW vw_adapter_students';    EXCEPTION WHEN OTHERS THEN NULL; END;
/

BEGIN EXECUTE IMMEDIATE 'DROP TABLE B_IMPORTED_SELECTION';  EXCEPTION WHEN OTHERS THEN NULL; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP TABLE B_IMPORTED_STUDENT';    EXCEPTION WHEN OTHERS THEN NULL; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP TABLE B_SELECTION';           EXCEPTION WHEN OTHERS THEN NULL; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP TABLE B_ACCOUNT';             EXCEPTION WHEN OTHERS THEN NULL; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP TABLE B_COURSE';              EXCEPTION WHEN OTHERS THEN NULL; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP TABLE B_STUDENT';             EXCEPTION WHEN OTHERS THEN NULL; END;
/

-- ============================================================
-- 第二步：建表（严格遵循 PDF 类型定义）
-- ============================================================

-- 表 3-7：院系 B 学生表结构 [学号 varchar2(9), 姓名 varchar2(10), 性别 varchar2(2),
--                             专业 varchar2(16), 密码 varchar2(6)]
-- 异构点：B 的密码存在学生表中，A 的密码存在账户表中
-- Oracle 默认按字节限制 VARCHAR2，性别需要用 CHAR 语义容纳中文“男/女”
CREATE TABLE B_STUDENT (
    student_no     VARCHAR2(9)  NOT NULL,
    student_name   VARCHAR2(10) NOT NULL,
    gender         VARCHAR2(2 CHAR)  NOT NULL,
    major          VARCHAR2(16) NOT NULL,
    student_passwd VARCHAR2(6)  NOT NULL,
    CONSTRAINT PK_B_STUDENT PRIMARY KEY (student_no)
);

-- 表 3-6：院系 B 账户表结构 [账户名 varchar2(12), 密码 varchar2(12),
--                             级别 number(2), 客体 varchar2(9) FK→B_STUDENT]
-- 异构点：B 的账户表通过 客体(student_no) 指向学生，A 的学生表指向账户，方向相反
CREATE TABLE B_ACCOUNT (
    acct_name   VARCHAR2(12) NOT NULL,
    acct_passwd VARCHAR2(12) NOT NULL,
    acct_level  NUMBER(2)    NOT NULL,
    student_no  VARCHAR2(9),
    CONSTRAINT PK_B_ACCOUNT         PRIMARY KEY (acct_name),
    CONSTRAINT FK_B_ACCOUNT_STUDENT FOREIGN KEY (student_no)
        REFERENCES B_STUDENT (student_no)
);

-- 表 3-8：院系 B 课程表结构 [编号 varchar2(5), 名称 varchar2(16), 课时 varchar2(2),
--                             学分 varchar2(1), 老师 varchar2(10), 地点 varchar2(20),
--                             共享 char(1)]
-- 异构点：B 直接存储课时字段；A 无课时字段（按学分×16 推导）；C 课时为 INTEGER
-- 课程编号格式 B0001~B0010（varchar2(5)）
CREATE TABLE B_COURSE (
    course_no   VARCHAR2(5)  NOT NULL,
    course_name VARCHAR2(16) NOT NULL,
    class_hours VARCHAR2(2)  NOT NULL,
    credit_pts  VARCHAR2(1)  NOT NULL,
    teacher     VARCHAR2(10) NOT NULL,
    location    VARCHAR2(20) NOT NULL,
    shared      CHAR(1)      NOT NULL,
    CONSTRAINT PK_B_COURSE       PRIMARY KEY (course_no),
    CONSTRAINT CK_B_COURSE_SHARE CHECK (shared IN ('Y', 'N'))
);

-- 表 3-9：院系 B 选课表结构 [课程编号 varchar2(5), 学号 varchar2(9), 得分 varchar2(3)]
-- 注：PDF 将 课程编号 列为 primary key，但单课程被多名学生选择在语义上合法，
--     实际约束应为 (course_no, student_no) 联合唯一，与 A/C 的处理方式保持一致
CREATE TABLE B_SELECTION (
    course_no  VARCHAR2(5) NOT NULL,
    student_no VARCHAR2(9) NOT NULL,
    score_text VARCHAR2(3) NOT NULL,
    CONSTRAINT UQ_B_SELECTION         UNIQUE      (course_no, student_no),
    CONSTRAINT FK_B_SELECTION_COURSE  FOREIGN KEY (course_no)
        REFERENCES B_COURSE  (course_no),
    CONSTRAINT FK_B_SELECTION_STUDENT FOREIGN KEY (student_no)
        REFERENCES B_STUDENT (student_no)
);

-- 跨院写回：外院学生选择 B 院共享课程时，将学生信息写入此处
-- 不破坏 B_SELECTION → B_STUDENT 的原始外键约束
CREATE TABLE B_IMPORTED_STUDENT (
    source_college CHAR(1)      NOT NULL,
    student_no     VARCHAR2(12) NOT NULL,
    student_name   VARCHAR2(40) NOT NULL,
    gender         VARCHAR2(2 CHAR)  NOT NULL,
    major          VARCHAR2(40) NOT NULL,
    imported_on    DATE         DEFAULT TRUNC(SYSDATE) NOT NULL,
    CONSTRAINT PK_B_IMPORTED_STUDENT PRIMARY KEY (source_college, student_no),
    CONSTRAINT CK_B_IMPORTED_STU_SRC CHECK (source_college IN ('A', 'B', 'C'))
);

-- 跨院写回：外院学生选择 B 院共享课程时，将选课信息写入此处
CREATE TABLE B_IMPORTED_SELECTION (
    course_no      VARCHAR2(5)  NOT NULL,
    source_college CHAR(1)      NOT NULL,
    student_no     VARCHAR2(12) NOT NULL,
    score_text     VARCHAR2(3)  DEFAULT '0'      NOT NULL,
    enrolled_on    DATE         DEFAULT TRUNC(SYSDATE) NOT NULL,
    status_code    VARCHAR2(12) DEFAULT 'ACTIVE' NOT NULL,
    CONSTRAINT PK_B_IMPORTED_SELECTION  PRIMARY KEY (course_no, source_college, student_no),
    CONSTRAINT FK_B_IMPORTED_SEL_COURSE FOREIGN KEY (course_no)
        REFERENCES B_COURSE (course_no),
    CONSTRAINT FK_B_IMPORTED_SEL_STU    FOREIGN KEY (source_college, student_no)
        REFERENCES B_IMPORTED_STUDENT (source_college, student_no),
    CONSTRAINT CK_B_IMPORTED_SEL_STATUS CHECK (status_code IN ('ACTIVE', 'WITHDRAWN'))
);

-- ============================================================
-- 第三步：种子数据
-- ============================================================

-- 50 名学生
-- 学号格式：年份(4位) + 序号(5位，零填充) = 9位，年份按 LEVEL-1 对 3 取模轮转 2022/2023/2024
-- 示例：LEVEL=1 → '202200001'，LEVEL=2 → '202300002'，LEVEL=3 → '202400003'，
--       LEVEL=4 → '202200004' ...
INSERT INTO B_STUDENT (student_no, student_name, gender, major, student_passwd)
SELECT
    TO_CHAR(2022 + MOD(LEVEL - 1, 3)) || LPAD(TO_CHAR(LEVEL), 5, '0') AS student_no,
    'B学生' || LPAD(TO_CHAR(LEVEL), 3, '0')                            AS student_name,
    CASE WHEN MOD(LEVEL, 2) = 1 THEN '男' ELSE '女' END                AS gender,
    '学院B'                                                             AS major,
    '123456'                                                            AS student_passwd
FROM DUAL
CONNECT BY LEVEL <= 50;

-- 50 个账户（每名学生对应一个账户，客体 student_no 指向该学生的学号）
INSERT INTO B_ACCOUNT (acct_name, acct_passwd, acct_level, student_no)
SELECT
    'bacc' || LPAD(TO_CHAR(LEVEL), 8, '0')                            AS acct_name,
    '123456'                                                            AS acct_passwd,
    1                                                                   AS acct_level,
    TO_CHAR(2022 + MOD(LEVEL - 1, 3)) || LPAD(TO_CHAR(LEVEL), 5, '0') AS student_no
FROM DUAL
CONNECT BY LEVEL <= 50;

-- 10 门课程（前 6 门标记为共享，后 4 门不共享）
-- 课时 (class_hours) 按 48/64/32 轮转，学分 (credit_pts) 按 3/4/2 轮转
INSERT ALL
    INTO B_COURSE (course_no, course_name, class_hours, credit_pts, teacher, location, shared)
        VALUES ('B0001', '数据库系统', '48', '3', 'B教师01', '实验楼101', 'Y')
    INTO B_COURSE (course_no, course_name, class_hours, credit_pts, teacher, location, shared)
        VALUES ('B0002', '数据集成',   '64', '4', 'B教师02', '实验楼102', 'Y')
    INTO B_COURSE (course_no, course_name, class_hours, credit_pts, teacher, location, shared)
        VALUES ('B0003', '软件工程',   '32', '2', 'B教师03', '实验楼103', 'Y')
    INTO B_COURSE (course_no, course_name, class_hours, credit_pts, teacher, location, shared)
        VALUES ('B0004', '计算机网络', '48', '3', 'B教师04', '实验楼104', 'Y')
    INTO B_COURSE (course_no, course_name, class_hours, credit_pts, teacher, location, shared)
        VALUES ('B0005', '操作系统',   '64', '4', 'B教师05', '实验楼105', 'Y')
    INTO B_COURSE (course_no, course_name, class_hours, credit_pts, teacher, location, shared)
        VALUES ('B0006', '人工智能',   '32', '2', 'B教师06', '实验楼106', 'Y')
    INTO B_COURSE (course_no, course_name, class_hours, credit_pts, teacher, location, shared)
        VALUES ('B0007', '高等数学',   '48', '3', 'B教师07', '教学楼201', 'N')
    INTO B_COURSE (course_no, course_name, class_hours, credit_pts, teacher, location, shared)
        VALUES ('B0008', '大学英语',   '64', '4', 'B教师08', '教学楼202', 'N')
    INTO B_COURSE (course_no, course_name, class_hours, credit_pts, teacher, location, shared)
        VALUES ('B0009', '信息安全',   '32', '2', 'B教师09', '实验楼203', 'N')
    INTO B_COURSE (course_no, course_name, class_hours, credit_pts, teacher, location, shared)
        VALUES ('B0010', 'Web开发',    '48', '3', 'B教师10', '实验楼204', 'N')
SELECT 1 FROM DUAL;

-- 250 条选课记录（每名学生选 5 门课，按行号轮转遍历 10 门课程）
-- 算法：学生行号 rn 从 1..50，偏移量 offset_no 从 0..4
--       课程索引 = MOD(rn + offset_no - 1, 10) + 1 → B0001~B0010（无重复）
--       成绩 = 70 + MOD(rn + offset_no, 25) → 70~94
INSERT INTO B_SELECTION (course_no, student_no, score_text)
SELECT
    'B' || LPAD(TO_CHAR(MOD(s.rn + c.offset_no - 1, 10) + 1), 4, '0') AS course_no,
    s.student_no                                                         AS student_no,
    TO_CHAR(70 + MOD(s.rn + c.offset_no, 25))                           AS score_text
FROM (
    SELECT ROWNUM AS rn, student_no
    FROM (SELECT student_no FROM B_STUDENT ORDER BY student_no)
) s
CROSS JOIN (
    SELECT LEVEL - 1 AS offset_no FROM DUAL CONNECT BY LEVEL <= 5
) c;

COMMIT;

-- ============================================================
-- 第四步：索引
-- ============================================================

CREATE INDEX IX_B_SELECTION_STUDENT    ON B_SELECTION          (student_no);
CREATE INDEX IX_B_SELECTION_COURSE     ON B_SELECTION          (course_no);
CREATE INDEX IX_B_IMPORTED_SEL_STUDENT ON B_IMPORTED_SELECTION (student_no);
CREATE INDEX IX_B_IMPORTED_SEL_COURSE  ON B_IMPORTED_SELECTION (course_no);

-- ============================================================
-- 第五步：适配器视图
-- 字段口径与后端 StudentRecord / CourseRecord / EnrollmentRecord 保持一致：
--   学生：id, college, name, gender, major, grade
--   课程：id, college, name, hours, credits, teacher, location, shared
--   选课：id, studentCollege, studentId, courseCollege, courseId,
--         enrolledAt, status, score
-- 映射依据 PDF 表 3-17 / 3-18 / 3-19
-- ============================================================

-- 学生视图
-- id ← student_no (PDF: 学号 → 统一 id)
-- grade ← 学号前 4 位 (入学年份，与 A/C 派生规则一致)
CREATE OR REPLACE VIEW vw_adapter_students AS
SELECT
    student_no                          AS id,
    'B'                                 AS college,
    student_name                        AS name,
    gender                              AS gender,
    major                               AS major,
    TO_NUMBER(SUBSTR(student_no, 1, 4)) AS grade
FROM B_STUDENT;

-- 课程视图
-- id      ← course_no   (PDF: 编号 → 统一 id)
-- name    ← course_name (PDF: 名称 → 统一 name)
-- hours   ← class_hours (PDF: 课时；B 直接存储，不同于 A 按学分×16 推导)
-- credits ← credit_pts  (PDF: 学分 → 统一 score/credits)
-- teacher ← teacher     (PDF: 老师 → 统一 teacher)
-- location← location    (PDF: 地点 → 统一 location)
-- shared  ← shared='Y'→1 / 'N'→0
CREATE OR REPLACE VIEW vw_adapter_courses AS
SELECT
    course_no                                    AS id,
    'B'                                          AS college,
    course_name                                  AS name,
    TO_NUMBER(class_hours)                       AS hours,
    CAST(TO_NUMBER(credit_pts) AS NUMBER(3, 1))  AS credits,
    teacher                                      AS teacher,
    location                                     AS location,
    CASE WHEN shared = 'Y' THEN 1 ELSE 0 END     AS shared
FROM B_COURSE;

-- 选课视图
-- 本院本院选课（B_SELECTION）与外院学生跨院写回（B_IMPORTED_SELECTION）合并输出
-- sid ← student_no (PDF: 学生编号 → 统一 sid)
-- cid ← course_no  (PDF: 课程编号 → 统一 cid)
-- score ← score_text (PDF: 得分 → 统一 score)
-- enrolledAt 本院按行号从 2026-03-01 顺延；外院记录取实际写回日期
CREATE OR REPLACE VIEW vw_adapter_enrollments AS
SELECT
    course_no || '-' || student_no                                                             AS id,
    'B'                                                                                        AS studentCollege,
    student_no                                                                                 AS studentId,
    'B'                                                                                        AS courseCollege,
    course_no                                                                                  AS courseId,
    TO_DATE('2026-03-01', 'YYYY-MM-DD')
        + ROW_NUMBER() OVER (ORDER BY student_no, course_no) - 1                              AS enrolledAt,
    'ACTIVE'                                                                                   AS status,
    score_text                                                                                 AS score
FROM B_SELECTION
UNION ALL
SELECT
    course_no || '-' || student_no   AS id,
    source_college                   AS studentCollege,
    student_no                       AS studentId,
    'B'                              AS courseCollege,
    course_no                        AS courseId,
    enrolled_on                      AS enrolledAt,
    status_code                      AS status,
    score_text                       AS score
FROM B_IMPORTED_SELECTION;

-- ============================================================
-- 验证：预期 account_count=50, student_count=50,
--             course_count=10,  selection_count=250
-- ============================================================

SELECT
    (SELECT COUNT(*) FROM B_ACCOUNT)   AS account_count,
    (SELECT COUNT(*) FROM B_STUDENT)   AS student_count,
    (SELECT COUNT(*) FROM B_COURSE)    AS course_count,
    (SELECT COUNT(*) FROM B_SELECTION) AS selection_count
FROM DUAL;
