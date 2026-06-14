# 数据提交规模与院系分布可视化

## 重新导出

在项目根目录运行：

```bash
python3 work4/visualization.py
```

脚本会读取：

- `work4/hw4_20260614/group_dept_summary.csv`
- `work4/hw4_20260614/quality_snapshot.csv`

并导出：

- `work4/distribution_report.html`：可直接用浏览器打开并截图的总览页。
- `work4/charts/student_total_by_group.svg`：各组 `student` 表提交数量。
- `work4/charts/course_total_by_group.svg`：各组 `course` 表提交数量。
- `work4/charts/sc_total_by_group.svg`：各组 `sc` 表提交数量。
- `work4/charts/student_dept_stacked_by_group.svg`：各组 `student` 表 A/B/C 院系分布。
- `work4/distribution_deviations.csv`：与标准提交规模偏差较大的组。

## 截图建议

优先打开 `work4/distribution_report.html`，按页面顺序截图：

1. 顶部 KPI 区域，展示服务器总体数据和 18 组数据规模。
2. 三张提交数量图，分别对应 `student`、`course`、`sc`。
3. A/B/C 院系分布堆叠图。
4. 数量异常组初筛表。

## 可写入报告的结论

- 18 组提交规模符合标准：`student=150`、`course=30`、`sc=750`。
- 18 组 `student` 表中 A/B/C 三个院系各 50 条，院系分布均衡。
- 多数组的数据量接近标准提交规模，但第 2 组明显偏高，是后续异常分析重点对象。
- 个别组存在提交数量不足、院系缺失或异常组号，建议由异常检测部分继续深入分析。
