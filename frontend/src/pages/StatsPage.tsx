import { useCallback, useEffect, useState } from 'react';
import { RefreshCw } from 'lucide-react';
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { api } from '../api/client';
import type { StatsSummary } from '../types/domain';
import { collegeLabel } from '../utils/collegeLabels';

export function StatsPage() {
  const [stats, setStats] = useState<StatsSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const load = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      setStats(await api.stats());
    } catch (err) {
      setError(err instanceof Error ? err.message : '统计数据加载失败');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const collegeStats =
    stats?.colleges.map((college) => ({
      ...college,
      displayName: collegeLabel(college.college),
    })) ?? [];

  if (loading && !stats) {
    return <div className="empty-state">统计数据加载中</div>;
  }

  return (
    <section className="page-stack">
      <header className="page-header">
        <div>
          <p className="eyebrow">Statistics</p>
          <h1>统计可视化</h1>
        </div>
        <button className="secondary-button" disabled={loading} onClick={load} type="button">
          <RefreshCw size={17} />
          {loading ? '刷新中' : '刷新'}
        </button>
      </header>

      {error && <div className="form-error">{error}</div>}

      {stats && (
        <div className="metric-grid">
          <div className="metric-panel">
            <span>学生总数</span>
            <strong>{stats.totalStudents}</strong>
          </div>
          <div className="metric-panel">
            <span>课程总数</span>
            <strong>{stats.totalCourses}</strong>
          </div>
          <div className="metric-panel">
            <span>选课总数</span>
            <strong>{stats.totalEnrollments}</strong>
          </div>
          <div className="metric-panel">
            <span>重叠课程</span>
            <strong>{stats.overlappingCourses.length}</strong>
          </div>
        </div>
      )}

      {stats && (
        <>
          <section className="panel chart-panel">
            <div className="panel-heading">
              <h2>学院数据规模</h2>
              <span>学生 / 课程 / 选课</span>
            </div>
            <ResponsiveContainer width="100%" height={320}>
              <BarChart data={collegeStats}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="displayName" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="studentCount" name="学生" fill="#2563eb" radius={[4, 4, 0, 0]} />
                <Bar dataKey="courseCount" name="课程" fill="#059669" radius={[4, 4, 0, 0]} />
                <Bar dataKey="enrollmentCount" name="选课" fill="#d97706" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </section>

          <section className="panel">
            <div className="panel-heading">
              <h2>学院明细</h2>
              <span>{collegeStats.length} 个学院</span>
            </div>
            <div className="college-stat-list">
              {collegeStats.map((college) => (
                <div className="college-stat-row" key={college.college}>
                  <strong>{college.displayName}</strong>
                  <span>{college.dbms}</span>
                  <span>{college.studentCount} 学生</span>
                  <span>{college.courseCount} 课程</span>
                  <span>{college.enrollmentCount} 选课</span>
                </div>
              ))}
            </div>
          </section>

          <section className="panel">
            <div className="panel-heading">
              <h2>课程重叠</h2>
              <span>{stats.overlappingCourses.length} 项</span>
            </div>
            <div className="overlap-list">
              {stats.overlappingCourses.map((course) => (
                <span key={course.courseName}>
                  {course.courseName} · {course.collegeCount} 院
                </span>
              ))}
            </div>
          </section>
        </>
      )}
    </section>
  );
}
