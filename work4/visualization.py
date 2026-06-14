#!/usr/bin/env python3
"""Data distribution visualization script for HW4.

Run from the repository root:

    python3 work4/visualization.py

The script reads CSV files from ``work4/hw4_20260614/`` and exports
screenshot-ready SVG charts plus a compact HTML report to
``work4/``.
"""

from __future__ import annotations

import csv
import html
from collections import defaultdict
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "hw4_20260614"
OUTPUT_DIR = BASE_DIR
CHART_DIR = BASE_DIR / "charts"

EXPECTED_TOTALS = {
    "student": 150,
    "course": 30,
    "sc": 750,
}

METRICS = {
    "student": "student_group_dept_counts",
    "course": "course_group_dept_counts",
    "sc": "sc_group_dept_counts",
}

TABLE_NAMES = {
    "student": "student 表提交数量",
    "course": "course 表提交数量",
    "sc": "sc 表提交数量",
}

DEPT_COLORS = {
    "A": "#2563eb",
    "B": "#16a34a",
    "C": "#f59e0b",
    "UNKNOWN": "#64748b",
}

BAR_COLOR = "#3b82f6"
HIGHLIGHT_COLOR = "#dc2626"
REFERENCE_COLOR = "#111827"
GRID_COLOR = "#d9e2ec"
TEXT_COLOR = "#172033"
MUTED_COLOR = "#64748b"
BACKGROUND = "#ffffff"


def read_group_summary() -> dict[str, dict[str, dict[str, int]]]:
    summary: dict[str, dict[str, dict[str, int]]] = defaultdict(lambda: defaultdict(dict))
    path = DATA_DIR / "group_dept_summary.csv"
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            metric = row["metric"]
            group_no = row["group_no"]
            dept_no = row["dept_no"] or "UNKNOWN"
            summary[metric][group_no][dept_no] = int(row["row_count"])
    return summary


def read_quality_snapshot() -> dict[str, int]:
    path = DATA_DIR / "quality_snapshot.csv"
    quality: dict[str, int] = {}
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            quality[row["metric"]] = int(row["value"])
    return quality


def group_sort_key(group_no: str) -> tuple[int, int | str]:
    if group_no.isdigit():
        return (0, int(group_no))
    return (1, group_no)


def totals_for_metric(
    summary: dict[str, dict[str, dict[str, int]]],
    table_key: str,
) -> dict[str, int]:
    metric = METRICS[table_key]
    return {
        group_no: sum(dept_counts.values())
        for group_no, dept_counts in summary.get(metric, {}).items()
    }


def svg_escape(value: object) -> str:
    return html.escape(str(value), quote=True)


def horizontal_bar_chart(
    title: str,
    subtitle: str,
    totals: dict[str, int],
    expected: int,
    output_path: Path,
) -> None:
    groups = sorted(totals, key=group_sort_key)
    max_value = max(max(totals.values(), default=0), expected)
    width = 1280
    row_height = 28
    top = 104
    bottom = 80
    left = 120
    right = 112
    plot_width = width - left - right
    height = max(560, top + bottom + len(groups) * row_height)
    plot_height = len(groups) * row_height

    def x(value: int) -> float:
        if max_value == 0:
            return float(left)
        return left + (value / max_value) * plot_width

    expected_x = x(expected)
    elements: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        f'<rect width="100%" height="100%" fill="{BACKGROUND}"/>',
        f'<text x="40" y="44" font-family="Arial, sans-serif" font-size="26" font-weight="700" fill="{TEXT_COLOR}">{svg_escape(title)}</text>',
        f'<text x="40" y="74" font-family="Arial, sans-serif" font-size="15" fill="{MUTED_COLOR}">{svg_escape(subtitle)}</text>',
    ]

    tick_count = 5
    for i in range(tick_count + 1):
        value = round(max_value * i / tick_count)
        tx = x(value)
        elements.append(f'<line x1="{tx:.1f}" y1="{top - 8}" x2="{tx:.1f}" y2="{top + plot_height}" stroke="{GRID_COLOR}" stroke-width="1"/>')
        elements.append(f'<text x="{tx:.1f}" y="{top + plot_height + 28}" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" fill="{MUTED_COLOR}">{value}</text>')

    elements.append(f'<line x1="{expected_x:.1f}" y1="{top - 20}" x2="{expected_x:.1f}" y2="{top + plot_height}" stroke="{REFERENCE_COLOR}" stroke-width="2" stroke-dasharray="6 6"/>')
    elements.append(f'<text x="{expected_x + 8:.1f}" y="{top - 26}" font-family="Arial, sans-serif" font-size="13" fill="{REFERENCE_COLOR}">正常值 {expected}</text>')

    for index, group_no in enumerate(groups):
        value = totals[group_no]
        y = top + index * row_height
        bar_x = left
        bar_y = y + 5
        bar_width = max(1, x(value) - left)
        color = HIGHLIGHT_COLOR if group_no == "18" else BAR_COLOR
        label_weight = "700" if group_no == "18" else "400"
        elements.append(f'<text x="{left - 18}" y="{y + 20}" text-anchor="end" font-family="Arial, sans-serif" font-size="13" font-weight="{label_weight}" fill="{TEXT_COLOR}">{svg_escape(group_no)}组</text>')
        elements.append(f'<rect x="{bar_x}" y="{bar_y}" width="{bar_width:.1f}" height="18" rx="3" fill="{color}"/>')
        elements.append(f'<text x="{bar_x + bar_width + 8:.1f}" y="{y + 20}" font-family="Arial, sans-serif" font-size="13" font-weight="{label_weight}" fill="{TEXT_COLOR}">{value}</text>')

    elements.append(f'<text x="{left}" y="{height - 24}" font-family="Arial, sans-serif" font-size="12" fill="{MUTED_COLOR}">红色为本组 18 组；虚线为课程要求的标准提交数量。</text>')
    elements.append("</svg>")
    output_path.write_text("\n".join(elements) + "\n", encoding="utf-8")


def stacked_dept_chart(
    title: str,
    subtitle: str,
    dept_counts_by_group: dict[str, dict[str, int]],
    expected: int,
    output_path: Path,
) -> None:
    groups = sorted(dept_counts_by_group, key=group_sort_key)
    totals = {group_no: sum(counts.values()) for group_no, counts in dept_counts_by_group.items()}
    max_value = max(max(totals.values(), default=0), expected)
    width = 1280
    row_height = 28
    top = 118
    bottom = 86
    left = 120
    right = 120
    plot_width = width - left - right
    height = max(580, top + bottom + len(groups) * row_height)
    plot_height = len(groups) * row_height

    def x(value: int) -> float:
        if max_value == 0:
            return float(left)
        return left + (value / max_value) * plot_width

    elements: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        f'<rect width="100%" height="100%" fill="{BACKGROUND}"/>',
        f'<text x="40" y="44" font-family="Arial, sans-serif" font-size="26" font-weight="700" fill="{TEXT_COLOR}">{svg_escape(title)}</text>',
        f'<text x="40" y="74" font-family="Arial, sans-serif" font-size="15" fill="{MUTED_COLOR}">{svg_escape(subtitle)}</text>',
    ]

    legend_x = 40
    for dept_no in ["A", "B", "C"]:
        color = DEPT_COLORS[dept_no]
        elements.append(f'<rect x="{legend_x}" y="90" width="14" height="14" rx="2" fill="{color}"/>')
        elements.append(f'<text x="{legend_x + 20}" y="102" font-family="Arial, sans-serif" font-size="13" fill="{TEXT_COLOR}">院系 {dept_no}</text>')
        legend_x += 88

    tick_count = 5
    for i in range(tick_count + 1):
        value = round(max_value * i / tick_count)
        tx = x(value)
        elements.append(f'<line x1="{tx:.1f}" y1="{top - 8}" x2="{tx:.1f}" y2="{top + plot_height}" stroke="{GRID_COLOR}" stroke-width="1"/>')
        elements.append(f'<text x="{tx:.1f}" y="{top + plot_height + 28}" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" fill="{MUTED_COLOR}">{value}</text>')

    expected_x = x(expected)
    elements.append(f'<line x1="{expected_x:.1f}" y1="{top - 20}" x2="{expected_x:.1f}" y2="{top + plot_height}" stroke="{REFERENCE_COLOR}" stroke-width="2" stroke-dasharray="6 6"/>')
    elements.append(f'<text x="{expected_x + 8:.1f}" y="{top - 26}" font-family="Arial, sans-serif" font-size="13" fill="{REFERENCE_COLOR}">正常合计 {expected}</text>')

    for index, group_no in enumerate(groups):
        counts = dept_counts_by_group[group_no]
        y = top + index * row_height
        current_x = left
        label_weight = "700" if group_no == "18" else "400"
        elements.append(f'<text x="{left - 18}" y="{y + 20}" text-anchor="end" font-family="Arial, sans-serif" font-size="13" font-weight="{label_weight}" fill="{TEXT_COLOR}">{svg_escape(group_no)}组</text>')
        for dept_no in ["A", "B", "C"]:
            count = counts.get(dept_no, 0)
            segment_width = max(0, x(count) - left)
            if count > 0:
                elements.append(f'<rect x="{current_x:.1f}" y="{y + 5}" width="{segment_width:.1f}" height="18" rx="2" fill="{DEPT_COLORS[dept_no]}"/>')
                if segment_width >= 30:
                    elements.append(f'<text x="{current_x + segment_width / 2:.1f}" y="{y + 19}" text-anchor="middle" font-family="Arial, sans-serif" font-size="11" font-weight="700" fill="#ffffff">{count}</text>')
            current_x += segment_width
        total = totals[group_no]
        elements.append(f'<text x="{current_x + 8:.1f}" y="{y + 20}" font-family="Arial, sans-serif" font-size="13" font-weight="{label_weight}" fill="{TEXT_COLOR}">{total}</text>')
        if group_no == "18":
            elements.append(f'<rect x="{left - 4}" y="{y + 2}" width="{plot_width + 8}" height="24" fill="none" stroke="{HIGHLIGHT_COLOR}" stroke-width="2" rx="4"/>')

    elements.append(f'<text x="{left}" y="{height - 24}" font-family="Arial, sans-serif" font-size="12" fill="{MUTED_COLOR}">18 组为 A/B/C 各 50 名学生，结构符合标准提交规模。</text>')
    elements.append("</svg>")
    output_path.write_text("\n".join(elements) + "\n", encoding="utf-8")


def deviation_rows(summary: dict[str, dict[str, dict[str, int]]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for table_key, expected in EXPECTED_TOTALS.items():
        totals = totals_for_metric(summary, table_key)
        for group_no, total in totals.items():
            delta = total - expected
            if delta != 0:
                rows.append({
                    "table": table_key,
                    "group_no": group_no,
                    "actual": total,
                    "expected": expected,
                    "delta": delta,
                    "abs_delta": abs(delta),
                })
    rows.sort(key=lambda row: (-int(row["abs_delta"]), str(row["table"]), group_sort_key(str(row["group_no"]))))
    return rows


def write_deviation_csv(rows: list[dict[str, object]]) -> Path:
    path = OUTPUT_DIR / "distribution_deviations.csv"
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["table", "group_no", "actual", "expected", "delta"])
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row[key] for key in ["table", "group_no", "actual", "expected", "delta"]})
    return path


def write_html_report(
    summary: dict[str, dict[str, dict[str, int]]],
    quality: dict[str, int],
    deviations: list[dict[str, object]],
    chart_files: dict[str, Path],
    deviation_csv: Path,
) -> None:
    group18 = {
        table_key: totals_for_metric(summary, table_key).get("18", 0)
        for table_key in ["student", "course", "sc"]
    }
    top_deviations = deviations[:12]

    def rel(path: Path) -> str:
        return path.relative_to(OUTPUT_DIR).as_posix()

    top_rows = "\n".join(
        "<tr>"
        f"<td>{svg_escape(row['table'])}</td>"
        f"<td>{svg_escape(row['group_no'])}</td>"
        f"<td>{row['actual']}</td>"
        f"<td>{row['expected']}</td>"
        f"<td>{row['delta']:+}</td>"
        "</tr>"
        for row in top_deviations
    )

    html_text = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>各组数据提交规模与院系分布可视化</title>
  <style>
    :root {{
      --text: #172033;
      --muted: #64748b;
      --line: #d9e2ec;
      --panel: #f8fafc;
      --accent: #dc2626;
    }}
    body {{
      margin: 0;
      font-family: Arial, "PingFang SC", "Microsoft YaHei", sans-serif;
      color: var(--text);
      background: #ffffff;
    }}
    main {{
      width: min(1180px, calc(100vw - 48px));
      margin: 32px auto 56px;
    }}
    header {{
      border-bottom: 1px solid var(--line);
      padding-bottom: 18px;
      margin-bottom: 24px;
    }}
    h1 {{
      font-size: 28px;
      margin: 0 0 10px;
    }}
    h2 {{
      font-size: 20px;
      margin: 28px 0 12px;
    }}
    p {{
      line-height: 1.65;
      margin: 8px 0;
    }}
    .kpis {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
      margin: 20px 0 10px;
    }}
    .kpi {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 14px 16px;
    }}
    .kpi .label {{
      color: var(--muted);
      font-size: 13px;
    }}
    .kpi .value {{
      font-size: 28px;
      font-weight: 700;
      margin-top: 4px;
    }}
    figure {{
      margin: 18px 0 28px;
      padding: 0;
      border: 1px solid var(--line);
      border-radius: 8px;
      overflow: hidden;
      background: #fff;
    }}
    figure img {{
      width: 100%;
      display: block;
    }}
    figcaption {{
      border-top: 1px solid var(--line);
      color: var(--muted);
      font-size: 13px;
      padding: 10px 14px;
      background: var(--panel);
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin-top: 10px;
      font-size: 14px;
    }}
    th, td {{
      border: 1px solid var(--line);
      padding: 8px 10px;
      text-align: right;
    }}
    th:first-child, td:first-child,
    th:nth-child(2), td:nth-child(2) {{
      text-align: left;
    }}
    th {{
      background: var(--panel);
    }}
    .note {{
      color: var(--muted);
      font-size: 14px;
    }}
    .accent {{
      color: var(--accent);
      font-weight: 700;
    }}
  </style>
</head>
<body>
<main>
  <header>
    <h1>各组数据提交规模与院系分布可视化分析</h1>
    <p>数据来源为服务器 hw4 数据库导出的 student、course、sc 三张表，重点展示各组提交数量差异和 A/B/C 院系分布。</p>
    <p class="note">红色高亮为本组 18 组；虚线为作业标准规模：student=150、course=30、sc=750。</p>
  </header>

  <section class="kpis">
    <div class="kpi"><div class="label">服务器 student 总量</div><div class="value">{quality.get('student_total', 0)}</div></div>
    <div class="kpi"><div class="label">服务器 course 总量</div><div class="value">{quality.get('course_total', 0)}</div></div>
    <div class="kpi"><div class="label">服务器 sc 总量</div><div class="value">{quality.get('sc_total', 0)}</div></div>
  </section>
  <section class="kpis">
    <div class="kpi"><div class="label">18 组 student</div><div class="value">{group18['student']}</div></div>
    <div class="kpi"><div class="label">18 组 course</div><div class="value">{group18['course']}</div></div>
    <div class="kpi"><div class="label">18 组 sc</div><div class="value">{group18['sc']}</div></div>
  </section>

  <h2>1. 各组提交数量对比</h2>
  <figure>
    <img src="{rel(chart_files['student_total'])}" alt="各组 student 表提交数量柱状图">
    <figcaption>图 1：student 表提交规模。标准组通常为 150 行，18 组符合标准。</figcaption>
  </figure>
  <figure>
    <img src="{rel(chart_files['course_total'])}" alt="各组 course 表提交数量柱状图">
    <figcaption>图 2：course 表提交规模。标准组通常为 30 行，部分组课程数量明显偏高。</figcaption>
  </figure>
  <figure>
    <img src="{rel(chart_files['sc_total'])}" alt="各组 sc 表提交数量柱状图">
    <figcaption>图 3：sc 表提交规模。标准组通常为 750 行，第 2 组等存在明显数量异常。</figcaption>
  </figure>

  <h2>2. student 表 A/B/C 院系分布</h2>
  <figure>
    <img src="{rel(chart_files['student_stacked'])}" alt="各组 student 表 A/B/C 院系堆叠柱状图">
    <figcaption>图 4：student 表按院系堆叠。18 组 A/B/C 各 50 行，结构均衡。</figcaption>
  </figure>

  <h2>3. 数量异常组初筛</h2>
  <p>下表列出与标准提交规模偏差最大的前 12 条记录。完整明细见 <code>{svg_escape(deviation_csv.name)}</code>。</p>
  <table>
    <thead><tr><th>表</th><th>组号</th><th>实际数量</th><th>标准数量</th><th>偏差</th></tr></thead>
    <tbody>{top_rows}</tbody>
  </table>

  <h2>4. 可写入报告的结论</h2>
  <p>从提交规模看，多数组的数据量接近作业标准，但存在少量组提交量明显偏离。<span class="accent">18 组</span>在 student、course、sc 三张表上分别为 150、30、750 行，且 student 表 A/B/C 三个院系均为 50 行，符合标准提交规模。</p>
  <p>第 2 组在三张表上均明显高于标准值，是后续异常数据分析应重点关注的对象。个别组存在缺少某些院系或组号异常的情况，可交由异常检测成员继续深入。</p>
</main>
</body>
</html>
"""
    (OUTPUT_DIR / "distribution_report.html").write_text(html_text, encoding="utf-8")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    CHART_DIR.mkdir(parents=True, exist_ok=True)

    summary = read_group_summary()
    quality = read_quality_snapshot()

    chart_files = {
        "student_total": CHART_DIR / "student_total_by_group.svg",
        "course_total": CHART_DIR / "course_total_by_group.svg",
        "sc_total": CHART_DIR / "sc_total_by_group.svg",
        "student_stacked": CHART_DIR / "student_dept_stacked_by_group.svg",
    }

    for table_key in ["student", "course", "sc"]:
        horizontal_bar_chart(
            title=f"各组 {TABLE_NAMES[table_key]}",
            subtitle=f"按 group_no 汇总 row_count，参考线为标准值 {EXPECTED_TOTALS[table_key]}",
            totals=totals_for_metric(summary, table_key),
            expected=EXPECTED_TOTALS[table_key],
            output_path=chart_files[f"{table_key}_total"],
        )

    stacked_dept_chart(
        title="各组 student 表 A/B/C 院系分布",
        subtitle="堆叠条形图展示每组 A、B、C 三个院系的学生数据数量",
        dept_counts_by_group=summary[METRICS["student"]],
        expected=EXPECTED_TOTALS["student"],
        output_path=chart_files["student_stacked"],
    )

    deviations = deviation_rows(summary)
    deviation_csv = write_deviation_csv(deviations)
    write_html_report(summary, quality, deviations, chart_files, deviation_csv)

    print("Generated visualization outputs:")
    print(OUTPUT_DIR / "distribution_report.html")
    for path in chart_files.values():
        print(path)
    print(deviation_csv)


if __name__ == "__main__":
    main()
