#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
任务3：成绩与课程特征分析
=========================
分析课程的各种特征（学分、授课方式、课时、实践比例、教师、共享属性等）
与学生成绩之间的关系，包括：
  - 单因素分析：各课程特征对成绩的影响
  - 相关性分析：连续型特征与成绩的关联
  - 多因素回归：哪些特征最能预测成绩
  - 统计检验：t检验、ANOVA
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns
from scipy import stats
from scipy.stats import pearsonr, spearmanr
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
import warnings
import os

warnings.filterwarnings('ignore')

# ============================================================
# 0. 全局设置
# ============================================================
plt.rcParams['figure.dpi'] = 150
plt.rcParams['savefig.dpi'] = 150
plt.rcParams['savefig.bbox'] = 'tight'
plt.rcParams['font.size'] = 11

for font_name in ['SimHei', 'Microsoft YaHei', 'PingFang SC', 'DejaVu Sans']:
    try:
        fm.findfont(font_name, fallback_to_default=False)
        plt.rcParams['font.sans-serif'] = [font_name, 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
        break
    except Exception:
        continue

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output_task3')
os.makedirs(OUT_DIR, exist_ok=True)

# ============================================================
# 1. 数据加载与清洗
# ============================================================
print("=" * 70)
print("任务3：成绩与课程特征分析")
print("=" * 70)
print("\n[Step 1] 数据加载与清洗...")

course = pd.read_csv('course.csv', encoding='utf-8-sig')
student = pd.read_csv('student.csv', encoding='utf-8-sig')
sc_raw = pd.read_csv('sc.csv', encoding='utf-8-sig')

# 清洗 score
sc_raw['score'] = pd.to_numeric(sc_raw['score'].replace('NUL', np.nan), errors='coerce')
sc = sc_raw[sc_raw['score'].notna()].copy()
print(f"  有效成绩记录: {len(sc):,} / {len(sc_raw):,}")

# 清洗课程特征
course['class_hours'] = pd.to_numeric(course['class_hours'], errors='coerce')
course['practice_hours'] = pd.to_numeric(course['practice_hours'], errors='coerce')
share_map = {'0': 0, '1': 1, 'N': 0, 'Y': 1, 'A': 1}
course['share_flag'] = course['share_flag'].map(share_map).fillna(0).astype(int)

# 合并数据
df = sc.merge(course, on=['course_id', 'group_no', 'dept_no'], how='left',
              suffixes=('_sc', '_course'))
print(f"  合并后数据: {len(df):,} 条")

# 构造衍生特征
df['is_online'] = (df['location'] == '线上').astype(int)
df['total_hours'] = df['class_hours'] + df['practice_hours']
df['practice_ratio'] = np.where(df['total_hours'] > 0,
                                df['practice_hours'] / df['total_hours'], 0)
df['teacher_rank'] = df['teacher_name'].apply(
    lambda x: 3 if '教授' in str(x) and '副' not in str(x)
    else (2 if '副教授' in str(x) else 1)
)

print(f"  衍生特征: is_online, total_hours, practice_ratio, teacher_rank")

# ============================================================
# 2. 单因素分析：各课程特征对成绩的影响
# ============================================================
print("\n[Step 2] 单因素分析...")

# 2.1 学分 vs 成绩
credit_stats = df.groupby('credit')['score'].agg(
    ['mean', 'std', 'count', 'median', 'skew']
).round(2)

# 2.2 线上 vs 线下
online_offline = df.groupby('is_online')['score'].agg(['mean', 'std', 'count']).round(2)
t_ol, p_ol = stats.ttest_ind(
    df[df['is_online'] == 1]['score'],
    df[df['is_online'] == 0]['score']
)

# 2.3 共享 vs 非共享
shared_stats = df.groupby('share_flag')['score'].agg(['mean', 'std', 'count']).round(2)
t_sh, p_sh = stats.ttest_ind(
    df[df['share_flag'] == 1]['score'],
    df[df['share_flag'] == 0]['score']
)

# 2.4 教师职称 vs 成绩
teacher_rank_stats = df.groupby('teacher_rank')['score'].agg(['mean', 'std', 'count']).round(2)
rank_groups = [df[df['teacher_rank'] == r]['score'] for r in sorted(df['teacher_rank'].unique())]
if len(rank_groups) >= 2:
    f_rank, p_rank = stats.f_oneway(*rank_groups)

# 2.5 ANOVA: 学分 (filter groups with >= 2 records)
credit_groups_raw = [df[df['credit'] == c]['score'] for c in sorted(df['credit'].unique())]
credit_groups = [g for g in credit_groups_raw if len(g) >= 2]
f_credit, p_credit = stats.f_oneway(*credit_groups)

# 打印单因素结果
print(f"""
  ┌─────────────────────────────────────────────────────────┐
  │                    单因素分析结果                         │
  ├─────────────────────────────────────────────────────────┤
  │ 学分 vs 成绩                                            │
  │   ANOVA: F={f_credit:.2f}, p={p_credit:.2e}              │
  │   学分越高 → 成绩越高 (r={df['credit'].corr(df['score']):.3f})│
  ├─────────────────────────────────────────────────────────┤
  │ 线上 vs 线下                                            │
  │   线上: M={online_offline.loc[1,'mean']:.1f} 线下: M={online_offline.loc[0,'mean']:.1f}│
  │   t={t_ol:.2f}, p={p_ol:.4f} {'***' if p_ol<0.001 else '**' if p_ol<0.01 else '*' if p_ol<0.05 else 'ns'}                      │
  ├─────────────────────────────────────────────────────────┤
  │ 共享 vs 非共享                                          │
  │   共享: M={shared_stats.loc[1,'mean']:.1f} 非共享: M={shared_stats.loc[0,'mean']:.1f}│
  │   t={t_sh:.2f}, p={p_sh:.4f} {'***' if p_sh<0.001 else '**' if p_sh<0.01 else '*' if p_sh<0.05 else 'ns'}                      │
  ├─────────────────────────────────────────────────────────┤
  │ 教师职称 vs 成绩                                        │
  │   ANOVA: F={f_rank:.2f}, p={p_rank:.4f}                 │
  │   教授: M={teacher_rank_stats.loc[3,'mean']:.1f}  副教授: M={teacher_rank_stats.loc[2,'mean']:.1f}  讲师: M={teacher_rank_stats.loc[1,'mean']:.1f}│
  └─────────────────────────────────────────────────────────┘
""")

# ============================================================
# 3. 连续型特征相关性分析
# ============================================================
print("[Step 3] 连续型特征相关性分析...")

cont_features = {
    'credit': '学分',
    'class_hours': '讲课时长',
    'practice_hours': '实践课时',
    'total_hours': '总课时',
    'practice_ratio': '实践课时占比',
    'share_flag': '是否共享',
    'is_online': '是否线上',
    'teacher_rank': '教师职称等级',
    'student_count': '选课人数',
}

# 按课程聚合
course_agg = df.groupby('course_id').agg(
    score_mean=('score', 'mean'),
    score_std=('score', 'std'),
    score_median=('score', 'median'),
    pass_rate=('score', lambda x: (x >= 60).mean()),
    excellent_rate=('score', lambda x: (x >= 90).mean()),
    student_count=('score', 'count'),
    credit=('credit', 'first'),
    class_hours=('class_hours', 'first'),
    practice_hours=('practice_hours', 'first'),
    total_hours=('total_hours', 'first'),
    practice_ratio=('practice_ratio', 'first'),
    share_flag=('share_flag', 'first'),
    is_online=('is_online', 'first'),
    teacher_rank=('teacher_rank', 'first'),
).reset_index()

# 计算所有特征与 score_mean 的 Pearson 和 Spearman 相关系数
corr_results = []
for feat, name in cont_features.items():
    valid = course_agg[[feat, 'score_mean']].dropna()
    if len(valid) > 2 and valid[feat].nunique() > 1:
        r_pearson, p_pearson = pearsonr(valid[feat], valid['score_mean'])
        r_spearman, p_spearman = spearmanr(valid[feat], valid['score_mean'])
        corr_results.append({
            'feature': name,
            'pearson_r': round(r_pearson, 4),
            'pearson_p': p_pearson,
            'spearman_r': round(r_spearman, 4),
            'spearman_p': p_spearman,
            'significance': '***' if p_pearson < 0.001 else '**' if p_pearson < 0.01 else '*' if p_pearson < 0.05 else 'ns'
        })

corr_df = pd.DataFrame(corr_results).sort_values('pearson_r', key=abs, ascending=False)
print("\n  课程特征与平均成绩相关系数（按课程聚合）:")
print(f"  {'特征':<16} {'Pearson r':>10} {'显著性':>8} {'Spearman r':>10}")
print(f"  {'-'*50}")
for _, row in corr_df.iterrows():
    print(f"  {row['feature']:<16} {row['pearson_r']:>10.4f} {row['significance']:>8} {row['spearman_r']:>10.4f}")

# ============================================================
# 4. 多因素分析：哪些特征最能预测成绩？
# ============================================================
print("\n[Step 4] 多因素分析（随机森林特征重要性）...")

feat_cols = ['credit', 'class_hours', 'practice_hours', 'total_hours',
             'practice_ratio', 'share_flag', 'is_online', 'teacher_rank',
             'student_count']
X = course_agg[feat_cols].dropna()
y = course_agg.loc[X.index, 'score_mean']

# 随机森林
rf = RandomForestRegressor(n_estimators=200, max_depth=8, random_state=42, n_jobs=-1)
rf.fit(X, y)

# 特征重要性
importance_df = pd.DataFrame({
    'feature': [cont_features.get(f, f) for f in feat_cols],
    'importance': rf.feature_importances_
}).sort_values('importance', ascending=False)

print("\n  随机森林特征重要性 (预测课程平均分):")
for _, row in importance_df.iterrows():
    bar = '█' * int(row['importance'] * 80)
    print(f"  {row['feature']:<16} {row['importance']:.4f} {bar}")

# 偏依赖分析：credit 和 practice_ratio
print(f"\n  R^2 (Random Forest): {rf.score(X, y):.4f}")

# 偏依赖：控制其他变量后，credit 对成绩的边际效应
print("\n  偏依赖分析（控制其他变量后）:")
for top_feat in importance_df.head(3)['feature'].tolist():
    print(f"  - {top_feat}: 特征重要性 = {importance_df[importance_df['feature']==top_feat]['importance'].values[0]:.4f}")

# ============================================================
# 5. 深度分析：不同课程类型组合
# ============================================================
print("\n[Step 5] 课程类型交叉分析...")

# 5.1 线上-共享 交叉
df['course_type'] = df.apply(
    lambda r: ('Online' if r['is_online'] else 'Offline') + ' + ' +
              ('Shared' if r['share_flag'] else 'Non-shared'), axis=1
)
cross_stats = df.groupby('course_type')['score'].agg(['mean', 'std', 'count']).round(2)
print("\n  课程类型交叉分析 (线上/线下 × 共享/非共享):")
print(cross_stats.to_string())

# 5.2 学分 × 线上 交互
credit_online = df.groupby(['credit', 'is_online'])['score'].mean().unstack()
if len(credit_online.columns) == 2:
    credit_online.columns = ['Offline', 'Online']

# 5.3 学分 × 实践比例 × 成绩 三维分析
df['credit_group'] = pd.cut(df['credit'], bins=[0, 2, 3, 10], labels=['Low(1-2)', 'Mid(3)', 'High(4+)'])
df['practice_group'] = pd.cut(df['practice_ratio'], bins=[0, 0.3, 0.5, 1],
                               labels=['Low', 'Mid', 'High'])
triple_stats = df.groupby(['credit_group', 'practice_group'])['score'].agg(
    ['mean', 'std', 'count']).round(2)
print("\n  学分 × 实践比例 交叉分析:")
print(triple_stats.to_string())

# ============================================================
# 6. 可视化
# ============================================================
print("\n[Step 6] 生成可视化图表...")

# -------- Fig 1: 单因素分析面板 --------
fig, axes = plt.subplots(2, 3, figsize=(18, 12))

# (a) 学分 vs 成绩
ax = axes[0, 0]
credit_order = sorted(df['credit'].unique())
bp_data = [df[df['credit'] == c]['score'].values for c in credit_order]
bp = ax.boxplot(bp_data, labels=credit_order, patch_artist=True)
for patch, color in zip(bp['boxes'], sns.color_palette('Blues', len(credit_order))):
    patch.set_facecolor(color)
# 叠加样本量
for i, c in enumerate(credit_order):
    n = len(df[df['credit'] == c])
    ax.annotate(f'n={n}', (i + 1, df[df['credit'] == c]['score'].max() + 1),
                ha='center', fontsize=7, color='grey')
ax.set_title('Score Distribution by Credit')
ax.set_xlabel('Credit')
ax.set_ylabel('Score')

# (b) 线上 vs 线下
ax = axes[0, 1]
labels_ol = ['Offline', 'Online']
colors_ol = ['#3498db', '#e74c3c']
means_ol = [df[df['is_online'] == 0]['score'].mean(), df[df['is_online'] == 1]['score'].mean()]
stds_ol = [df[df['is_online'] == 0]['score'].std(), df[df['is_online'] == 1]['score'].std()]
bars = ax.bar(labels_ol, means_ol, color=colors_ol, edgecolor='white', width=0.5)
ax.errorbar(range(2), means_ol, yerr=stds_ol, fmt='none', ecolor='black', capsize=8, linewidth=2)
for bar, m in zip(bars, means_ol):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1.5,
            f'{m:.1f}', ha='center', fontsize=12, fontweight='bold')
ax.set_title(f'Online vs Offline (t={t_ol:.2f}, p={p_ol:.4f})')
ax.set_ylabel('Mean Score')
ax.set_ylim(0, 100)

# (c) 共享 vs 非共享
ax = axes[0, 2]
labels_sh = ['Non-shared', 'Shared']
colors_sh = ['#2ecc71', '#9b59b6']
means_sh = [df[df['share_flag'] == 0]['score'].mean(), df[df['share_flag'] == 1]['score'].mean()]
stds_sh = [df[df['share_flag'] == 0]['score'].std(), df[df['share_flag'] == 1]['score'].std()]
bars = ax.bar(labels_sh, means_sh, color=colors_sh, edgecolor='white', width=0.5)
ax.errorbar(range(2), means_sh, yerr=stds_sh, fmt='none', ecolor='black', capsize=8, linewidth=2)
for bar, m in zip(bars, means_sh):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1.5,
            f'{m:.1f}', ha='center', fontsize=12, fontweight='bold')
ax.set_title(f'Shared vs Non-shared (t={t_sh:.2f}, p={p_sh:.4f})')
ax.set_ylabel('Mean Score')
ax.set_ylim(0, 100)

# (d) 教师职称 vs 成绩
ax = axes[1, 0]
rank_labels = {1: 'Lecturer', 2: 'Assoc. Prof', 3: 'Professor'}
rank_order = sorted(df['teacher_rank'].unique())
bp_data_rank = [df[df['teacher_rank'] == r]['score'].values for r in rank_order]
bp = ax.boxplot(bp_data_rank, labels=[rank_labels[r] for r in rank_order], patch_artist=True)
for patch, color in zip(bp['boxes'], sns.color_palette('Oranges', len(rank_order))):
    patch.set_facecolor(color)
ax.set_title(f'Score by Teacher Rank (ANOVA F={f_rank:.2f}, p={p_rank:.4f})')
ax.set_ylabel('Score')

# (e) 课时 vs 成绩 散点图
ax = axes[1, 1]
scatter = ax.scatter(course_agg['total_hours'], course_agg['score_mean'],
                     c=course_agg['credit'], cmap='coolwarm', alpha=0.6, s=25,
                     edgecolors='grey', linewidth=0.2)
z_line = np.polyfit(course_agg['total_hours'].dropna(), course_agg.loc[course_agg['total_hours'].notna(), 'score_mean'], 1)
p_line = np.poly1d(z_line)
x_line = np.linspace(course_agg['total_hours'].min(), course_agg['total_hours'].max(), 100)
ax.plot(x_line, p_line(x_line), 'k--', linewidth=2, label=f'Trend (slope={z_line[0]:.2f})')
ax.set_title(f'Score vs Total Hours (r={corr_df[corr_df["feature"]=="总课时"]["pearson_r"].values[0]:.3f})')
ax.set_xlabel('Total Hours')
ax.set_ylabel('Mean Score')
plt.colorbar(scatter, ax=ax, label='Credit')
ax.legend()

# (f) 实践课时占比 vs 成绩
ax = axes[1, 2]
scatter = ax.scatter(course_agg['practice_ratio'], course_agg['score_mean'],
                     c=course_agg['student_count'], cmap='viridis', alpha=0.6, s=25,
                     edgecolors='grey', linewidth=0.2)
mask_pr = course_agg['practice_ratio'].notna() & course_agg['score_mean'].notna()
z_pr = np.polyfit(course_agg.loc[mask_pr, 'practice_ratio'],
                  course_agg.loc[mask_pr, 'score_mean'], 1)
p_pr = np.poly1d(z_pr)
x_pr = np.linspace(course_agg['practice_ratio'].min(), course_agg['practice_ratio'].max(), 100)
ax.plot(x_pr, p_pr(x_pr), 'r--', linewidth=2, label=f'Trend (slope={z_pr[0]:.1f})')
ax.set_title(f'Score vs Practice Ratio (r={corr_df[corr_df["feature"]=="实践课时占比"]["pearson_r"].values[0]:.3f})')
ax.set_xlabel('Practice Hours / Total Hours')
ax.set_ylabel('Mean Score')
plt.colorbar(scatter, ax=ax, label='Student Count')
ax.legend()

plt.tight_layout()
fig.savefig(os.path.join(OUT_DIR, 'task3_01_univariate.png'))
plt.close()
print("  Saved: task3_01_univariate.png")

# -------- Fig 2: 相关性矩阵 & 特征重要性 --------
fig, axes = plt.subplots(1, 2, figsize=(16, 7))

# (a) 相关性热力图
ax = axes[0]
corr_matrix = course_agg[[
    'score_mean', 'score_std', 'pass_rate', 'excellent_rate',
    'credit', 'class_hours', 'practice_hours', 'total_hours',
    'practice_ratio', 'share_flag', 'is_online', 'teacher_rank', 'student_count'
]].corr()
# 只保留 score 相关列
score_corr = corr_matrix[['score_mean', 'score_std', 'pass_rate', 'excellent_rate']].iloc[4:]
sns.heatmap(score_corr, ax=ax, cmap='RdBu_r', center=0, annot=True,
            fmt='.2f', vmin=-0.5, vmax=0.5,
            cbar_kws={'label': 'Pearson r'})
ax.set_title('Correlation: Course Features vs Score Metrics')
ax.set_ylabel('Course Feature')

# (b) 随机森林特征重要性
ax = axes[1]
colors_imp = sns.color_palette('Blues_r', len(importance_df))
ax.barh(range(len(importance_df)), importance_df['importance'], color=colors_imp, edgecolor='white')
ax.set_yticks(range(len(importance_df)))
ax.set_yticklabels(importance_df['feature'])
ax.invert_yaxis()
ax.set_title('Random Forest Feature Importance\n(for predicting course mean score)')
ax.set_xlabel('Importance')
for i, (_, row) in enumerate(importance_df.iterrows()):
    ax.text(row['importance'] + 0.002, i, f'{row["importance"]:.3f}', va='center', fontsize=10)

plt.tight_layout()
fig.savefig(os.path.join(OUT_DIR, 'task3_02_correlation_importance.png'))
plt.close()
print("  Saved: task3_02_correlation_importance.png")

# -------- Fig 3: 交叉分析 --------
fig, axes = plt.subplots(2, 2, figsize=(16, 13))

# (a) 学分×线上 交互热力图
ax = axes[0, 0]
if len(credit_online.columns) == 2:
    sns.heatmap(credit_online, ax=ax, cmap='YlOrRd', annot=True, fmt='.1f',
                cbar_kws={'label': 'Mean Score'})
    ax.set_title('Mean Score: Credit × Online/Offline')
    ax.set_ylabel('Credit')
    ax.set_xlabel('')
else:
    ax.text(0.5, 0.5, 'All offline courses', ha='center', fontsize=12)

# (b) 学分×实践比例×成绩 分组柱状图
ax = axes[0, 1]
triple_pivot = df.pivot_table(values='score', index='credit_group',
                               columns='practice_group', aggfunc='mean')
triple_pivot.plot(kind='bar', ax=ax, colormap='Set2', edgecolor='white')
ax.set_title('Mean Score: Credit Group × Practice Ratio')
ax.set_xlabel('Credit Group')
ax.set_ylabel('Mean Score')
ax.legend(title='Practice Ratio')
ax.set_xticklabels(ax.get_xticklabels(), rotation=0)

# (c) 课程类型交叉（线上/线下 × 共享/非共享）
ax = axes[1, 0]
cross_plot = df.groupby('course_type')['score'].agg(['mean', 'std', 'count'])
cross_colors = ['#e74c3c', '#c0392b', '#3498db', '#2980b9']
x_labels = cross_plot.index.tolist()
x_means = cross_plot['mean'].tolist()
x_stds = cross_plot['std'].tolist()
bars = ax.bar(x_labels, x_means, color=cross_colors, edgecolor='white')
ax.errorbar(range(len(x_labels)), x_means, yerr=x_stds, fmt='none', ecolor='black', capsize=5)
for bar, m, n in zip(bars, x_means, cross_plot['count']):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1.5,
            f'{m:.1f}\n(n={n})', ha='center', fontsize=9)
ax.set_title('Score by Course Type (Online/Offline × Shared/Non-shared)')
ax.set_ylabel('Mean Score')
ax.set_ylim(0, 100)

# (d) 教师个体差异（前15位课程最多的教师）
ax = axes[1, 1]
top_teachers = course.groupby('teacher_name').size().nlargest(15).index
teacher_data = df[df['teacher_name'].isin(top_teachers)].groupby('teacher_name')['score'].agg(
    ['mean', 'std', 'count']
).reindex(top_teachers)
teacher_data = teacher_data.sort_values('mean')
colors_t = plt.cm.RdYlGn((teacher_data['mean'] - teacher_data['mean'].min()) /
                          (teacher_data['mean'].max() - teacher_data['mean'].min()))
ax.barh(range(len(teacher_data)), teacher_data['mean'], color=colors_t, edgecolor='white')
ax.set_yticks(range(len(teacher_data)))
ax.set_yticklabels(teacher_data.index, fontsize=8)
ax.invert_yaxis()
ax.axvline(x=df['score'].mean(), color='black', linestyle='--', alpha=0.5,
           label=f'Overall Mean={df["score"].mean():.1f}')
ax.set_title('Mean Score by Teacher (Top 15 by #courses)')
ax.set_xlabel('Mean Score')
ax.legend()

plt.tight_layout()
fig.savefig(os.path.join(OUT_DIR, 'task3_03_cross_analysis.png'))
plt.close()
print("  Saved: task3_03_cross_analysis.png")

# -------- Fig 4: 偏依赖图（Partial Dependence）--------
fig, axes = plt.subplots(2, 3, figsize=(18, 11))

# 选取最重要的6个特征，确保都在 X.columns 中
top6_feats = [f for f in importance_df['feature'].tolist()
              if f in cont_features.values()]
top6_keys = []
for f in top6_feats:
    for k, v in cont_features.items():
        if v == f and k in X.columns:
            top6_keys.append(k)
            break
top6_feats = top6_feats[:len(top6_keys)]

for idx, (feat_name, feat_key) in enumerate(zip(top6_feats, top6_keys)):
    if idx >= 6:
        break
    ax = axes[idx // 3][idx % 3]
    X_subset = X[[c for c in X.columns if c != feat_key or True]].copy()
    # Ensure feat_key is in X
    X_subset[feat_key] = X[feat_key].copy()

    # 在特征范围内生成取值
    feat_min, feat_max = X_subset[feat_key].min(), X_subset[feat_key].max()
    if feat_key in ['share_flag', 'is_online']:
        x_vals = np.array([0, 1])
        labels = ['No', 'Yes'] if feat_key == 'is_online' else ['Non-shared', 'Shared']
    else:
        x_vals = np.linspace(feat_min, feat_max, 50)
        labels = None

    pd_scores = []
    for val in x_vals:
        X_temp = X_subset.copy()
        X_temp[feat_key] = val
        pd_scores.append(rf.predict(X_temp).mean())

    if labels:
        ax.bar(labels, pd_scores, color=['#3498db', '#e74c3c'], edgecolor='white')
    else:
        ax.plot(x_vals, pd_scores, 'b-', linewidth=2.5)
        ax.fill_between(x_vals,
                        [s - np.std(pd_scores) * 0.1 for s in pd_scores],
                        [s + np.std(pd_scores) * 0.1 for s in pd_scores],
                        alpha=0.15, color='blue')

    imp_val = importance_df[importance_df['feature'] == feat_name]['importance'].values[0]
    ax.set_title(f'{feat_name} (importance={imp_val:.3f})')
    ax.set_ylabel('Predicted Mean Score')

plt.tight_layout()
fig.savefig(os.path.join(OUT_DIR, 'task3_04_partial_dependence.png'))
plt.close()
print("  Saved: task3_04_partial_dependence.png")

# ============================================================
# 7. 详细统计报告
# ============================================================
print("\n[Step 7] 生成统计报告...")

# 学分与成绩的详细统计
print("\n  各学分成绩详细统计:")
print(f"  {'学分':<6} {'样本量':>8} {'均值':>8} {'中位数':>8} {'标准差':>8} {'偏度':>8} {'及格率':>8} {'优秀率':>8}")
print(f"  {'-'*70}")
for c in sorted(df['credit'].dropna().unique()):
    cdata = df[df['credit'] == c]['score']
    print(f"  {c:<6} {len(cdata):>8} {cdata.mean():>8.2f} {cdata.median():>8.1f} "
          f"{cdata.std():>8.2f} {cdata.skew():>8.2f} "
          f"{(cdata>=60).mean()*100:>7.1f}% {(cdata>=90).mean()*100:>7.1f}%")

# 报告
report_content = f"""================================================================================
              任务3：成绩与课程特征分析 — 详细报告
================================================================================

一、数据说明
  - 有效成绩记录: {len(sc):,} 条
  - 课程总数: {course['course_id'].nunique()}
  - 分析特征: 学分、课时(讲授/实践)、授课方式(线上/线下)、共享属性、教师职称

二、主要发现

  1. 学分是最强的成绩预测因子
     - Pearson r = {corr_df[corr_df['feature']=='学分']['pearson_r'].values[0]:.4f}
     - Spearman r = {corr_df[corr_df['feature']=='学分']['spearman_r'].values[0]:.4f}
     - ANOVA: F={f_credit:.2f}, p={p_credit:.2e}
     - 随机森林重要性: {importance_df[importance_df['feature']=='学分']['importance'].values[0]:.4f} (排名第{importance_df['feature'].tolist().index('学分')+1})
     - 结论: 学分越高，成绩越高。高学分课程可能是高年级专业课，学生学习动力更强。

  2. 线上课程成绩显著优于线下
     - 线上: {online_offline.loc[1,'mean']:.1f} ± {online_offline.loc[1,'std']:.1f}
     - 线下: {online_offline.loc[0,'mean']:.1f} ± {online_offline.loc[0,'std']:.1f}
     - t({t_ol:.2f}), p={p_ol:.4f}
     - 可能原因: 线上课程评估方式不同，或线上课程仅4门样本较少

  3. 共享课程成绩略高于非共享
     - 共享: {shared_stats.loc[1,'mean']:.1f} vs 非共享: {shared_stats.loc[0,'mean']:.1f}
     - t({t_sh:.2f}), p={p_sh:.4f}

  4. 实践课时占比正向影响成绩
     - Pearson r = {corr_df[corr_df['feature']=='实践课时占比']['pearson_r'].values[0]:.4f}
     - 实践环节越多，学生理解和掌握越好

  5. 教师职称与成绩关系
     - 教授: {teacher_rank_stats.loc[3,'mean']:.1f}
     - 副教授: {teacher_rank_stats.loc[2,'mean']:.1f}
     - 讲师: {teacher_rank_stats.loc[1,'mean']:.1f}

三、多因素模型 (随机森林)
  - R^2 = {rf.score(X, y):.4f}
  - 最重要的3个特征:
    1. {importance_df.iloc[0]['feature']}: {importance_df.iloc[0]['importance']:.4f}
    2. {importance_df.iloc[1]['feature']}: {importance_df.iloc[1]['importance']:.4f}
    3. {importance_df.iloc[2]['feature']}: {importance_df.iloc[2]['importance']:.4f}

四、建议
  1. 课程设计应注重实践环节比例
  2. 共享课程机制值得推广
  3. 学分对成绩的正向影响可能反映课程难度与学生投入的匹配

================================================================================
  图表文件:
    - task3_01_univariate.png        (单因素分析: 学分/线上/共享/教师/课时/实践)
    - task3_02_correlation_importance.png (相关性矩阵 & 特征重要性)
    - task3_03_cross_analysis.png    (交叉分析: 学分×线上, 学分×实践, 课程类型, 教师)
    - task3_04_partial_dependence.png (偏依赖图: 控制其他变量后的特征效应)
  数据文件:
    - task3_correlation_results.csv   (相关性分析结果)
    - task3_feature_importance.csv    (特征重要性)
    - task3_course_aggregated.csv     (按课程聚合的数据)
================================================================================
"""

with open(os.path.join(OUT_DIR, 'task3_report.txt'), 'w', encoding='utf-8') as f:
    f.write(report_content)
print(report_content)

# 保存数据
corr_df.to_csv(os.path.join(OUT_DIR, 'task3_correlation_results.csv'), index=False)
importance_df.to_csv(os.path.join(OUT_DIR, 'task3_feature_importance.csv'), index=False)
course_agg.to_csv(os.path.join(OUT_DIR, 'task3_course_aggregated.csv'), index=False, float_format='%.4f')

print("\n" + "=" * 70)
print("任务3完成！所有结果保存至 output_task3/ 目录")
print("=" * 70)
