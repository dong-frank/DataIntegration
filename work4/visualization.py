#!/usr/bin/env python3
"""Task 1 visualization script for the HW4 exported dataset.

Run from the repository root:

    python work4/visualization.py

The script reads CSV files from ``work4/hw4_20260614/`` and exports a
report-ready HTML page plus screenshot-ready SVG charts to ``work4/``.
It intentionally uses only the Python standard library so the report can be
regenerated in a clean checkout.
"""

from __future__ import annotations

import csv
import html
from collections import Counter, defaultdict
from pathlib import Path
from typing import Callable, Iterable


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

CATEGORY_COLORS = {
    "male": "#2563eb",
    "female": "#db2777",
    "unknown": "#64748b",
    "shared": "#16a34a",
    "not_shared": "#f59e0b",
    "other": "#64748b",
    "valid": "#16a34a",
    "missing": "#f59e0b",
    "invalid": "#dc2626",
    "class_hours": "#2563eb",
    "practice_hours": "#f97316",
}

BAR_COLOR = "#3b82f6"
HIGHLIGHT_COLOR = "#dc2626"
REFERENCE_COLOR = "#111827"
GRID_COLOR = "#d9e2ec"
TEXT_COLOR = "#172033"
MUTED_COLOR = "#64748b"
BACKGROUND = "#ffffff"
def read_csv_file(name: str) -> list[dict[str, str]]:
    path = DATA_DIR / name
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


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
    if group_no and group_no.isdigit():
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


def pct(value: float | None, digits: int = 1) -> str:
    if value is None:
        return "-"
    return f"{value:.{digits}f}%"


def number(value: float | int | None, digits: int = 1) -> str:
    if value is None:
        return "-"
    if isinstance(value, int) or float(value).is_integer():
        return str(int(value))
    return f"{value:.{digits}f}"


def parse_score(value: str | None) -> float | None:
    if value is None:
        return None
    cleaned = value.strip()
    if cleaned == "" or cleaned.upper() in {"NUL", "NULL", "NONE", "NA", "N/A"}:
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def parse_number(value: str | None) -> float | None:
    if value is None:
        return None
    cleaned = value.strip()
    if cleaned == "" or cleaned.upper() in {"NUL", "NULL", "NONE", "NA", "N/A"}:
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def is_missing_like(value: str | None) -> bool:
    if value is None:
        return True
    cleaned = value.strip()
    return cleaned == "" or cleaned.upper() in {"NUL", "NULL", "NONE", "NA", "N/A"}


def score_status(value: str | None) -> str:
    if parse_score(value) is not None:
        return "valid"
    if is_missing_like(value):
        return "missing"
    return "invalid"


def normalize_gender(value: str | None) -> str:
    cleaned = (value or "").strip().upper()
    if cleaned in {"男", "M", "MALE"}:
        return "male"
    if cleaned in {"女", "F", "FEMALE"}:
        return "female"
    return "unknown"


def normalize_share_flag(value: str | None) -> str:
    cleaned = (value or "").strip().upper()
    if cleaned in {"1", "Y", "YES", "TRUE", "T"}:
        return "shared"
    if cleaned in {"0", "N", "NO", "FALSE", "F"}:
        return "not_shared"
    return "other"


def value_counts(rows: Iterable[dict[str, str]], column: str) -> dict[str, int]:
    counter: Counter[str] = Counter()
    for row in rows:
        value = (row.get(column) or "").strip() or "空值"
        counter[value] += 1
    return dict(counter)


def nested_counts_by_group(
    rows: Iterable[dict[str, str]],
    classifier: Callable[[dict[str, str]], str],
) -> dict[str, dict[str, int]]:
    result: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for row in rows:
        group_no = (row.get("group_no") or "UNKNOWN").strip() or "UNKNOWN"
        result[group_no][classifier(row)] += 1
    return {group_no: dict(counts) for group_no, counts in result.items()}


def score_bins(sc_rows: Iterable[dict[str, str]]) -> dict[str, int]:
    bins = {
        "缺失/占位": 0,
        "0分": 0,
        "1-59": 0,
        "60-69": 0,
        "70-79": 0,
        "80-89": 0,
        "90-100": 0,
        "其他": 0,
    }
    for row in sc_rows:
        raw = row.get("score")
        score = parse_score(raw)
        if score is None:
            bins["缺失/占位" if is_missing_like(raw) else "其他"] += 1
        elif score == 0:
            bins["0分"] += 1
        elif score < 60:
            bins["1-59"] += 1
        elif score < 70:
            bins["60-69"] += 1
        elif score < 80:
            bins["70-79"] += 1
        elif score < 90:
            bins["80-89"] += 1
        elif score <= 100:
            bins["90-100"] += 1
        else:
            bins["其他"] += 1
    return bins


def score_stats_by_group(sc_rows: Iterable[dict[str, str]]) -> dict[str, dict[str, float]]:
    bucket: dict[str, dict[str, float]] = defaultdict(lambda: {
        "total": 0,
        "valid": 0,
        "missing": 0,
        "invalid": 0,
        "score_sum": 0.0,
        "pass": 0,
    })
    for row in sc_rows:
        group_no = (row.get("group_no") or "UNKNOWN").strip() or "UNKNOWN"
        stats = bucket[group_no]
        stats["total"] += 1
        raw = row.get("score")
        score = parse_score(raw)
        if score is None:
            if is_missing_like(raw):
                stats["missing"] += 1
            else:
                stats["invalid"] += 1
            continue
        stats["valid"] += 1
        stats["score_sum"] += score
        if score >= 60:
            stats["pass"] += 1

    result: dict[str, dict[str, float]] = {}
    for group_no, stats in bucket.items():
        valid = stats["valid"]
        result[group_no] = {
            **stats,
            "average": stats["score_sum"] / valid if valid else 0.0,
            "pass_rate": stats["pass"] * 100 / valid if valid else 0.0,
            "valid_rate": valid * 100 / stats["total"] if stats["total"] else 0.0,
        }
    return result


def course_workload_by_credit(course_rows: Iterable[dict[str, str]]) -> dict[str, dict[str, float]]:
    bucket: dict[str, dict[str, float]] = defaultdict(lambda: {
        "count": 0,
        "class_hours": 0.0,
        "practice_hours": 0.0,
    })
    for row in course_rows:
        credit = (row.get("credit") or "未知").strip() or "未知"
        class_hours = parse_number(row.get("class_hours"))
        practice_hours = parse_number(row.get("practice_hours"))
        if class_hours is None and practice_hours is None:
            continue
        bucket[credit]["count"] += 1
        bucket[credit]["class_hours"] += class_hours or 0.0
        bucket[credit]["practice_hours"] += practice_hours or 0.0

    result: dict[str, dict[str, float]] = {}
    for credit, values in bucket.items():
        count = values["count"] or 1
        result[credit] = {
            "理论学时": values["class_hours"] / count,
            "实践学时": values["practice_hours"] / count,
        }
    return result


def top_items(counts: dict[str, int], limit: int) -> dict[str, int]:
    return dict(sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:limit])


def write_svg(output_path: Path, elements: list[str]) -> None:
    output_path.write_text("\n".join(elements) + "\n", encoding="utf-8")


def chart_header(width: int, height: int, title: str, subtitle: str) -> list[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        f'<rect width="100%" height="100%" fill="{BACKGROUND}"/>',
        f'<text x="40" y="44" font-family="Arial, Microsoft YaHei, sans-serif" font-size="26" font-weight="700" fill="{TEXT_COLOR}">{svg_escape(title)}</text>',
        f'<text x="40" y="74" font-family="Arial, Microsoft YaHei, sans-serif" font-size="15" fill="{MUTED_COLOR}">{svg_escape(subtitle)}</text>',
    ]


def horizontal_bar_chart(
    title: str,
    subtitle: str,
    values: dict[str, float | int],
    output_path: Path,
    *,
    reference_value: float | None = None,
    reference_label: str | None = None,
    label_suffix: str = "组",
    sort_as_group: bool = True,
    sort_by_value: bool = False,
    color: str = BAR_COLOR,
    highlight_label: str | None = "18",
    value_formatter: Callable[[float], str] = lambda value: number(value),
    footer: str = "",
    x_max: float | None = None,
) -> None:
    if sort_by_value:
        rows = sorted(values.items(), key=lambda item: (-float(item[1]), str(item[0])))
    elif sort_as_group:
        rows = sorted(values.items(), key=lambda item: group_sort_key(item[0]))
    else:
        rows = list(values.items())

    max_data = max((float(value) for _, value in rows), default=0.0)
    max_reference = reference_value or 0.0
    max_value = max(x_max or 0.0, max_data, max_reference, 1.0)
    width = 1280
    row_height = 30
    top = 108
    bottom = 86 if footer else 70
    left = 150
    right = 120
    plot_width = width - left - right
    height = max(560, top + bottom + len(rows) * row_height)
    plot_height = len(rows) * row_height

    def x(value: float) -> float:
        return left + (value / max_value) * plot_width

    elements = chart_header(width, height, title, subtitle)
    tick_count = 5
    for i in range(tick_count + 1):
        value = max_value * i / tick_count
        tx = x(value)
        elements.append(f'<line x1="{tx:.1f}" y1="{top - 8}" x2="{tx:.1f}" y2="{top + plot_height}" stroke="{GRID_COLOR}" stroke-width="1"/>')
        elements.append(f'<text x="{tx:.1f}" y="{top + plot_height + 28}" text-anchor="middle" font-family="Arial, Microsoft YaHei, sans-serif" font-size="12" fill="{MUTED_COLOR}">{value_formatter(value)}</text>')

    if reference_value is not None:
        reference_x = x(reference_value)
        elements.append(f'<line x1="{reference_x:.1f}" y1="{top - 20}" x2="{reference_x:.1f}" y2="{top + plot_height}" stroke="{REFERENCE_COLOR}" stroke-width="2" stroke-dasharray="6 6"/>')
        elements.append(f'<text x="{reference_x + 8:.1f}" y="{top - 26}" font-family="Arial, Microsoft YaHei, sans-serif" font-size="13" fill="{REFERENCE_COLOR}">{svg_escape(reference_label or number(reference_value))}</text>')

    for index, (label, raw_value) in enumerate(rows):
        value = float(raw_value)
        y = top + index * row_height
        bar_width = max(1.0, x(value) - left)
        is_highlight = highlight_label is not None and label == highlight_label
        bar_color = HIGHLIGHT_COLOR if is_highlight else color
        label_weight = "700" if is_highlight else "400"
        label_text = f"{label}{label_suffix}" if label_suffix else label
        elements.append(f'<text x="{left - 18}" y="{y + 21}" text-anchor="end" font-family="Arial, Microsoft YaHei, sans-serif" font-size="13" font-weight="{label_weight}" fill="{TEXT_COLOR}">{svg_escape(label_text)}</text>')
        elements.append(f'<rect x="{left}" y="{y + 6}" width="{bar_width:.1f}" height="18" rx="3" fill="{bar_color}"/>')
        elements.append(f'<text x="{left + bar_width + 8:.1f}" y="{y + 21}" font-family="Arial, Microsoft YaHei, sans-serif" font-size="13" font-weight="{label_weight}" fill="{TEXT_COLOR}">{svg_escape(value_formatter(value))}</text>')

    if footer:
        elements.append(f'<text x="{left}" y="{height - 24}" font-family="Arial, Microsoft YaHei, sans-serif" font-size="12" fill="{MUTED_COLOR}">{svg_escape(footer)}</text>')
    elements.append("</svg>")
    write_svg(output_path, elements)


def stacked_bar_chart_by_group(
    title: str,
    subtitle: str,
    data_by_group: dict[str, dict[str, int]],
    categories: list[tuple[str, str, str]],
    output_path: Path,
    *,
    reference_value: float | None = None,
    reference_label: str | None = None,
    footer: str = "",
) -> None:
    groups = sorted(data_by_group, key=group_sort_key)
    totals = {group_no: sum(counts.values()) for group_no, counts in data_by_group.items()}
    max_value = max(max(totals.values(), default=0), reference_value or 0, 1)
    width = 1280
    row_height = 30
    top = 126
    bottom = 86 if footer else 72
    left = 120
    right = 132
    plot_width = width - left - right
    height = max(580, top + bottom + len(groups) * row_height)
    plot_height = len(groups) * row_height

    def x(value: float) -> float:
        return left + (value / max_value) * plot_width

    elements = chart_header(width, height, title, subtitle)

    legend_x = 40
    for key, label, color in categories:
        elements.append(f'<rect x="{legend_x}" y="91" width="14" height="14" rx="2" fill="{color}"/>')
        elements.append(f'<text x="{legend_x + 20}" y="103" font-family="Arial, Microsoft YaHei, sans-serif" font-size="13" fill="{TEXT_COLOR}">{svg_escape(label)}</text>')
        legend_x += max(86, len(label) * 15 + 36)

    tick_count = 5
    for i in range(tick_count + 1):
        value = round(max_value * i / tick_count)
        tx = x(value)
        elements.append(f'<line x1="{tx:.1f}" y1="{top - 8}" x2="{tx:.1f}" y2="{top + plot_height}" stroke="{GRID_COLOR}" stroke-width="1"/>')
        elements.append(f'<text x="{tx:.1f}" y="{top + plot_height + 28}" text-anchor="middle" font-family="Arial, Microsoft YaHei, sans-serif" font-size="12" fill="{MUTED_COLOR}">{value}</text>')

    if reference_value is not None:
        reference_x = x(reference_value)
        elements.append(f'<line x1="{reference_x:.1f}" y1="{top - 20}" x2="{reference_x:.1f}" y2="{top + plot_height}" stroke="{REFERENCE_COLOR}" stroke-width="2" stroke-dasharray="6 6"/>')
        elements.append(f'<text x="{reference_x + 8:.1f}" y="{top - 26}" font-family="Arial, Microsoft YaHei, sans-serif" font-size="13" fill="{REFERENCE_COLOR}">{svg_escape(reference_label or number(reference_value))}</text>')

    for index, group_no in enumerate(groups):
        counts = data_by_group[group_no]
        y = top + index * row_height
        current_x = left
        label_weight = "700" if group_no == "18" else "400"
        elements.append(f'<text x="{left - 18}" y="{y + 21}" text-anchor="end" font-family="Arial, Microsoft YaHei, sans-serif" font-size="13" font-weight="{label_weight}" fill="{TEXT_COLOR}">{svg_escape(group_no)}组</text>')
        for key, _, color in categories:
            count = counts.get(key, 0)
            segment_width = max(0.0, x(count) - left)
            if count > 0:
                elements.append(f'<rect x="{current_x:.1f}" y="{y + 6}" width="{segment_width:.1f}" height="18" rx="2" fill="{color}"/>')
                if segment_width >= 34:
                    elements.append(f'<text x="{current_x + segment_width / 2:.1f}" y="{y + 20}" text-anchor="middle" font-family="Arial, Microsoft YaHei, sans-serif" font-size="11" font-weight="700" fill="#ffffff">{count}</text>')
            current_x += segment_width
        total = totals[group_no]
        elements.append(f'<text x="{current_x + 8:.1f}" y="{y + 21}" font-family="Arial, Microsoft YaHei, sans-serif" font-size="13" font-weight="{label_weight}" fill="{TEXT_COLOR}">{total}</text>')
        if group_no == "18":
            elements.append(f'<rect x="{left - 4}" y="{y + 3}" width="{plot_width + 8}" height="24" fill="none" stroke="{HIGHLIGHT_COLOR}" stroke-width="2" rx="4"/>')

    if footer:
        elements.append(f'<text x="{left}" y="{height - 24}" font-family="Arial, Microsoft YaHei, sans-serif" font-size="12" fill="{MUTED_COLOR}">{svg_escape(footer)}</text>')
    elements.append("</svg>")
    write_svg(output_path, elements)


def vertical_bar_chart(
    title: str,
    subtitle: str,
    values: dict[str, int | float],
    output_path: Path,
    *,
    colors: dict[str, str] | None = None,
    footer: str = "",
    value_formatter: Callable[[float], str] = lambda value: number(value),
) -> None:
    rows = list(values.items())
    width = 1120
    height = 560
    left = 86
    right = 48
    top = 108
    bottom = 104 if footer else 82
    plot_width = width - left - right
    plot_height = height - top - bottom
    max_value = max((float(value) for _, value in rows), default=0.0) or 1.0

    def y(value: float) -> float:
        return top + plot_height - (value / max_value) * plot_height

    elements = chart_header(width, height, title, subtitle)
    tick_count = 5
    for i in range(tick_count + 1):
        value = max_value * i / tick_count
        ty = y(value)
        elements.append(f'<line x1="{left}" y1="{ty:.1f}" x2="{left + plot_width}" y2="{ty:.1f}" stroke="{GRID_COLOR}" stroke-width="1"/>')
        elements.append(f'<text x="{left - 12}" y="{ty + 4:.1f}" text-anchor="end" font-family="Arial, Microsoft YaHei, sans-serif" font-size="12" fill="{MUTED_COLOR}">{value_formatter(value)}</text>')

    slot = plot_width / max(len(rows), 1)
    bar_width = min(70, slot * 0.64)
    for index, (label, raw_value) in enumerate(rows):
        value = float(raw_value)
        x = left + slot * index + (slot - bar_width) / 2
        bar_top = y(value)
        color = (colors or {}).get(label, BAR_COLOR)
        elements.append(f'<rect x="{x:.1f}" y="{bar_top:.1f}" width="{bar_width:.1f}" height="{top + plot_height - bar_top:.1f}" rx="4" fill="{color}"/>')
        elements.append(f'<text x="{x + bar_width / 2:.1f}" y="{bar_top - 8:.1f}" text-anchor="middle" font-family="Arial, Microsoft YaHei, sans-serif" font-size="13" font-weight="700" fill="{TEXT_COLOR}">{svg_escape(value_formatter(value))}</text>')
        elements.append(f'<text x="{x + bar_width / 2:.1f}" y="{top + plot_height + 28}" text-anchor="middle" font-family="Arial, Microsoft YaHei, sans-serif" font-size="13" fill="{TEXT_COLOR}">{svg_escape(label)}</text>')

    if footer:
        elements.append(f'<text x="{left}" y="{height - 24}" font-family="Arial, Microsoft YaHei, sans-serif" font-size="12" fill="{MUTED_COLOR}">{svg_escape(footer)}</text>')
    elements.append("</svg>")
    write_svg(output_path, elements)


def grouped_bar_chart(
    title: str,
    subtitle: str,
    data: dict[str, dict[str, float]],
    series: list[tuple[str, str]],
    output_path: Path,
    *,
    footer: str = "",
) -> None:
    labels = sorted(data, key=lambda label: group_sort_key(label))
    width = 1120
    height = 560
    left = 86
    right = 54
    top = 124
    bottom = 104 if footer else 82
    plot_width = width - left - right
    plot_height = height - top - bottom
    max_value = max((values.get(name, 0.0) for values in data.values() for name, _ in series), default=0.0) or 1.0

    def y(value: float) -> float:
        return top + plot_height - (value / max_value) * plot_height

    elements = chart_header(width, height, title, subtitle)
    legend_x = 40
    for name, color in series:
        elements.append(f'<rect x="{legend_x}" y="91" width="14" height="14" rx="2" fill="{color}"/>')
        elements.append(f'<text x="{legend_x + 20}" y="103" font-family="Arial, Microsoft YaHei, sans-serif" font-size="13" fill="{TEXT_COLOR}">{svg_escape(name)}</text>')
        legend_x += len(name) * 15 + 42

    tick_count = 5
    for i in range(tick_count + 1):
        value = max_value * i / tick_count
        ty = y(value)
        elements.append(f'<line x1="{left}" y1="{ty:.1f}" x2="{left + plot_width}" y2="{ty:.1f}" stroke="{GRID_COLOR}" stroke-width="1"/>')
        elements.append(f'<text x="{left - 12}" y="{ty + 4:.1f}" text-anchor="end" font-family="Arial, Microsoft YaHei, sans-serif" font-size="12" fill="{MUTED_COLOR}">{number(value)}</text>')

    slot = plot_width / max(len(labels), 1)
    bar_width = min(32, slot * 0.62 / max(len(series), 1))
    for index, label in enumerate(labels):
        base_x = left + slot * index + (slot - bar_width * len(series)) / 2
        for series_index, (name, color) in enumerate(series):
            value = data[label].get(name, 0.0)
            x = base_x + bar_width * series_index
            bar_top = y(value)
            elements.append(f'<rect x="{x:.1f}" y="{bar_top:.1f}" width="{bar_width - 2:.1f}" height="{top + plot_height - bar_top:.1f}" rx="3" fill="{color}"/>')
        elements.append(f'<text x="{left + slot * index + slot / 2:.1f}" y="{top + plot_height + 28}" text-anchor="middle" font-family="Arial, Microsoft YaHei, sans-serif" font-size="13" fill="{TEXT_COLOR}">{svg_escape(label)}学分</text>')

    if footer:
        elements.append(f'<text x="{left}" y="{height - 24}" font-family="Arial, Microsoft YaHei, sans-serif" font-size="12" fill="{MUTED_COLOR}">{svg_escape(footer)}</text>')
    elements.append("</svg>")
    write_svg(output_path, elements)


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


def build_chart_files() -> dict[str, Path]:
    return {
        "student_total": CHART_DIR / "student_total_by_group.svg",
        "course_total": CHART_DIR / "course_total_by_group.svg",
        "sc_total": CHART_DIR / "sc_total_by_group.svg",
        "student_dept_stacked": CHART_DIR / "student_dept_stacked_by_group.svg",
        "course_dept_stacked": CHART_DIR / "course_dept_stacked_by_group.svg",
        "sc_dept_stacked": CHART_DIR / "sc_dept_stacked_by_group.svg",
        "student_gender_by_group": CHART_DIR / "student_gender_by_group.svg",
        "student_department_top": CHART_DIR / "student_department_top.svg",
        "course_credit_distribution": CHART_DIR / "course_credit_distribution.svg",
        "course_share_by_group": CHART_DIR / "course_share_by_group.svg",
        "course_workload_by_credit": CHART_DIR / "course_workload_by_credit.svg",
        "score_distribution": CHART_DIR / "score_distribution.svg",
        "score_validity_by_group": CHART_DIR / "score_validity_by_group.svg",
        "score_average_by_group": CHART_DIR / "score_average_by_group.svg",
        "score_pass_rate_by_group": CHART_DIR / "score_pass_rate_by_group.svg",
    }


def generate_charts(
    summary: dict[str, dict[str, dict[str, int]]],
    student_rows: list[dict[str, str]],
    course_rows: list[dict[str, str]],
    sc_rows: list[dict[str, str]],
    chart_files: dict[str, Path],
) -> dict[str, object]:
    for table_key in ["student", "course", "sc"]:
        horizontal_bar_chart(
            title=f"各组 {TABLE_NAMES[table_key]}",
            subtitle=f"按 group_no 汇总 row_count，参考线为标准值 {EXPECTED_TOTALS[table_key]}",
            values=totals_for_metric(summary, table_key),
            reference_value=EXPECTED_TOTALS[table_key],
            reference_label=f"标准值 {EXPECTED_TOTALS[table_key]}",
            output_path=chart_files[f"{table_key}_total"],
            footer="红色为本组 18 组；虚线为课程要求的标准提交数量。",
        )

    dept_categories = [
        ("A", "院系 A", DEPT_COLORS["A"]),
        ("B", "院系 B", DEPT_COLORS["B"]),
        ("C", "院系 C", DEPT_COLORS["C"]),
        ("UNKNOWN", "未知", DEPT_COLORS["UNKNOWN"]),
    ]
    stacked_bar_chart_by_group(
        title="各组 student 表 A/B/C 院系分布",
        subtitle="堆叠条形图展示每组 A、B、C 三个院系的学生数据数量",
        data_by_group=summary[METRICS["student"]],
        categories=dept_categories,
        reference_value=EXPECTED_TOTALS["student"],
        reference_label=f"标准合计 {EXPECTED_TOTALS['student']}",
        output_path=chart_files["student_dept_stacked"],
        footer="18 组为 A/B/C 各 50 名学生，结构符合标准提交规模。",
    )
    stacked_bar_chart_by_group(
        title="各组 course 表 A/B/C 院系分布",
        subtitle="展示每组课程数据在 A/B/C 三个院系中的分布",
        data_by_group=summary[METRICS["course"]],
        categories=dept_categories,
        reference_value=EXPECTED_TOTALS["course"],
        reference_label=f"标准合计 {EXPECTED_TOTALS['course']}",
        output_path=chart_files["course_dept_stacked"],
        footer="课程表的院系分布可用于观察是否存在某院系课程缺失或过量提交。",
    )
    stacked_bar_chart_by_group(
        title="各组 sc 表 A/B/C 院系分布",
        subtitle="展示每组选课成绩记录在 A/B/C 三个院系中的分布",
        data_by_group=summary[METRICS["sc"]],
        categories=dept_categories,
        reference_value=EXPECTED_TOTALS["sc"],
        reference_label=f"标准合计 {EXPECTED_TOTALS['sc']}",
        output_path=chart_files["sc_dept_stacked"],
        footer="sc 表通常规模最大，堆叠图更容易定位某个院系记录的整体偏移。",
    )

    gender_by_group = nested_counts_by_group(student_rows, lambda row: normalize_gender(row.get("gender")))
    stacked_bar_chart_by_group(
        title="各组 student 表性别字段分布",
        subtitle="将 男/M 归为男，女/F 归为女，其余归为未知或异常写法",
        data_by_group=gender_by_group,
        categories=[
            ("male", "男", CATEGORY_COLORS["male"]),
            ("female", "女", CATEGORY_COLORS["female"]),
            ("unknown", "未知/异常", CATEGORY_COLORS["unknown"]),
        ],
        reference_value=EXPECTED_TOTALS["student"],
        reference_label=f"标准合计 {EXPECTED_TOTALS['student']}",
        output_path=chart_files["student_gender_by_group"],
        footer="该图保留字段写法差异，便于后续清洗和异常分析继续细查。",
    )

    department_top = top_items(value_counts(student_rows, "department"), 18)
    horizontal_bar_chart(
        title="student 表原始 department 字段 Top 18",
        subtitle="直接统计原始专业/学院名称，展示跨组字段命名差异",
        values=department_top,
        output_path=chart_files["student_department_top"],
        label_suffix="",
        sort_as_group=False,
        sort_by_value=True,
        color="#0f766e",
        highlight_label=None,
        footer="该图不做同义词合并，用来直观看到学院/专业名称的非标准写法。",
    )

    credit_counts = dict(sorted(value_counts(course_rows, "credit").items(), key=lambda item: group_sort_key(item[0])))
    vertical_bar_chart(
        title="course 表学分分布",
        subtitle="统计所有课程记录的 credit 字段",
        values=credit_counts,
        output_path=chart_files["course_credit_distribution"],
        colors={"1": "#64748b", "2": "#2563eb", "3": "#16a34a", "4": "#f59e0b", "5": "#dc2626"},
        footer="大部分课程集中在 2-4 学分，少量 1/5 学分课程可在后续课程特征分析中展开。",
    )

    share_by_group = nested_counts_by_group(course_rows, lambda row: normalize_share_flag(row.get("share_flag")))
    stacked_bar_chart_by_group(
        title="各组 course 表共享课程标记分布",
        subtitle="将 1/Y 归为共享，0/N 归为非共享，其余归为其他写法",
        data_by_group=share_by_group,
        categories=[
            ("shared", "共享", CATEGORY_COLORS["shared"]),
            ("not_shared", "非共享", CATEGORY_COLORS["not_shared"]),
            ("other", "其他写法", CATEGORY_COLORS["other"]),
        ],
        reference_value=EXPECTED_TOTALS["course"],
        reference_label=f"标准合计 {EXPECTED_TOTALS['course']}",
        output_path=chart_files["course_share_by_group"],
        footer="共享标记存在 0/1 与 Y/N 两类写法，图中已统一到三个展示类别。",
    )

    workload = course_workload_by_credit(course_rows)
    grouped_bar_chart(
        title="course 表不同学分课程平均学时",
        subtitle="按 credit 分组，分别展示 class_hours 与 practice_hours 的平均值",
        data=workload,
        series=[
            ("理论学时", CATEGORY_COLORS["class_hours"]),
            ("实践学时", CATEGORY_COLORS["practice_hours"]),
        ],
        output_path=chart_files["course_workload_by_credit"],
        footer="该图用于观察学分与理论/实践学时之间是否大体匹配。",
    )

    score_distribution = score_bins(sc_rows)
    vertical_bar_chart(
        title="sc 表成绩分布总览",
        subtitle="缺失/占位包含空值、NUL、NULL；0 分单独列出",
        values=score_distribution,
        output_path=chart_files["score_distribution"],
        colors={
            "缺失/占位": "#64748b",
            "0分": "#dc2626",
            "1-59": "#f97316",
            "60-69": "#f59e0b",
            "70-79": "#16a34a",
            "80-89": "#2563eb",
            "90-100": "#7c3aed",
            "其他": "#334155",
        },
        footer="这是任务一的描述性展示，异常值归因留给任务二继续分析。",
    )

    score_validity = nested_counts_by_group(sc_rows, lambda row: score_status(row.get("score")))
    stacked_bar_chart_by_group(
        title="各组 sc 表成绩字段有效性",
        subtitle="按 group_no 展示数值成绩、缺失/占位和其他非法写法",
        data_by_group=score_validity,
        categories=[
            ("valid", "数值成绩", CATEGORY_COLORS["valid"]),
            ("missing", "缺失/占位", CATEGORY_COLORS["missing"]),
            ("invalid", "非法写法", CATEGORY_COLORS["invalid"]),
        ],
        reference_value=EXPECTED_TOTALS["sc"],
        reference_label=f"标准合计 {EXPECTED_TOTALS['sc']}",
        output_path=chart_files["score_validity_by_group"],
        footer="该图能快速看出每组成绩字段是否可用于后续统计分析。",
    )

    score_stats = score_stats_by_group(sc_rows)
    averages = {group_no: stats["average"] for group_no, stats in score_stats.items()}
    horizontal_bar_chart(
        title="各组 sc 表数值成绩平均分",
        subtitle="仅使用可解析为数字的 score，缺失/占位不参与均值",
        values=averages,
        output_path=chart_files["score_average_by_group"],
        reference_value=60,
        reference_label="及格线 60",
        color="#0f766e",
        value_formatter=lambda value: number(value, 1),
        footer="平均分是描述性指标，需结合有效成绩数量一起解释。",
        x_max=100,
    )

    pass_rates = {group_no: stats["pass_rate"] for group_no, stats in score_stats.items()}
    horizontal_bar_chart(
        title="各组 sc 表数值成绩及格率",
        subtitle="及格率 = 数值成绩中 score >= 60 的记录数 / 数值成绩记录数",
        values=pass_rates,
        output_path=chart_files["score_pass_rate_by_group"],
        reference_value=80,
        reference_label="参考线 80%",
        color="#7c3aed",
        value_formatter=lambda value: pct(value, 1),
        footer="缺失/占位成绩不进入分母，后续分析应同步报告各组有效成绩比例。",
        x_max=100,
    )

    return {
        "gender_by_group": gender_by_group,
        "department_top": department_top,
        "credit_counts": credit_counts,
        "share_by_group": share_by_group,
        "score_distribution": score_distribution,
        "score_validity": score_validity,
        "score_stats": score_stats,
    }


def write_html_report(
    summary: dict[str, dict[str, dict[str, int]]],
    quality: dict[str, int],
    chart_files: dict[str, Path],
    deviation_csv: Path,
    derived: dict[str, object],
) -> Path:
    group18 = {
        table_key: totals_for_metric(summary, table_key).get("18", 0)
        for table_key in ["student", "course", "sc"]
    }
    score_stats = derived["score_stats"]
    group18_score = score_stats.get("18", {}) if isinstance(score_stats, dict) else {}
    score_distribution = derived["score_distribution"]
    missing_scores = score_distribution.get("缺失/占位", 0) if isinstance(score_distribution, dict) else 0
    def rel(path: Path) -> str:
        return path.relative_to(OUTPUT_DIR).as_posix()

    def figure(key: str, caption: str) -> str:
        path = chart_files[key]
        return f"""  <figure>
    <img src="{rel(path)}" alt="{svg_escape(caption)}">
    <figcaption>{svg_escape(caption)}</figcaption>
  </figure>"""

    task_rows = "\n".join([
        "<tr><td>1</td><td>数据的可视化</td><td>已完成本报告：覆盖 student、course、sc 三张表的规模、字段分布和基础成绩画像。</td></tr>",
        "<tr><td>2</td><td>异常数据发现</td><td>后续可从数量偏差、缺失成绩、异常组号、字段写法不一致继续深入。</td></tr>",
        "<tr><td>3</td><td>成绩与课程特征分析</td><td>可基于本报告的成绩/课程图，继续做均分、及格率、学分学时与课程共享关系分析。</td></tr>",
        "<tr><td>4</td><td>相似分析</td><td>可用各组的规模、院系比例、成绩分布、课程画像构建组间相似度。</td></tr>",
        "<tr><td>5</td><td>报告整理</td><td>汇总各任务图表、方法和结论，形成最终实验报告。</td></tr>",
    ])

    html_text = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>任务一：HW4 数据可视化总览</title>
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
      font-size: 30px;
      margin: 0 0 10px;
    }}
    h2 {{
      font-size: 21px;
      margin: 32px 0 12px;
    }}
    p {{
      line-height: 1.68;
      margin: 8px 0;
    }}
    .kpis {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 12px;
      margin: 20px 0 10px;
    }}
    .kpi {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 14px 16px;
      min-width: 0;
    }}
    .kpi .label {{
      color: var(--muted);
      font-size: 13px;
    }}
    .kpi .value {{
      font-size: 26px;
      font-weight: 700;
      margin-top: 4px;
      word-break: break-word;
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
      vertical-align: top;
    }}
    th {{
      background: var(--panel);
      text-align: left;
    }}
    .note {{
      color: var(--muted);
      font-size: 14px;
    }}
    .accent {{
      color: var(--accent);
      font-weight: 700;
    }}
    code {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 4px;
      padding: 1px 5px;
    }}
    @media (max-width: 820px) {{
      main {{
        width: min(100% - 28px, 1180px);
        margin-top: 20px;
      }}
      .kpis {{
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }}
    }}
  </style>
</head>
<body>
<main>
  <header>
    <h1>任务一：HW4 数据可视化总览</h1>
    <p>数据来源为 <code>work4/hw4_20260614</code> 下的 <code>student.csv</code>、<code>course.csv</code>、<code>sc.csv</code>、汇总表和质量快照。本页用于完成“数据的可视化”任务，并为后续异常发现、成绩/课程特征分析和相似分析提供入口。</p>
    <p class="note">图中红色高亮为本组 18 组；提交规模参考值为 student=150、course=30、sc=750。</p>
  </header>

  <h2>任务拆解</h2>
  <table>
    <thead><tr><th>序号</th><th>任务</th><th>当前处理方式</th></tr></thead>
    <tbody>{task_rows}</tbody>
  </table>

  <h2>数据概览</h2>
  <section class="kpis">
    <div class="kpi"><div class="label">student 总量</div><div class="value">{quality.get('student_total', 0)}</div></div>
    <div class="kpi"><div class="label">course 总量</div><div class="value">{quality.get('course_total', 0)}</div></div>
    <div class="kpi"><div class="label">sc 总量</div><div class="value">{quality.get('sc_total', 0)}</div></div>
    <div class="kpi"><div class="label">成绩缺失/占位</div><div class="value">{missing_scores}</div></div>
  </section>
  <section class="kpis">
    <div class="kpi"><div class="label">18 组 student</div><div class="value">{group18['student']}</div></div>
    <div class="kpi"><div class="label">18 组 course</div><div class="value">{group18['course']}</div></div>
    <div class="kpi"><div class="label">18 组 sc</div><div class="value">{group18['sc']}</div></div>
    <div class="kpi"><div class="label">18 组数值成绩均分</div><div class="value">{number(group18_score.get('average'), 1)}</div></div>
  </section>

  <h2>1. 提交规模与院系结构</h2>
{figure('student_total', '图 1：各组 student 表提交数量，虚线为标准 150 行。')}
{figure('course_total', '图 2：各组 course 表提交数量，虚线为标准 30 行。')}
{figure('sc_total', '图 3：各组 sc 表提交数量，虚线为标准 750 行。')}
{figure('student_dept_stacked', '图 4：student 表按 A/B/C 院系堆叠展示。')}
{figure('course_dept_stacked', '图 5：course 表按 A/B/C 院系堆叠展示。')}
{figure('sc_dept_stacked', '图 6：sc 表按 A/B/C 院系堆叠展示。')}

  <h2>2. 学生数据画像</h2>
{figure('student_gender_by_group', '图 7：student 表性别字段分布，统一展示男、女、未知/异常写法。')}
{figure('student_department_top', '图 8：student 表原始 department 字段 Top 18，保留原始命名差异。')}

  <h2>3. 课程数据画像</h2>
{figure('course_credit_distribution', '图 9：course 表学分分布。')}
{figure('course_share_by_group', '图 10：各组 course 表共享课程标记分布。')}
{figure('course_workload_by_credit', '图 11：不同学分课程的平均理论学时和实践学时。')}

  <h2>4. 成绩数据画像</h2>
{figure('score_distribution', '图 12：sc 表成绩分布总览，缺失/占位与 0 分单独呈现。')}
{figure('score_validity_by_group', '图 13：各组成绩字段有效性，展示数值成绩、缺失/占位、非法写法。')}
{figure('score_average_by_group', '图 14：各组数值成绩平均分，缺失/占位不参与均值。')}
{figure('score_pass_rate_by_group', '图 15：各组数值成绩及格率，缺失/占位不进入分母。')}

  <h2>可写入报告的简短说明</h2>
  <p>本次可视化覆盖三张原始数据表：从提交规模看，本组 <span class="accent">18 组</span> 的 student/course/sc 数量分别为 {group18['student']}、{group18['course']}、{group18['sc']}，符合标准提交规模；从结构看，student/course/sc 均可按 A/B/C 院系继续观察分布。</p>
  <p>字段层面，student 表的 gender 和 department 存在多种写法；course 表的 share_flag 同时出现 0/1 与 Y/N 写法；sc 表中共有 {missing_scores} 条成绩为空值、NUL 或 NULL，占位成绩需要在后续异常数据发现中重点解释。完整数量偏差明细见 <code>{svg_escape(deviation_csv.name)}</code>。</p>
</main>
</body>
</html>
"""
    report_path = OUTPUT_DIR / "task1_visualization_report.html"
    report_path.write_text(html_text, encoding="utf-8")
    (OUTPUT_DIR / "distribution_report.html").write_text(html_text, encoding="utf-8")
    return report_path


def write_readme(chart_files: dict[str, Path]) -> Path:
    chart_lines = "\n".join(
        f"- `{path.relative_to(OUTPUT_DIR).as_posix()}`"
        for path in chart_files.values()
    )
    readme_text = f"""# 任务一：HW4 数据可视化

## 任务拆解

1. 数据的可视化：当前脚本已完成，覆盖 `student`、`course`、`sc` 三张表的规模、院系结构、字段分布、课程特征和成绩概览。
2. 异常数据发现：建议基于数量偏差、异常组号、成绩缺失、字段写法不一致继续展开。
3. 成绩与课程特征分析：建议进一步分析均分、及格率、课程学分/学时、共享课程与成绩之间的关系。
4. 相似分析：建议把各组规模、院系比例、课程画像、成绩分布转为特征向量，寻找与 18 组最相似的组。
5. 报告整理：汇总图表、方法和结论，形成最终实验报告。

## 重新生成

在项目根目录运行：

```bash
python work4/visualization.py
```

脚本会读取：

- `work4/hw4_20260614/student.csv`
- `work4/hw4_20260614/course.csv`
- `work4/hw4_20260614/sc.csv`
- `work4/hw4_20260614/group_dept_summary.csv`
- `work4/hw4_20260614/quality_snapshot.csv`

并导出：

- `work4/task1_visualization_report.html`：任务一主报告，可直接浏览和截图。
- `work4/distribution_report.html`：与主报告内容一致，保留旧入口。
- `work4/distribution_deviations.csv`：与标准提交规模存在偏差的记录。
{chart_lines}

## 截图建议

优先打开 `work4/task1_visualization_report.html`，按页面章节截图：

1. 数据概览 KPI 与任务拆解表。
2. 提交规模与 A/B/C 院系结构。
3. 学生 gender/department 字段画像。
4. 课程 credit、share_flag、学时画像。
5. 成绩分布、成绩字段有效性、均分和及格率。

## 可写入报告的结论

- 18 组提交规模符合标准：`student=150`、`course=30`、`sc=750`。
- 18 组在三张表上均可按 A/B/C 院系形成完整结构，适合作为后续相似分析的基准组。
- `student.gender`、`student.department`、`course.share_flag` 存在多种字段写法，是后续数据清洗和异常分析的入口。
- `sc.score` 中存在空值、`NUL`、`NULL` 等占位成绩，任务二需要进一步判断这些记录的来源和影响。
"""
    path = OUTPUT_DIR / "visualization_README.md"
    path.write_text(readme_text, encoding="utf-8")
    return path


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    CHART_DIR.mkdir(parents=True, exist_ok=True)

    summary = read_group_summary()
    quality = read_quality_snapshot()
    student_rows = read_csv_file("student.csv")
    course_rows = read_csv_file("course.csv")
    sc_rows = read_csv_file("sc.csv")
    chart_files = build_chart_files()

    derived = generate_charts(summary, student_rows, course_rows, sc_rows, chart_files)
    deviations = deviation_rows(summary)
    deviation_csv = write_deviation_csv(deviations)
    report_path = write_html_report(summary, quality, chart_files, deviation_csv, derived)
    readme_path = write_readme(chart_files)

    print("Generated visualization outputs:")
    print(report_path)
    print(OUTPUT_DIR / "distribution_report.html")
    for path in chart_files.values():
        print(path)
    print(deviation_csv)
    print(readme_path)


if __name__ == "__main__":
    main()
