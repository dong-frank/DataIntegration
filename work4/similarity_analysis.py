#!/usr/bin/env python3
"""Task 4 similarity analysis for HW4 exported dataset.

Run from the repository root:

    python work4/similarity_analysis.py

The script reads CSV files from ``work4/hw4_20260614/``, computes multi-
dimensional feature vectors for every group, and ranks all groups by their
standardised Euclidean distance to Group 18 (our group).  Results are written
to ``work4/similarity_results.csv`` and ``work4/task4_similarity_report.html``.
Uses only the Python standard library.
"""

from __future__ import annotations

import csv
import html
import math
from collections import defaultdict
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "hw4_20260614"
OUTPUT_DIR = BASE_DIR

OUR_GROUP = 18
ANOMALOUS_GROUP = 221250099   # outlier group excluded from analysis

SCORE_BINS = [(0, 60), (60, 70), (70, 80), (80, 90), (90, 101)]
BIN_LABELS = ["<60", "60-69", "70-79", "80-89", "90-100"]

# Feature names used for distance computation
FEATURE_NAMES = [
    "stu_count",
    "gender_ratio_male",
    "course_count",
    "avg_credit",
    "avg_class_hours",
    "avg_practice_hours",
    "share_ratio",
    "avg_score",
    "std_score",
    "pass_rate",
    "score_q25",
    "score_q75",
    "bin_fail",
    "bin_60s",
    "bin_70s",
    "bin_80s",
    "bin_90s",
    "enrollment_density",
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _std(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    m = _mean(values)
    return math.sqrt(sum((v - m) ** 2 for v in values) / (len(values) - 1))


def _quantile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    s = sorted(values)
    idx = q * (len(s) - 1)
    lo, hi = int(idx), min(int(idx) + 1, len(s) - 1)
    return s[lo] + (s[hi] - s[lo]) * (idx - lo)


def _bin_distribution(scores: list[float]) -> list[float]:
    if not scores:
        return [0.0] * len(SCORE_BINS)
    counts = [0] * len(SCORE_BINS)
    for s in scores:
        for i, (lo, hi) in enumerate(SCORE_BINS):
            if lo <= s < hi:
                counts[i] += 1
                break
    total = len(scores)
    return [c / total for c in counts]


def _standardise(matrix: dict[int, list[float]]) -> dict[int, list[float]]:
    """Z-score standardise each feature column across all groups."""
    groups = list(matrix.keys())
    n_feat = len(FEATURE_NAMES)
    col_means = []
    col_stds = []
    for j in range(n_feat):
        col = [matrix[g][j] for g in groups]
        m = _mean(col)
        s = _std(col)
        col_means.append(m)
        col_stds.append(s if s > 0 else 1.0)

    result = {}
    for g in groups:
        result[g] = [
            (matrix[g][j] - col_means[j]) / col_stds[j]
            for j in range(n_feat)
        ]
    return result


def _euclidean(a: list[float], b: list[float]) -> float:
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_students() -> dict[int, list[dict]]:
    groups: dict[int, list[dict]] = defaultdict(list)
    with open(DATA_DIR / "student.csv", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            g = int(row["group_no"])
            if g == ANOMALOUS_GROUP:
                continue
            groups[g].append(row)
    return dict(groups)


def load_courses() -> dict[int, list[dict]]:
    groups: dict[int, list[dict]] = defaultdict(list)
    with open(DATA_DIR / "course.csv", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            g = int(row["group_no"])
            if g == ANOMALOUS_GROUP:
                continue
            groups[g].append(row)
    return dict(groups)


def load_sc() -> dict[int, list[dict]]:
    groups: dict[int, list[dict]] = defaultdict(list)
    with open(DATA_DIR / "sc.csv", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            g = int(row["group_no"])
            if g == ANOMALOUS_GROUP:
                continue
            groups[g].append(row)
    return dict(groups)


# ---------------------------------------------------------------------------
# Feature extraction
# ---------------------------------------------------------------------------

def extract_features(
    students: dict[int, list[dict]],
    courses: dict[int, list[dict]],
    sc: dict[int, list[dict]],
) -> dict[int, list[float]]:
    all_groups = sorted(set(students) | set(courses) | set(sc))
    features: dict[int, list[float]] = {}

    for g in all_groups:
        s_rows = students.get(g, [])
        c_rows = courses.get(g, [])
        sc_rows = sc.get(g, [])

        # --- student ---
        stu_count = float(len(s_rows))
        gender_ratio = (
            sum(1 for r in s_rows if r["gender"] == "男") / len(s_rows)
            if s_rows else 0.0
        )

        # --- course ---
        course_count = float(len(c_rows))
        def _safe_floats(rows: list[dict], key: str) -> list[float]:
            result = []
            for r in rows:
                try:
                    v = float(r[key])
                    result.append(v)
                except (ValueError, KeyError, TypeError):
                    pass
            return result

        credits = _safe_floats(c_rows, "credit")
        class_hours = _safe_floats(c_rows, "class_hours")
        practice_hours = _safe_floats(c_rows, "practice_hours")
        share_flags = _safe_floats(c_rows, "share_flag")

        avg_credit = _mean(credits)
        avg_class_hours = _mean(class_hours)
        avg_practice_hours = _mean(practice_hours)
        share_ratio = _mean(share_flags) if share_flags else 0.0

        # --- score ---
        scores: list[float] = []
        for r in sc_rows:
            try:
                scores.append(float(r["score"]))
            except (ValueError, KeyError):
                pass

        avg_score = _mean(scores)
        std_score = _std(scores)
        pass_rate = (
            sum(1 for s in scores if s >= 60) / len(scores) if scores else 0.0
        )
        score_q25 = _quantile(scores, 0.25)
        score_q75 = _quantile(scores, 0.75)
        bin_dist = _bin_distribution(scores)

        enrollment_density = len(sc_rows) / stu_count if stu_count > 0 else 0.0

        features[g] = [
            stu_count,
            gender_ratio,
            course_count,
            avg_credit,
            avg_class_hours,
            avg_practice_hours,
            share_ratio,
            avg_score,
            std_score,
            pass_rate,
            score_q25,
            score_q75,
            bin_dist[0],
            bin_dist[1],
            bin_dist[2],
            bin_dist[3],
            bin_dist[4],
            enrollment_density,
        ]

    return features


# ---------------------------------------------------------------------------
# Similarity ranking
# ---------------------------------------------------------------------------

def rank_groups(
    features: dict[int, list[float]], target: int
) -> list[tuple[int, float]]:
    scaled = _standardise(features)
    target_vec = scaled[target]
    distances = []
    for g, vec in scaled.items():
        if g == target:
            continue
        distances.append((g, _euclidean(target_vec, vec)))
    distances.sort(key=lambda x: x[1])
    return distances


# ---------------------------------------------------------------------------
# CSV output
# ---------------------------------------------------------------------------

def write_csv(
    ranking: list[tuple[int, float]],
    features: dict[int, list[float]],
) -> Path:
    out = OUTPUT_DIR / "similarity_results.csv"
    header = ["rank", "group_no", "distance"] + FEATURE_NAMES
    with open(out, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        # write our group first (rank 0)
        our_feat = features[OUR_GROUP]
        writer.writerow(
            [0, OUR_GROUP, 0.0] + [f"{v:.4f}" for v in our_feat]
        )
        for rank, (g, dist) in enumerate(ranking, 1):
            feat = features[g]
            writer.writerow(
                [rank, g, f"{dist:.4f}"] + [f"{v:.4f}" for v in feat]
            )
    return out


# ---------------------------------------------------------------------------
# HTML report
# ---------------------------------------------------------------------------

def _feat_row(label: str, our_val: float, other_val: float) -> str:
    diff = other_val - our_val
    diff_str = f"+{diff:.3f}" if diff >= 0 else f"{diff:.3f}"
    style = "color:#c0392b;" if abs(diff) > 0.5 * max(abs(our_val), 1) else ""
    return (
        f"<tr><td>{html.escape(label)}</td>"
        f"<td>{our_val:.3f}</td>"
        f"<td>{other_val:.3f}</td>"
        f"<td style='{style}'>{diff_str}</td></tr>\n"
    )


def write_html(
    ranking: list[tuple[int, float]],
    features: dict[int, list[float]],
) -> Path:
    our_feat = features[OUR_GROUP]
    top5 = ranking[:5]

    # build comparison table rows for top-5
    comparison_blocks = []
    for rank, (g, dist) in enumerate(top5, 1):
        other_feat = features[g]
        rows_html = "".join(
            _feat_row(name, our_feat[i], other_feat[i])
            for i, name in enumerate(FEATURE_NAMES)
        )
        comparison_blocks.append(
            f"<h3>#{rank} Group {g} &nbsp;<small style='color:#666;font-weight:normal'>"
            f"distance = {dist:.4f}</small></h3>\n"
            f"<table class='cmp'>\n"
            f"<thead><tr><th>Feature</th><th>Group {OUR_GROUP} (ours)</th>"
            f"<th>Group {g}</th><th>Diff</th></tr></thead>\n"
            f"<tbody>{rows_html}</tbody></table>\n"
        )

    # full ranking table
    full_rows = ""
    for rank, (g, dist) in enumerate(ranking, 1):
        bar_pct = min(100, int(dist / ranking[-1][1] * 100)) if ranking else 0
        bar = (
            f"<div style='display:inline-block;width:{bar_pct}%;height:10px;"
            f"background:#3498db;vertical-align:middle'></div>"
        )
        full_rows += (
            f"<tr><td>{rank}</td><td><b>{g}</b></td>"
            f"<td>{dist:.4f} {bar}</td></tr>\n"
        )

    html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>Group Similarity Analysis — Group {OUR_GROUP}</title>
<style>
  body {{ font-family: 'Segoe UI', sans-serif; margin: 40px; color: #333; }}
  h1 {{ color: #2c3e50; }}
  h2 {{ color: #2980b9; border-bottom: 2px solid #2980b9; padding-bottom: 4px; }}
  h3 {{ color: #27ae60; }}
  table {{ border-collapse: collapse; margin-bottom: 20px; width: 100%; max-width: 800px; }}
  th, td {{ border: 1px solid #ccc; padding: 6px 12px; text-align: left; font-size: 13px; }}
  th {{ background: #f0f4f8; }}
  tr:nth-child(even) {{ background: #fafafa; }}
  table.cmp td:nth-child(2), table.cmp td:nth-child(3) {{ text-align: right; }}
  .badge {{ display:inline-block; background:#2980b9; color:#fff;
            border-radius:4px; padding:2px 8px; font-size:12px; }}
  .summary {{ background:#eaf4fb; border-left:4px solid #2980b9;
              padding:12px 20px; margin:20px 0; border-radius:4px; }}
</style>
</head>
<body>
<h1>Group Similarity Analysis</h1>
<div class="summary">
  <b>Our group:</b> <span class="badge">Group {OUR_GROUP}</span> &nbsp;
  <b>Most similar group:</b> <span class="badge">Group {top5[0][0]}</span>
  &nbsp; (distance = {top5[0][1]:.4f})<br><br>
  Analysis dimensions: {len(FEATURE_NAMES)} features across student composition,
  course structure, and score distribution.
  Distance metric: standardised Euclidean distance (z-score normalised).
</div>

<h2>Full Ranking</h2>
<table>
<thead><tr><th>Rank</th><th>Group</th><th>Distance (smaller = more similar)</th></tr></thead>
<tbody>{full_rows}</tbody>
</table>

<h2>Top-5 Detailed Comparison with Group {OUR_GROUP}</h2>
{"".join(comparison_blocks)}

<hr>
<p style="color:#999;font-size:12px">
  Generated by similarity_analysis.py &nbsp;|&nbsp;
  Data: hw4_20260614 &nbsp;|&nbsp;
  Group {OUR_GROUP} features: stu_count={our_feat[0]:.0f},
  avg_score={our_feat[7]:.2f}, pass_rate={our_feat[9]:.2%},
  course_count={our_feat[2]:.0f}
</p>
</body>
</html>
"""

    out = OUTPUT_DIR / "task4_similarity_report.html"
    with open(out, "w", encoding="utf-8") as f:
        f.write(html_content)
    return out


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("Loading data...")
    students = load_students()
    courses = load_courses()
    sc = load_sc()

    print("Extracting features...")
    features = extract_features(students, courses, sc)
    print(f"  Groups found: {sorted(features)}")

    print(f"Ranking groups by similarity to Group {OUR_GROUP}...")
    ranking = rank_groups(features, OUR_GROUP)

    print("\n=== Similarity Ranking (top 10) ===")
    for rank, (g, dist) in enumerate(ranking[:10], 1):
        print(f"  #{rank:2d}  Group {g:3d}  distance={dist:.4f}")

    csv_path = write_csv(ranking, features)
    html_path = write_html(ranking, features)

    print(f"\nCSV  -> {csv_path}")
    print(f"HTML -> {html_path}")
    print("Done.")


if __name__ == "__main__":
    main()
