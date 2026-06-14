#!/usr/bin/env python3
"""Task 2 anomaly detection for HW4 exported dataset.

Run from the repository root:

    python work4/anomaly_detection.py

The script reads CSV files from ``work4/hw4_20260614/`` and writes a
report-ready HTML page plus CSV outputs to ``work4/``.  It intentionally uses
only the Python standard library so it can be regenerated in a clean checkout.
"""

from __future__ import annotations

import csv
import html
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from statistics import mean, pstdev


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "hw4_20260614"
OUTPUT_DIR = BASE_DIR

OUR_GROUP = "18"
VALID_DEPTS = {"A", "B", "C"}
EXPECTED_GROUP_TOTALS = {"student": 150, "course": 30, "sc": 750}
EXPECTED_DEPT_TOTALS = {"student": 50, "course": 10, "sc": 250}
MISSING_MARKERS = {"", "NUL", "NULL", "NONE", "NA", "N/A"}


@dataclass(frozen=True)
class Anomaly:
    severity: str
    table: str
    rule_id: str
    rule_name: str
    group_no: str
    dept_no: str
    record_key: str
    field: str
    value: str
    detail: str


def read_csv_file(name: str) -> list[dict[str, str]]:
    path = DATA_DIR / name
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv_file(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def clean(value: object) -> str:
    return "" if value is None else str(value).strip()


def norm_missing(value: object) -> bool:
    return clean(value).upper() in MISSING_MARKERS


def parse_float(value: object) -> float | None:
    if norm_missing(value):
        return None
    try:
        return float(clean(value))
    except ValueError:
        return None


def group_sort_key(value: str) -> tuple[int, int | str]:
    if value.isdigit():
        return (0, int(value))
    return (1, value)


def row_location(row: dict[str, str]) -> tuple[str, str]:
    group_no = clean(row.get("group_no")) or "UNKNOWN"
    dept_no = clean(row.get("dept_no")) or "UNKNOWN"
    return group_no, dept_no


def make_anomaly(
    severity: str,
    table: str,
    rule_id: str,
    rule_name: str,
    row: dict[str, str] | None,
    record_key: str,
    field: str,
    value: object,
    detail: str,
    group_no: str | None = None,
    dept_no: str | None = None,
) -> Anomaly:
    if row is not None:
        row_group, row_dept = row_location(row)
    else:
        row_group, row_dept = "UNKNOWN", "UNKNOWN"
    return Anomaly(
        severity=severity,
        table=table,
        rule_id=rule_id,
        rule_name=rule_name,
        group_no=group_no or row_group,
        dept_no=dept_no or row_dept,
        record_key=record_key,
        field=field,
        value=clean(value),
        detail=detail,
    )


def student_key(row: dict[str, str]) -> str:
    return f"{clean(row.get('group_no'))}|{clean(row.get('dept_no'))}|{clean(row.get('student_id'))}"


def course_key(row: dict[str, str]) -> str:
    return f"{clean(row.get('group_no'))}|{clean(row.get('dept_no'))}|{clean(row.get('course_id'))}"


def sc_key(row: dict[str, str]) -> str:
    return (
        f"{clean(row.get('group_no'))}|{clean(row.get('dept_no'))}|"
        f"{clean(row.get('student_id'))}|{clean(row.get('course_id'))}"
    )


def detect_required_and_domain(
    table: str,
    rows: list[dict[str, str]],
    required_fields: list[str],
    key_func,
) -> list[Anomaly]:
    anomalies: list[Anomaly] = []
    for row in rows:
        record_key = key_func(row)
        for field in required_fields:
            if norm_missing(row.get(field)):
                anomalies.append(
                    make_anomaly(
                        "ERROR",
                        table,
                        "REQUIRED_MISSING",
                        "关键字段缺失或占位",
                        row,
                        record_key,
                        field,
                        row.get(field),
                        f"{field} 为空、NUL、NULL 或其他缺失占位",
                    )
                )
        group_no, dept_no = row_location(row)
        if not group_no.isdigit():
            anomalies.append(
                make_anomaly(
                    "ERROR",
                    table,
                    "INVALID_GROUP",
                    "组号格式异常",
                    row,
                    record_key,
                    "group_no",
                    group_no,
                    "group_no 应为数字组号",
                )
            )
        if dept_no not in VALID_DEPTS:
            anomalies.append(
                make_anomaly(
                    "ERROR",
                    table,
                    "INVALID_DEPT",
                    "院系标识异常",
                    row,
                    record_key,
                    "dept_no",
                    dept_no,
                    "dept_no 应属于 A/B/C",
                )
            )
    return anomalies


def detect_duplicates(
    table: str,
    rows: list[dict[str, str]],
    key_func,
    key_field: str,
) -> list[Anomaly]:
    anomalies: list[Anomaly] = []
    buckets: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        buckets[key_func(row)].append(row)
    for key, duplicated_rows in buckets.items():
        if len(duplicated_rows) <= 1:
            continue
        for row in duplicated_rows:
            anomalies.append(
                make_anomaly(
                    "ERROR",
                    table,
                    "DUPLICATE_KEY",
                    "业务主键重复",
                    row,
                    key,
                    key_field,
                    key,
                    f"同一 group_no + dept_no 下出现 {len(duplicated_rows)} 条相同业务主键记录",
                )
            )
    return anomalies


def detect_student_anomalies(rows: list[dict[str, str]]) -> list[Anomaly]:
    anomalies = detect_required_and_domain(
        "student",
        rows,
        ["student_id", "student_name", "gender", "department", "group_no", "dept_no"],
        student_key,
    )
    anomalies.extend(detect_duplicates("student", rows, student_key, "student_id"))
    for row in rows:
        gender = clean(row.get("gender"))
        if gender.upper() not in {"男", "女", "M", "F", "MALE", "FEMALE"}:
            anomalies.append(
                make_anomaly(
                    "WARNING",
                    "student",
                    "NON_STANDARD_GENDER",
                    "性别写法非标准",
                    row,
                    student_key(row),
                    "gender",
                    gender,
                    "gender 建议统一为 男/女 或 M/F 后再分析",
                )
            )
    return anomalies


def detect_course_anomalies(rows: list[dict[str, str]]) -> list[Anomaly]:
    anomalies = detect_required_and_domain(
        "course",
        rows,
        ["course_id", "course_name", "credit", "teacher_name", "group_no", "dept_no"],
        course_key,
    )
    anomalies.extend(detect_duplicates("course", rows, course_key, "course_id"))
    for row in rows:
        key = course_key(row)
        credit = parse_float(row.get("credit"))
        if credit is None:
            anomalies.append(
                make_anomaly("ERROR", "course", "INVALID_CREDIT", "学分非数值或缺失", row, key, "credit", row.get("credit"), "credit 应为数值")
            )
        elif credit <= 0 or credit > 10:
            anomalies.append(
                make_anomaly("WARNING", "course", "UNUSUAL_CREDIT", "学分范围可疑", row, key, "credit", row.get("credit"), "credit 通常应在 0 到 10 之间")
            )

        for field in ["class_hours", "practice_hours"]:
            hours = parse_float(row.get(field))
            if hours is None:
                anomalies.append(
                    make_anomaly("WARNING", "course", "INVALID_HOURS", "学时非数值或缺失", row, key, field, row.get(field), f"{field} 应为非负数值")
                )
            elif hours < 0 or hours > 256:
                anomalies.append(
                    make_anomaly("WARNING", "course", "UNUSUAL_HOURS", "学时范围可疑", row, key, field, row.get(field), f"{field} 不应为负数或过大值")
                )

        share_flag = clean(row.get("share_flag")).upper()
        if share_flag not in {"0", "1", "Y", "N", "YES", "NO", "TRUE", "FALSE", "T", "F"}:
            anomalies.append(
                make_anomaly("WARNING", "course", "INVALID_SHARE_FLAG", "共享标记写法异常", row, key, "share_flag", row.get("share_flag"), "share_flag 建议统一为 0/1 或 Y/N")
            )
    return anomalies


def detect_sc_anomalies(
    sc_rows: list[dict[str, str]],
    student_rows: list[dict[str, str]],
    course_rows: list[dict[str, str]],
) -> list[Anomaly]:
    anomalies = detect_required_and_domain(
        "sc",
        sc_rows,
        ["course_id", "student_id", "group_no", "dept_no"],
        sc_key,
    )
    anomalies.extend(detect_duplicates("sc", sc_rows, sc_key, "student_id+course_id"))
    student_keys = {student_key(row) for row in student_rows}
    course_keys = {course_key(row) for row in course_rows}

    for row in sc_rows:
        key = sc_key(row)
        score_raw = row.get("score")
        score = parse_float(score_raw)
        if norm_missing(score_raw):
            anomalies.append(
                make_anomaly("ERROR", "sc", "SCORE_MISSING", "成绩缺失或占位", row, key, "score", score_raw, "score 为空、NUL、NULL 或其他缺失占位，无法参与均分/及格率计算")
            )
        elif score is None:
            anomalies.append(
                make_anomaly("ERROR", "sc", "SCORE_NOT_NUMERIC", "成绩非数值", row, key, "score", score_raw, "score 无法转换为数值")
            )
        elif score < 0 or score > 100:
            anomalies.append(
                make_anomaly("ERROR", "sc", "SCORE_OUT_OF_RANGE", "成绩超出 0-100", row, key, "score", score_raw, "score 应落在 0 到 100 区间")
            )
        elif score < 60:
            anomalies.append(
                make_anomaly("INFO", "sc", "LOW_SCORE", "低分/不及格记录", row, key, "score", score_raw, "score 低于 60，可作为学习效果分析的风险样本")
            )

        if student_key(row) not in student_keys:
            anomalies.append(
                make_anomaly("ERROR", "sc", "STUDENT_NOT_FOUND", "选课学生不存在", row, key, "student_id", row.get("student_id"), "sc 中的 group_no + dept_no + student_id 在 student 表不存在")
            )
        if course_key(row) not in course_keys:
            anomalies.append(
                make_anomaly("ERROR", "sc", "COURSE_NOT_FOUND", "选课课程不存在", row, key, "course_id", row.get("course_id"), "sc 中的 group_no + dept_no + course_id 在 course 表不存在")
            )
    return anomalies


def detect_distribution_anomalies(tables: dict[str, list[dict[str, str]]]) -> list[Anomaly]:
    anomalies: list[Anomaly] = []
    for table, rows in tables.items():
        group_counts = Counter(clean(row.get("group_no")) or "UNKNOWN" for row in rows)
        dept_counts = Counter(row_location(row) for row in rows)
        for group_no, actual in sorted(group_counts.items(), key=lambda item: group_sort_key(item[0])):
            expected = EXPECTED_GROUP_TOTALS[table]
            if actual != expected:
                anomalies.append(
                    make_anomaly(
                        "WARNING",
                        table,
                        "GROUP_COUNT_DEVIATION",
                        "组提交总量偏离标准",
                        None,
                        f"group={group_no}",
                        "row_count",
                        actual,
                        f"{table} 表第 {group_no} 组实际 {actual} 条，标准为 {expected} 条，偏差 {actual - expected:+d}",
                        group_no=group_no,
                        dept_no="ALL",
                    )
                )
        for (group_no, dept_no), actual in sorted(dept_counts.items(), key=lambda item: (group_sort_key(item[0][0]), item[0][1])):
            expected = EXPECTED_DEPT_TOTALS[table]
            if dept_no in VALID_DEPTS and actual != expected:
                anomalies.append(
                    make_anomaly(
                        "WARNING",
                        table,
                        "DEPT_COUNT_DEVIATION",
                        "院系提交量偏离标准",
                        None,
                        f"group={group_no}|dept={dept_no}",
                        "row_count",
                        actual,
                        f"{table} 表第 {group_no} 组 {dept_no} 院实际 {actual} 条，标准为 {expected} 条，偏差 {actual - expected:+d}",
                        group_no=group_no,
                        dept_no=dept_no,
                    )
                )
    return anomalies


def score_profile(sc_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    buckets: dict[tuple[str, str], list[float]] = defaultdict(list)
    missing_counts: Counter[tuple[str, str]] = Counter()
    invalid_counts: Counter[tuple[str, str]] = Counter()
    low_counts: Counter[tuple[str, str]] = Counter()
    total_counts: Counter[tuple[str, str]] = Counter()

    for row in sc_rows:
        loc = row_location(row)
        total_counts[loc] += 1
        score_raw = row.get("score")
        score = parse_float(score_raw)
        if norm_missing(score_raw):
            missing_counts[loc] += 1
        elif score is None or score < 0 or score > 100:
            invalid_counts[loc] += 1
        else:
            buckets[loc].append(score)
            if score < 60:
                low_counts[loc] += 1

    rows: list[dict[str, object]] = []
    for group_no, dept_no in sorted(total_counts, key=lambda loc: (group_sort_key(loc[0]), loc[1])):
        scores = buckets[(group_no, dept_no)]
        total = total_counts[(group_no, dept_no)]
        valid = len(scores)
        rows.append(
            {
                "group_no": group_no,
                "dept_no": dept_no,
                "total_records": total,
                "valid_scores": valid,
                "missing_scores": missing_counts[(group_no, dept_no)],
                "invalid_scores": invalid_counts[(group_no, dept_no)],
                "low_scores": low_counts[(group_no, dept_no)],
                "average_score": round(mean(scores), 2) if scores else "",
                "score_stddev": round(pstdev(scores), 2) if len(scores) > 1 else "",
                "pass_rate": round((valid - low_counts[(group_no, dept_no)]) / valid * 100, 2) if valid else "",
            }
        )
    return rows


def summarize_anomalies(anomalies: list[Anomaly]) -> list[dict[str, object]]:
    counter: Counter[tuple[str, str, str, str, str, str]] = Counter()
    examples: dict[tuple[str, str, str, str, str, str], str] = {}
    for anomaly in anomalies:
        key = (
            anomaly.severity,
            anomaly.table,
            anomaly.rule_id,
            anomaly.rule_name,
            anomaly.group_no,
            anomaly.dept_no,
        )
        counter[key] += 1
        examples.setdefault(key, anomaly.detail)

    severity_rank = {"ERROR": 0, "WARNING": 1, "INFO": 2}
    rows: list[dict[str, object]] = []
    for key, count in sorted(
        counter.items(),
        key=lambda item: (severity_rank.get(item[0][0], 9), item[0][1], item[0][2], group_sort_key(item[0][4]), item[0][5]),
    ):
        severity, table, rule_id, rule_name, group_no, dept_no = key
        rows.append(
            {
                "severity": severity,
                "table": table,
                "rule_id": rule_id,
                "rule_name": rule_name,
                "group_no": group_no,
                "dept_no": dept_no,
                "count": count,
                "example_detail": examples[key],
            }
        )
    return rows


def group18_conclusion(summary_rows: list[dict[str, object]], score_rows: list[dict[str, object]]) -> list[str]:
    group18_summary = [row for row in summary_rows if row["group_no"] == OUR_GROUP]
    error_count = sum(int(row["count"]) for row in group18_summary if row["severity"] == "ERROR")
    warning_count = sum(int(row["count"]) for row in group18_summary if row["severity"] == "WARNING")
    info_count = sum(int(row["count"]) for row in group18_summary if row["severity"] == "INFO")
    group18_scores = [row for row in score_rows if row["group_no"] == OUR_GROUP]
    missing = sum(int(row["missing_scores"]) for row in group18_scores)
    invalid = sum(int(row["invalid_scores"]) for row in group18_scores)
    low = sum(int(row["low_scores"]) for row in group18_scores)
    valid = sum(int(row["valid_scores"]) for row in group18_scores)
    avg_values = [float(row["average_score"]) for row in group18_scores if row["average_score"] != ""]

    return [
        f"第 {OUR_GROUP} 组 ERROR 级异常 {error_count} 条，WARNING 级异常 {warning_count} 条，INFO 级低分提示 {info_count} 条。",
        f"第 {OUR_GROUP} 组成绩字段缺失/占位 {missing} 条，非法成绩 {invalid} 条，不及格低分 {low} 条，有效成绩 {valid} 条。",
        f"第 {OUR_GROUP} 组三个院系有效成绩均分约为 {round(mean(avg_values), 2) if avg_values else '-'}，可在任务三继续分析课程特征与成绩的关系。",
    ]


def render_table(rows: list[dict[str, object]], columns: list[str], limit: int | None = None) -> str:
    shown_rows = rows if limit is None else rows[:limit]
    header = "".join(f"<th>{html.escape(col)}</th>" for col in columns)
    body = []
    for row in shown_rows:
        body.append("<tr>" + "".join(f"<td>{html.escape(str(row.get(col, '')))}</td>" for col in columns) + "</tr>")
    if not body:
        body.append(f"<tr><td colspan=\"{len(columns)}\">无记录</td></tr>")
    return f"<table><thead><tr>{header}</tr></thead><tbody>{''.join(body)}</tbody></table>"


def write_html_report(
    summary_rows: list[dict[str, object]],
    record_rows: list[dict[str, object]],
    score_rows: list[dict[str, object]],
) -> None:
    severity_counts = Counter(str(row["severity"]) for row in record_rows)
    table_counts = Counter(str(row["table"]) for row in record_rows)
    conclusions = group18_conclusion(summary_rows, score_rows)
    group18_summary = [row for row in summary_rows if row["group_no"] == OUR_GROUP]

    html_doc = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <title>任务二：异常数据发现</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 32px; color: #172033; }}
    h1, h2 {{ color: #0f172a; }}
    .cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; margin: 18px 0; }}
    .card {{ border: 1px solid #d9e2ec; border-radius: 10px; padding: 14px 16px; background: #f8fafc; }}
    .metric {{ font-size: 28px; font-weight: 700; color: #2563eb; }}
    table {{ border-collapse: collapse; width: 100%; margin: 12px 0 24px; font-size: 13px; }}
    th, td {{ border: 1px solid #d9e2ec; padding: 7px 9px; text-align: left; vertical-align: top; }}
    th {{ background: #e8f1ff; }}
    code {{ background: #f1f5f9; padding: 2px 5px; border-radius: 4px; }}
    .note {{ color: #475569; }}
  </style>
</head>
<body>
  <h1>任务二：异常数据发现</h1>
  <p class="note">数据来源：<code>work4/hw4_20260614/</code>；检测对象：student、course、sc 三张表。</p>

  <h2>1. 检测概览</h2>
  <div class="cards">
    <div class="card"><div>ERROR</div><div class="metric">{severity_counts.get('ERROR', 0)}</div><div>需要优先清洗</div></div>
    <div class="card"><div>WARNING</div><div class="metric">{severity_counts.get('WARNING', 0)}</div><div>结构或分布可疑</div></div>
    <div class="card"><div>INFO</div><div class="metric">{severity_counts.get('INFO', 0)}</div><div>低分风险提示</div></div>
    <div class="card"><div>涉及表</div><div class="metric">{len(table_counts)}</div><div>{html.escape(', '.join(sorted(table_counts)))}</div></div>
  </div>

  <h2>2. 本组（第 {OUR_GROUP} 组）结论</h2>
  <ul>{''.join(f'<li>{html.escape(item)}</li>' for item in conclusions)}</ul>
  {render_table(group18_summary, ['severity', 'table', 'rule_id', 'rule_name', 'group_no', 'dept_no', 'count', 'example_detail'])}

  <h2>3. 全量异常汇总</h2>
  {render_table(summary_rows, ['severity', 'table', 'rule_id', 'rule_name', 'group_no', 'dept_no', 'count', 'example_detail'])}

  <h2>4. 成绩质量画像</h2>
  {render_table(score_rows, ['group_no', 'dept_no', 'total_records', 'valid_scores', 'missing_scores', 'invalid_scores', 'low_scores', 'average_score', 'score_stddev', 'pass_rate'])}

  <h2>5. 明细样例（前 200 条）</h2>
  <p class="note">完整明细见 <code>work4/anomaly_records.csv</code>。</p>
  {render_table(record_rows, ['severity', 'table', 'rule_id', 'rule_name', 'group_no', 'dept_no', 'record_key', 'field', 'value', 'detail'], limit=200)}
</body>
</html>
"""
    (OUTPUT_DIR / "task2_anomaly_report.html").write_text(html_doc, encoding="utf-8")


def main() -> None:
    student_rows = read_csv_file("student.csv")
    course_rows = read_csv_file("course.csv")
    sc_rows = read_csv_file("sc.csv")
    tables = {"student": student_rows, "course": course_rows, "sc": sc_rows}

    anomalies: list[Anomaly] = []
    anomalies.extend(detect_student_anomalies(student_rows))
    anomalies.extend(detect_course_anomalies(course_rows))
    anomalies.extend(detect_sc_anomalies(sc_rows, student_rows, course_rows))
    anomalies.extend(detect_distribution_anomalies(tables))

    record_rows = [anomaly.__dict__ for anomaly in anomalies]
    summary_rows = summarize_anomalies(anomalies)
    score_rows = score_profile(sc_rows)

    write_csv_file(
        OUTPUT_DIR / "anomaly_records.csv",
        record_rows,
        ["severity", "table", "rule_id", "rule_name", "group_no", "dept_no", "record_key", "field", "value", "detail"],
    )
    write_csv_file(
        OUTPUT_DIR / "anomaly_summary.csv",
        summary_rows,
        ["severity", "table", "rule_id", "rule_name", "group_no", "dept_no", "count", "example_detail"],
    )
    write_csv_file(
        OUTPUT_DIR / "score_quality_profile.csv",
        score_rows,
        ["group_no", "dept_no", "total_records", "valid_scores", "missing_scores", "invalid_scores", "low_scores", "average_score", "score_stddev", "pass_rate"],
    )
    write_html_report(summary_rows, record_rows, score_rows)

    severity_counts = Counter(row["severity"] for row in record_rows)
    print("异常检测完成：")
    print(f"- 明细：{OUTPUT_DIR / 'anomaly_records.csv'}")
    print(f"- 汇总：{OUTPUT_DIR / 'anomaly_summary.csv'}")
    print(f"- 成绩画像：{OUTPUT_DIR / 'score_quality_profile.csv'}")
    print(f"- HTML报告：{OUTPUT_DIR / 'task2_anomaly_report.html'}")
    print(f"- ERROR={severity_counts.get('ERROR', 0)}, WARNING={severity_counts.get('WARNING', 0)}, INFO={severity_counts.get('INFO', 0)}")


if __name__ == "__main__":
    main()
