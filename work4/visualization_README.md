# 任务一：HW4 数据可视化

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
- `charts/student_total_by_group.svg`
- `charts/course_total_by_group.svg`
- `charts/sc_total_by_group.svg`
- `charts/student_dept_stacked_by_group.svg`
- `charts/course_dept_stacked_by_group.svg`
- `charts/sc_dept_stacked_by_group.svg`
- `charts/student_gender_by_group.svg`
- `charts/student_department_top.svg`
- `charts/course_credit_distribution.svg`
- `charts/course_share_by_group.svg`
- `charts/course_workload_by_credit.svg`
- `charts/score_distribution.svg`
- `charts/score_validity_by_group.svg`
- `charts/score_average_by_group.svg`
- `charts/score_pass_rate_by_group.svg`

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
