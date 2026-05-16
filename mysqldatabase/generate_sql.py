#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
学院 C MySQL 数据库初始化脚本生成器
生成包含 50 名学生、10 门课程、250 条选课记录的完整 SQL
"""

import datetime

COURSE_NAMES = [
    "数据库系统", "数据集成", "软件工程", "计算机网络", "操作系统",
    "人工智能", "高等数学", "大学英语", "信息安全", "Web开发"
]


def generate_students():
    students = []
    for i in range(1, 51):
        student = {
            "id": f"C-S{i:03d}",
            "college_code": "C",
            "name": f"学院C学生{i:03d}",
            "gender": "女" if i % 2 == 0 else "男",
            "major": "学院C教学管理",
            "grade": 2022 + (i % 3)
        }
        students.append(student)
    return students


def generate_courses():
    courses = []
    for i in range(1, 11):
        course = {
            "id": f"C-C{i:03d}",
            "college_code": "C",
            "name": COURSE_NAMES[i - 1],
            "credits": 2.0 + (i % 3),
            "teacher": f"学院C教师{i:02d}",
            "shared": i <= 6  # 前6门课为共享课程
        }
        courses.append(course)
    return courses


def generate_enrollments(students, courses):
    enrollments = []
    counter = 1
    for student_idx, student in enumerate(students):
        for j in range(5):  # 每个学生选5门课
            course_idx = (student_idx + j) % len(courses)
            course = courses[course_idx]
            enrollment = {
                "id": f"C-E{counter:04d}",
                "student_college": "C",
                "student_id": student["id"],
                "course_college": "C",
                "course_id": course["id"],
                "enrolled_at": datetime.date(2026, 3, 1) + datetime.timedelta(days=j),
                "status": "ACTIVE"
            }
            enrollments.append(enrollment)
            counter += 1
    return enrollments


def generate_sql():
    students = generate_students()
    courses = generate_courses()
    enrollments = generate_enrollments(students, courses)

    sql_content = []
    sql_content.append("-- 学院 C / MySQL 初始化脚本")
    sql_content.append("-- 数据库建议名: college_c")
    sql_content.append("-- 包含 50 名学生、10 门课程、250 条选课记录")
    sql_content.append("")
    sql_content.append("-- 创建数据库")
    sql_content.append("CREATE DATABASE IF NOT EXISTS college_c CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
    sql_content.append("USE college_c;")
    sql_content.append("")
    sql_content.append("-- 创建学生表")
    sql_content.append("CREATE TABLE IF NOT EXISTS students (")
    sql_content.append("    id VARCHAR(20) NOT NULL PRIMARY KEY COMMENT '学生ID',")
    sql_content.append("    college_code ENUM('A', 'B', 'C') NOT NULL COMMENT '学院代码',")
    sql_content.append("    name VARCHAR(50) NOT NULL COMMENT '学生姓名',")
    sql_content.append("    gender ENUM('男', '女') NOT NULL COMMENT '性别',")
    sql_content.append("    major VARCHAR(100) NOT NULL COMMENT '专业',")
    sql_content.append("    grade INT NOT NULL COMMENT '年级'")
    sql_content.append(") COMMENT '学生信息表';")
    sql_content.append("")
    sql_content.append("-- 创建课程表")
    sql_content.append("CREATE TABLE IF NOT EXISTS courses (")
    sql_content.append("    id VARCHAR(20) NOT NULL PRIMARY KEY COMMENT '课程ID',")
    sql_content.append("    college_code ENUM('A', 'B', 'C') NOT NULL COMMENT '学院代码',")
    sql_content.append("    name VARCHAR(100) NOT NULL COMMENT '课程名称',")
    sql_content.append("    credits DOUBLE NOT NULL COMMENT '学分',")
    sql_content.append("    teacher VARCHAR(50) NOT NULL COMMENT '授课教师',")
    sql_content.append("    shared BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否为共享课程'")
    sql_content.append(") COMMENT '课程信息表';")
    sql_content.append("")
    sql_content.append("-- 创建选课记录表")
    sql_content.append("CREATE TABLE IF NOT EXISTS enrollments (")
    sql_content.append("    id VARCHAR(20) NOT NULL PRIMARY KEY COMMENT '选课记录ID',")
    sql_content.append("    student_college ENUM('A', 'B', 'C') NOT NULL COMMENT '学生所在学院',")
    sql_content.append("    student_id VARCHAR(20) NOT NULL COMMENT '学生ID',")
    sql_content.append("    course_college ENUM('A', 'B', 'C') NOT NULL COMMENT '课程所属学院',")
    sql_content.append("    course_id VARCHAR(20) NOT NULL COMMENT '课程ID',")
    sql_content.append("    enrolled_at DATE NOT NULL COMMENT '选课日期',")
    sql_content.append("    status VARCHAR(20) NOT NULL COMMENT '选课状态'")
    sql_content.append(") COMMENT '选课记录表';")
    sql_content.append("")
    sql_content.append("-- 插入学生数据")
    sql_content.append("INSERT INTO students (id, college_code, name, gender, major, grade) VALUES")
    for i, student in enumerate(students):
        line = f"    ('{student['id']}', '{student['college_code']}', '{student['name']}', '{student['gender']}', '{student['major']}', {student['grade']})"
        if i < len(students) - 1:
            line += ","
        else:
            line += ";"
        sql_content.append(line)
    sql_content.append("")
    sql_content.append("-- 插入课程数据")
    sql_content.append("INSERT INTO courses (id, college_code, name, credits, teacher, shared) VALUES")
    for i, course in enumerate(courses):
        shared_bool = "TRUE" if course['shared'] else "FALSE"
        line = f"    ('{course['id']}', '{course['college_code']}', '{course['name']}', {course['credits']}, '{course['teacher']}', {shared_bool})"
        if i < len(courses) - 1:
            line += ","
        else:
            line += ";"
        sql_content.append(line)
    sql_content.append("")
    sql_content.append("-- 插入选课记录数据")
    sql_content.append("INSERT INTO enrollments (id, student_college, student_id, course_college, course_id, enrolled_at, status) VALUES")
    for i, enrollment in enumerate(enrollments):
        line = f"    ('{enrollment['id']}', '{enrollment['student_college']}', '{enrollment['student_id']}', '{enrollment['course_college']}', '{enrollment['course_id']}', '{enrollment['enrolled_at']}', '{enrollment['status']}')"
        if i < len(enrollments) - 1:
            line += ","
        else:
            line += ";"
        sql_content.append(line)
    sql_content.append("")
    sql_content.append("-- 数据导入完成")

    return "\n".join(sql_content)


if __name__ == "__main__":
    sql = generate_sql()
    output_file = "/Users/bytedance/Desktop/数据集成作业三/mysqldatabase/init.sql"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(sql)
    print(f"SQL 脚本已生成: {output_file}")

    # 同时生成字段映射说明文档
    mapping_content = """# 学院 C MySQL 字段映射说明

## 学生表 (students) 与 StudentRecord 映射关系

| MySQL 字段 | Java 字段 | 类型 | 说明 |
|-----------|----------|------|------|
| id | id | VARCHAR(20) | 学生ID |
| college_code | college | ENUM('A','B','C') | 学院代码 |
| name | name | VARCHAR(50) | 学生姓名 |
| gender | gender | ENUM('男','女') | 性别 |
| major | major | VARCHAR(100) | 专业 |
| grade | grade | INT | 年级 |

## 课程表 (courses) 与 CourseRecord 映射关系

| MySQL 字段 | Java 字段 | 类型 | 说明 |
|-----------|----------|------|------|
| id | id | VARCHAR(20) | 课程ID |
| college_code | college | ENUM('A','B','C') | 学院代码 |
| name | name | VARCHAR(100) | 课程名称 |
| credits | credits | DOUBLE | 学分 |
| teacher | teacher | VARCHAR(50) | 授课教师 |
| shared | shared | BOOLEAN | 是否为共享课程 |

## 选课记录表 (enrollments) 与 EnrollmentRecord 映射关系

| MySQL 字段 | Java 字段 | 类型 | 说明 |
|-----------|----------|------|------|
| id | id | VARCHAR(20) | 选课记录ID |
| student_college | studentCollege | ENUM('A','B','C') | 学生所在学院 |
| student_id | studentId | VARCHAR(20) | 学生ID |
| course_college | courseCollege | ENUM('A','B','C') | 课程所属学院 |
| course_id | courseId | VARCHAR(20) | 课程ID |
| enrolled_at | enrolledAt | DATE | 选课日期 |
| status | status | VARCHAR(20) | 选课状态 |

## 数据库连接信息

- 数据库名: college_c
- 字符集: utf8mb4
- JDBC URL: jdbc:mysql://localhost:3306/college_c?useUnicode=true&characterEncoding=utf8&useSSL=false&serverTimezone=Asia/Shanghai
"""
    mapping_file = "/Users/bytedance/Desktop/数据集成作业三/mysqldatabase/字段映射说明.md"
    with open(mapping_file, "w", encoding="utf-8") as f:
        f.write(mapping_content)
    print(f"字段映射说明已生成: {mapping_file}")

