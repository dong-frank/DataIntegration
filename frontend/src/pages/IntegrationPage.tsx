import { FormEvent, useEffect, useState } from 'react';
import { RefreshCw, Trash2 } from 'lucide-react';
import { api } from '../api/client';
import { DataTable } from '../components/DataTable';
import type { CollegeCode, CourseRecord, StatsSummary } from '../types/domain';

export function IntegrationPage() {
  const [source, setSource] = useState<CollegeCode>('A');
  const [courses, setCourses] = useState<CourseRecord[]>([]);
  const [stats, setStats] = useState<StatsSummary | null>(null);
  const [enrollmentId, setEnrollmentId] = useState('A-E0001');
  const [message, setMessage] = useState('');

  const load = async () => {
    const [nextCourses, nextStats] = await Promise.all([api.sharedCourses(source), api.stats()]);
    setCourses(nextCourses);
    setStats(nextStats);
  };

  useEffect(() => {
    void load();
  }, [source]);

  const withdraw = async (event: FormEvent) => {
    event.preventDefault();
    const result = await api.withdraw(enrollmentId);
    setMessage(result.withdrawn ? `${result.enrollmentId} 已退选` : `${enrollmentId} 未找到`);
    await load();
  };

  return (
    <section className="page-stack">
      <header className="page-header">
        <div>
          <p className="eyebrow">Integration Server</p>
          <h1>集成服务器</h1>
        </div>
        <button className="secondary-button" onClick={load} type="button">
          <RefreshCw size={17} />
          刷新
        </button>
      </header>

      <div className="toolbar">
        <label>
          课程来源
          <select value={source} onChange={(event) => setSource(event.target.value as CollegeCode)}>
            <option value="A">学院A / SQL Server</option>
            <option value="B">学院B / Oracle</option>
            <option value="C">学院C / MySQL</option>
          </select>
        </label>
        <form className="inline-form" onSubmit={withdraw}>
          <label>
            退课记录
            <input value={enrollmentId} onChange={(event) => setEnrollmentId(event.target.value)} />
          </label>
          <button className="danger-button" title="退选课程" type="submit">
            <Trash2 size={17} />
            退选
          </button>
        </form>
      </div>

      {message && <div className="notice">{message}</div>}

      <section className="panel">
        <div className="panel-heading">
          <h2>共享课程</h2>
          <span>{courses.length} 门</span>
        </div>
        <DataTable
          rows={courses}
          emptyText="暂无共享课程"
          columns={[
            { key: 'college', label: '来源', render: (course) => `学院${course.college}` },
            { key: 'id', label: '课程号', render: (course) => course.id },
            { key: 'name', label: '课程名', render: (course) => course.name },
            { key: 'hours', label: '课时', render: (course) => course.hours },
            { key: 'credits', label: '学分', render: (course) => course.credits },
            { key: 'teacher', label: '教师', render: (course) => course.teacher },
            { key: 'location', label: '地点', render: (course) => course.location },
          ]}
        />
      </section>

      {stats && (
        <section className="metric-grid">
          <div className="metric-panel">
            <span>总学生</span>
            <strong>{stats.totalStudents}</strong>
          </div>
          <div className="metric-panel">
            <span>总课程</span>
            <strong>{stats.totalCourses}</strong>
          </div>
          <div className="metric-panel">
            <span>总选课</span>
            <strong>{stats.totalEnrollments}</strong>
          </div>
        </section>
      )}
    </section>
  );
}
