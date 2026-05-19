import { FormEvent, useCallback, useEffect, useMemo, useState } from 'react';
import { Plus, RefreshCw, Trash2 } from 'lucide-react';
import { api } from '../api/client';
import { DataTable } from '../components/DataTable';
import type { CollegeCode, CourseRecord, EnrollmentCreatePayload, StatsSummary } from '../types/domain';

const collegeOptions: Array<{ code: CollegeCode; label: string; dbms: string }> = [
  { code: 'A', label: '学院A', dbms: 'SQL Server' },
  { code: 'B', label: '学院B', dbms: 'Oracle' },
  { code: 'C', label: '学院C', dbms: 'MySQL' },
];

const defaultEnrollForm: EnrollmentCreatePayload = {
  studentCollege: 'B',
  studentId: 'B-S001',
  courseCollege: 'A',
  courseId: 'A-C001',
};

export function IntegrationPage() {
  const [source, setSource] = useState<CollegeCode>('A');
  const [courses, setCourses] = useState<CourseRecord[]>([]);
  const [stats, setStats] = useState<StatsSummary | null>(null);
  const [enrollmentId, setEnrollmentId] = useState('A-E0001');
  const [enrollForm, setEnrollForm] = useState<EnrollmentCreatePayload>(defaultEnrollForm);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const [nextCourses, nextStats] = await Promise.all([api.sharedCourses(source), api.stats()]);
      setCourses(nextCourses);
      setStats(nextStats);
    } catch (err) {
      setError(err instanceof Error ? err.message : '集成数据加载失败');
    } finally {
      setLoading(false);
    }
  }, [source]);

  useEffect(() => {
    void load();
  }, [load]);

  useEffect(() => {
    setEnrollForm((form) => {
      const stillVisible = courses.some((course) => course.college === form.courseCollege && course.id === form.courseId);
      if (stillVisible || courses.length === 0) {
        return form;
      }

      const firstCourse = courses[0];
      return {
        ...form,
        courseCollege: firstCourse.college,
        courseId: firstCourse.id,
      };
    });
  }, [courses]);

  const selectedCourse = useMemo(
    () => courses.find((course) => course.college === enrollForm.courseCollege && course.id === enrollForm.courseId),
    [courses, enrollForm.courseCollege, enrollForm.courseId],
  );

  const updateEnrollForm = <K extends keyof EnrollmentCreatePayload>(key: K, value: EnrollmentCreatePayload[K]) => {
    setEnrollForm((form) => ({
      ...form,
      [key]: value,
    }));
  };

  const selectCourse = (course: CourseRecord) => {
    setEnrollForm((form) => ({
      ...form,
      courseCollege: course.college,
      courseId: course.id,
    }));
  };

  const enroll = async (event: FormEvent) => {
    event.preventDefault();
    setSubmitting(true);
    setError('');
    setMessage('');
    try {
      const record = await api.enroll({
        ...enrollForm,
        studentId: enrollForm.studentId.trim(),
        courseId: enrollForm.courseId.trim(),
      });
      setMessage(`已创建选课记录 ${record.id}`);
      setEnrollmentId(record.id);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : '跨学院选课失败');
    } finally {
      setSubmitting(false);
    }
  };

  const withdraw = async (event: FormEvent) => {
    event.preventDefault();
    setSubmitting(true);
    setError('');
    setMessage('');
    try {
      const result = await api.withdraw(enrollmentId.trim());
      setMessage(result.withdrawn ? `${result.enrollmentId} 已退选` : `${enrollmentId} 未找到`);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : '退课失败');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <section className="page-stack">
      <header className="page-header">
        <div>
          <p className="eyebrow">Integration Server</p>
          <h1>集成服务器</h1>
        </div>
        <button className="secondary-button" disabled={loading} onClick={load} type="button">
          <RefreshCw size={17} />
          {loading ? '刷新中' : '刷新'}
        </button>
      </header>

      {error && <div className="form-error">{error}</div>}
      {message && <div className="notice">{message}</div>}

      <section className="toolbar">
        <label>
          共享课程来源
          <select value={source} onChange={(event) => setSource(event.target.value as CollegeCode)}>
            {collegeOptions.map((college) => (
              <option key={college.code} value={college.code}>
                {college.label} / {college.dbms}
              </option>
            ))}
          </select>
        </label>
        {stats && (
          <div className="toolbar-summary">
            <span>{stats.totalStudents} 名学生</span>
            <span>{stats.totalCourses} 门课程</span>
            <span>{stats.totalEnrollments} 条选课</span>
          </div>
        )}
      </section>

      <section className="split-grid">
        <div className="panel">
          <div className="panel-heading">
            <h2>跨学院选课</h2>
            <span>{selectedCourse ? selectedCourse.name : '选择共享课程'}</span>
          </div>
          <form className="form-grid" onSubmit={enroll}>
            <label>
              学生学院
              <select
                value={enrollForm.studentCollege}
                onChange={(event) => updateEnrollForm('studentCollege', event.target.value as CollegeCode)}
              >
                {collegeOptions.map((college) => (
                  <option key={college.code} value={college.code}>
                    {college.label}
                  </option>
                ))}
              </select>
            </label>
            <label>
              学号
              <input
                value={enrollForm.studentId}
                onChange={(event) => updateEnrollForm('studentId', event.target.value)}
                placeholder="B-S001"
              />
            </label>
            <label>
              课程学院
              <select
                value={enrollForm.courseCollege}
                onChange={(event) => updateEnrollForm('courseCollege', event.target.value as CollegeCode)}
              >
                {collegeOptions.map((college) => (
                  <option key={college.code} value={college.code}>
                    {college.label}
                  </option>
                ))}
              </select>
            </label>
            <label>
              课程号
              <input
                value={enrollForm.courseId}
                onChange={(event) => updateEnrollForm('courseId', event.target.value)}
                placeholder="A-C001"
              />
            </label>
            <button className="primary-button form-action" disabled={submitting} type="submit">
              <Plus size={17} />
              创建选课
            </button>
          </form>
        </div>

        <div className="panel">
          <div className="panel-heading">
            <h2>退课处理</h2>
            <span>按选课记录号</span>
          </div>
          <form className="inline-form" onSubmit={withdraw}>
            <label>
              退课记录
              <input value={enrollmentId} onChange={(event) => setEnrollmentId(event.target.value)} />
            </label>
            <button className="danger-button" disabled={submitting} title="退选课程" type="submit">
              <Trash2 size={17} />
              退选
            </button>
          </form>
        </div>
      </section>

      <section className="panel">
        <div className="panel-heading">
          <h2>共享课程</h2>
          <span>{loading ? '加载中' : `${courses.length} 门`}</span>
        </div>
        <DataTable
          rows={courses}
          emptyText={loading ? '正在加载共享课程' : '暂无共享课程'}
          columns={[
            { key: 'college', label: '来源', render: (course) => `学院${course.college}` },
            { key: 'id', label: '课程号', render: (course) => course.id },
            { key: 'name', label: '课程名', render: (course) => course.name },
            { key: 'hours', label: '课时', render: (course) => course.hours },
            { key: 'credits', label: '学分', render: (course) => course.credits },
            { key: 'teacher', label: '教师', render: (course) => course.teacher },
            { key: 'location', label: '地点', render: (course) => course.location },
            {
              key: 'action',
              label: '操作',
              render: (course) => (
                <button className="table-action" onClick={() => selectCourse(course)} type="button">
                  选择
                </button>
              ),
            },
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
          <div className="metric-panel">
            <span>重叠课程</span>
            <strong>{stats.overlappingCourses.length}</strong>
          </div>
        </section>
      )}
    </section>
  );
}
