#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
学院 C MySQL 数据库初始化脚本生成器
依据 PDF《基于 XML 数据集成的集成教务系统示例》表 3-11 / 3-12 风格生成:
  - C_STUDENT  (Sno/Snm/Sex/Sde/Pwd)
  - C_COURSE   (Cno/Cnm/Ctm/Cpt/Tec/Pla/Share)
  - C_SELECTION(Cno/Sno/Grd)
并附带适配视图 vw_adapter_students / vw_adapter_courses / vw_adapter_enrollments。
共 50 名学生、10 门课程、250 条选课记录。
"""

COURSE_NAMES = [
    "数据库系统", "数据集成", "软件工程", "计算机网络", "操作系统",
    "人工智能", "高等数学", "大学英语", "信息安全", "Web开发",
]

PLACES = [
    "实验楼101", "实验楼102", "实验楼103", "实验楼104", "实验楼105",
    "实验楼106", "教学楼201", "教学楼202", "实验楼203", "实验楼204",
]


def generate_students():
    students = []
    for i in range(1, 51):
        year = 2022 + (i % 3)
        students.append({
            "Sno": f"{year}{i:05d}",  # 9 位
            "Snm": f"学生{i:03d}",
            "Sex": "女" if i % 2 == 0 else "男",
            "Sde": "学院C",
            "Pwd": "123456",
        })
    return students


def generate_courses():
    courses = []
    for i in range(1, 11):
        courses.append({
            "Cno": f"C{i:03d}",  # 4 位 (CHAR(4))
            "Cnm": COURSE_NAMES[i - 1],
            "Ctm": 32 + (i % 3) * 16,
            "Cpt": 2 + (i % 3),
            "Tec": f"C教师{i:02d}",
            "Pla": PLACES[i - 1],
            "Share": "Y" if i <= 6 else "N",
        })
    return courses


def generate_selections(students, courses):
    selections = []
    for si, s in enumerate(students):
        for j in range(5):
            ci = (si + j) % len(courses)
            selections.append({
                "Cno": courses[ci]["Cno"],
                "Sno": s["Sno"],
                "Grd": 70 + ((si + j) * 7) % 25,
            })
    return selections


def generate_sql():
    students = generate_students()
    courses = generate_courses()
    selections = generate_selections(students, courses)

    out = []

    def w(line=""):
        out.append(line)

    w("-- 学院 C / MySQL 初始化脚本")
    w("-- 数据库建议名: college_c")
    w("-- 底层表严格遵循 PDF 表 3-11 / 3-12 风格 (Sno/Snm/Sex/Sde/Pwd, Cno/Cnm/Ctm/Cpt/Tec/Pla/Share, Cno/Sno/Grd)")
    w("-- 包含 50 名学生、10 门课程、250 条选课记录")
    w("-- 在底表之上额外提供适配器视图 vw_adapter_students / vw_adapter_courses / vw_adapter_enrollments，供后端统一读取")
    w("")
    w("CREATE DATABASE IF NOT EXISTS college_c CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
    w("USE college_c;")
    w("")
    w("-- 清理已有视图与表，便于重复执行")
    w("DROP VIEW IF EXISTS vw_adapter_enrollments;")
    w("DROP VIEW IF EXISTS vw_adapter_courses;")
    w("DROP VIEW IF EXISTS vw_adapter_students;")
    w("DROP TABLE IF EXISTS C_IMPORTED_SELECTION;")
    w("DROP TABLE IF EXISTS C_IMPORTED_STUDENT;")
    w("DROP TABLE IF EXISTS C_SELECTION;")
    w("DROP TABLE IF EXISTS C_COURSE;")
    w("DROP TABLE IF EXISTS C_STUDENT;")
    w("")
    w("-- 表 3-11: 院系 C 学生表结构 [Sno 学号, Snm 姓名, Sex 性别, Sde 院系, Pwd 密码]")
    w("CREATE TABLE C_STUDENT (")
    w("    Sno VARCHAR(9)  NOT NULL PRIMARY KEY COMMENT '学号',")
    w("    Snm VARCHAR(10) NOT NULL              COMMENT '姓名',")
    w("    Sex VARCHAR(1)  NOT NULL              COMMENT '性别',")
    w("    Sde VARCHAR(6)  NOT NULL              COMMENT '院系',")
    w("    Pwd CHAR(6)     NOT NULL              COMMENT '密码'")
    w(") COMMENT '院系C学生表 (PDF 表3-11)';")
    w("")
    w("-- 表 3-12: 院系 C 课程表结构 [Cno 课程编号, Cnm 课程名称, Ctm 课时, Cpt 学分, Tec 授课老师, Pla 授课地点, Share 共享]")
    w("CREATE TABLE C_COURSE (")
    w("    Cno   CHAR(4)     NOT NULL PRIMARY KEY COMMENT '课程编号',")
    w("    Cnm   VARCHAR(10) NOT NULL              COMMENT '课程名称',")
    w("    Ctm   INTEGER     NOT NULL              COMMENT '课时',")
    w("    Cpt   INTEGER     NOT NULL              COMMENT '学分',")
    w("    Tec   VARCHAR(20) NOT NULL              COMMENT '授课老师',")
    w("    Pla   VARCHAR(18) NOT NULL              COMMENT '授课地点',")
    w("    Share CHAR(1)     NOT NULL              COMMENT '共享标记',")
    w("    CONSTRAINT CK_C_COURSE_SHARE CHECK (Share IN ('Y','N'))")
    w(") COMMENT '院系C课程表 (PDF 表3-12)';")
    w("")
    w("-- 表 3-11 (选课): 院系 C 选课表结构 [Cno 课程编号, Sno 学号, Grd 成绩]")
    w("CREATE TABLE C_SELECTION (")
    w("    Cno CHAR(4)  NOT NULL COMMENT '课程编号',")
    w("    Sno CHAR(9)  NOT NULL COMMENT '学号',")
    w("    Grd INTEGER  NOT NULL COMMENT '成绩',")
    w("    CONSTRAINT UQ_C_SELECTION UNIQUE (Cno, Sno),")
    w("    CONSTRAINT FK_C_SELECTION_COURSE  FOREIGN KEY (Cno) REFERENCES C_COURSE  (Cno),")
    w("    CONSTRAINT FK_C_SELECTION_STUDENT FOREIGN KEY (Sno) REFERENCES C_STUDENT (Sno)")
    w(") COMMENT '院系C选课表 (PDF 表3-11 选课)';")
    w("")
    w("-- 跨院选课导入的外院学生信息")
    w("CREATE TABLE C_IMPORTED_STUDENT (")
    w("    source_college CHAR(1)     NOT NULL COMMENT '来源学院',")
    w("    student_no     VARCHAR(20) NOT NULL COMMENT '外院学号',")
    w("    student_name   VARCHAR(40) NOT NULL COMMENT '外院学生姓名',")
    w("    gender_name    VARCHAR(2)  NOT NULL COMMENT '性别',")
    w("    major_name     VARCHAR(40) NOT NULL COMMENT '院系/专业',")
    w("    imported_on    DATE        NOT NULL COMMENT '导入日期',")
    w("    CONSTRAINT PK_C_IMPORTED_STUDENT PRIMARY KEY (source_college, student_no),")
    w("    CONSTRAINT CK_C_IMPORTED_STUDENT_SOURCE CHECK (source_college IN ('A','B','C'))")
    w(") COMMENT '院系C跨院导入学生表';")
    w("")
    w("-- 跨院选课导入的选课信息")
    w("CREATE TABLE C_IMPORTED_SELECTION (")
    w("    Cno            CHAR(4)     NOT NULL COMMENT '课程编号',")
    w("    source_college CHAR(1)     NOT NULL COMMENT '来源学院',")
    w("    student_no     VARCHAR(20) NOT NULL COMMENT '外院学号',")
    w("    Grd            INTEGER     NOT NULL DEFAULT 0 COMMENT '成绩',")
    w("    enrolled_on    DATE        NOT NULL COMMENT '选课日期',")
    w("    status_code    VARCHAR(12) NOT NULL DEFAULT 'ACTIVE' COMMENT '选课状态',")
    w("    CONSTRAINT PK_C_IMPORTED_SELECTION PRIMARY KEY (Cno, source_college, student_no),")
    w("    CONSTRAINT FK_C_IMPORTED_SELECTION_COURSE FOREIGN KEY (Cno) REFERENCES C_COURSE (Cno),")
    w("    CONSTRAINT FK_C_IMPORTED_SELECTION_STUDENT FOREIGN KEY (source_college, student_no)")
    w("        REFERENCES C_IMPORTED_STUDENT (source_college, student_no),")
    w("    CONSTRAINT CK_C_IMPORTED_SELECTION_STATUS CHECK (status_code IN ('ACTIVE','WITHDRAWN'))")
    w(") COMMENT '院系C跨院导入选课表';")
    w("")
    w("-- 学生数据 (50 名)")
    w("INSERT INTO C_STUDENT (Sno, Snm, Sex, Sde, Pwd) VALUES")
    for i, s in enumerate(students):
        end = "," if i < len(students) - 1 else ";"
        w(f"    ('{s['Sno']}', '{s['Snm']}', '{s['Sex']}', '{s['Sde']}', '{s['Pwd']}'){end}")
    w("")
    w("-- 课程数据 (10 门)")
    w("INSERT INTO C_COURSE (Cno, Cnm, Ctm, Cpt, Tec, Pla, Share) VALUES")
    for i, c in enumerate(courses):
        end = "," if i < len(courses) - 1 else ";"
        w(f"    ('{c['Cno']}', '{c['Cnm']}', {c['Ctm']}, {c['Cpt']}, '{c['Tec']}', '{c['Pla']}', '{c['Share']}'){end}")
    w("")
    w("-- 选课数据 (250 条)")
    w("INSERT INTO C_SELECTION (Cno, Sno, Grd) VALUES")
    for i, e in enumerate(selections):
        end = "," if i < len(selections) - 1 else ";"
        w(f"    ('{e['Cno']}', '{e['Sno']}', {e['Grd']}){end}")
    w("")
    w("-- 适配器视图：将底层 PDF 字段统一映射为后端期望的字段名")
    w("-- 字段映射 (依据 PDF 表 3-17/3-18/3-19): id <- Sno/Cno, name <- Snm/Cnm, score/credits <- Grd/Cpt, teacher <- Tec, location <- Pla")
    w("CREATE VIEW vw_adapter_students AS")
    w("SELECT")
    w("    Sno                                  AS id,")
    w("    'C'                                  AS college,")
    w("    Snm                                  AS name,")
    w("    Sex                                  AS gender,")
    w("    Sde                                  AS major,")
    w("    CAST(LEFT(Sno, 4) AS UNSIGNED)       AS grade")
    w("FROM C_STUDENT;")
    w("")
    w("CREATE VIEW vw_adapter_courses AS")
    w("SELECT")
    w("    Cno                                  AS id,")
    w("    'C'                                  AS college,")
    w("    Cnm                                  AS name,")
    w("    Ctm                                  AS hours,")
    w("    CAST(Cpt AS DECIMAL(3,1))            AS credits,")
    w("    Tec                                  AS teacher,")
    w("    Pla                                  AS location,")
    w("    (CASE WHEN Share = 'Y' THEN 1 ELSE 0 END) AS shared")
    w("FROM C_COURSE;")
    w("")
    w("CREATE VIEW vw_adapter_enrollments AS")
    w("SELECT")
    w("    CONCAT(Cno, '-', Sno)                AS id,")
    w("    'C'                                  AS studentCollege,")
    w("    Sno                                  AS studentId,")
    w("    'C'                                  AS courseCollege,")
    w("    Cno                                  AS courseId,")
    w("    DATE_ADD('2026-03-01', INTERVAL (CAST(SUBSTRING(Cno, 2) AS UNSIGNED) - 1) DAY) AS enrolledAt,")
    w("    'ACTIVE'                             AS status,")
    w("    Grd                                  AS score")
    w("FROM C_SELECTION")
    w("UNION ALL")
    w("SELECT")
    w("    CONCAT(Cno, '-', student_no)          AS id,")
    w("    source_college                       AS studentCollege,")
    w("    student_no                           AS studentId,")
    w("    'C'                                  AS courseCollege,")
    w("    Cno                                  AS courseId,")
    w("    enrolled_on                          AS enrolledAt,")
    w("    status_code                          AS status,")
    w("    Grd                                  AS score")
    w("FROM C_IMPORTED_SELECTION;")
    w("")
    w("-- 数据导入完成")

    return "\n".join(out) + "\n"


if __name__ == "__main__":
    import os
    sql = generate_sql()
    output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "init.sql")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(sql)
    print(f"SQL 脚本已生成: {output_file}")
