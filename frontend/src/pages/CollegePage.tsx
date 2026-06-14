import { useCallback, useEffect, useMemo, useState } from 'react';
import { RefreshCw } from 'lucide-react';
import { Navigate, useParams } from 'react-router-dom';
import { api } from '../api/client';
import { DataTable } from '../components/DataTable';
import type { CollegeCode, CourseRecord, EnrollmentRecord, LoginResponse, StudentRecord } from '../types/domain';
import { collegeLabel, displayCollegeText } from '../utils/collegeLabels';

interface CollegePageProps {
  session: LoginResponse;
}

const dbmsByCollege: Record<CollegeCode, string> = {
  A: 'SQL Server',
  B: 'Oracle',
  C: 'MySQL',
};

const colleges: CollegeCode[] = ['A', 'B', 'C'];

const statusLabels: Record<string, string> = {
  ACTIVE: '有效',
  WITHDRAWN: '已退选',
};

function isCollegeCode(value: string | undefined): value is CollegeCode {
  return colleges.includes(value as CollegeCode);
}

function statusLabel(status: string): string {
  return statusLabels[status] ?? status;
}

export function CollegePage({ session }: CollegePageProps) {
  const params = useParams();
  const college = isCollegeCode(params.college) ? params.college : session.college ?? 'A';
  const collegeName = collegeLabel(college);
  const canView = session.role === 'INTEGRATION_ADMIN' || college === session.college;
  const [students, setStudents] = useState<StudentRecord[]>([]);
  const [courses, setCourses] = useState<CourseRecord[]>([]);
  const [enrollments, setEnrollments] = useState<EnrollmentRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const load = useCallback(async () => {
    if (!canView) {
      return;
    }

    setLoading(true);
    setError('');
    try {
      const [nextStudents, nextCourses, nextEnrollments] = await Promise.all([
        api.students(college),
        api.courses(college),
        api.enrollments(college),
      ]);
      setStudents(nextStudents);
      setCourses(nextCourses);
      setEnrollments(nextEnrollments);
    } catch (err) {
      setError(err instanceof Error ? err.message : '学院数据加载失败');
    } finally {
      setLoading(false);
    }
  }, [canView, college]);

  useEffect(() => {
    void load();
  }, [load]);

  const activeEnrollments = useMemo(
    () => enrollments.filter((enrollment) => enrollment.status === 'ACTIVE').length,
    [enrollments],
  );

  if (!canView) {
    return <Navigate to={session.college ? `/college/${session.college}` : '/integration'} replace />;
  }

  return (
    <section className="page-stack">
      <header className="page-header">
        <div>
          <p className="eyebrow">College {college}</p>
          <h1>{collegeName}教务系统</h1>
        </div>
        <button className="secondary-button" disabled={loading} onClick={load} type="button">
          <RefreshCw size={17} />
          {loading ? '刷新中' : '刷新'}
        </button>
      </header>

      {error && <div className="form-error">{error}</div>}

      <div className="metric-grid">
        <div className="metric-panel">
          <span>学生</span>
          <strong>{students.length}</strong>
        </div>
        <div className="metric-panel">
          <span>课程</span>
          <strong>{courses.length}</strong>
        </div>
        <div className="metric-panel">
          <span>有效选课</span>
          <strong>{activeEnrollments}</strong>
        </div>
        <div className="metric-panel">
          <span>DBMS</span>
          <strong>{dbmsByCollege[college]}</strong>
        </div>
      </div>

      <section className="panel">
        <div className="panel-heading">
          <h2>课程信息</h2>
          <span>{loading ? '加载中' : `${courses.filter((course) => course.shared).length} 门可跨院选修`}</span>
        </div>
        <DataTable
          rows={courses}
          emptyText={loading ? '正在加载课程' : '暂无课程'}
          columns={[
            { key: 'id', label: '课程号', render: (course) => course.id },
            { key: 'name', label: '课程名', render: (course) => course.name },
            { key: 'hours', label: '课时', render: (course) => course.hours },
            { key: 'credits', label: '学分', render: (course) => course.credits },
            { key: 'teacher', label: '教师', render: (course) => course.teacher },
            { key: 'location', label: '地点', render: (course) => course.location },
            {
              key: 'shared',
              label: '可跨院选修',
              render: (course) => (
                <span className={course.shared ? 'status-badge status-active' : 'status-badge'}>
                  {course.shared ? '是' : '否'}
                </span>
              ),
            },
          ]}
        />
      </section>

      <section className="split-grid">
        <div className="panel">
          <div className="panel-heading">
            <h2>学生信息</h2>
            <span>{loading ? '加载中' : `${students.length} 条`}</span>
          </div>
          <div className="scroll-table">
            <DataTable
              rows={students}
              emptyText={loading ? '正在加载学生' : '暂无学生'}
              columns={[
                { key: 'id', label: '学号', render: (student) => student.id },
                { key: 'name', label: '姓名', render: (student) => student.name },
                { key: 'gender', label: '性别', render: (student) => student.gender },
                { key: 'major', label: '专业', render: (student) => displayCollegeText(student.major) },
                { key: 'grade', label: '年级', render: (student) => student.grade },
              ]}
            />
          </div>
        </div>
        <div className="panel">
          <div className="panel-heading">
            <h2>选课信息</h2>
            <span>{loading ? '加载中' : `${enrollments.length} 条`}</span>
          </div>
          <div className="scroll-table">
            <DataTable
              rows={enrollments}
              emptyText={loading ? '正在加载选课' : '暂无选课'}
              columns={[
                { key: 'id', label: '记录号', render: (enrollment) => enrollment.id },
                { key: 'studentCollege', label: '学生学院', render: (enrollment) => collegeLabel(enrollment.studentCollege) },
                { key: 'studentId', label: '学生', render: (enrollment) => enrollment.studentId },
                { key: 'courseId', label: '课程', render: (enrollment) => enrollment.courseId },
                { key: 'score', label: '成绩', render: (enrollment) => enrollment.score },
                {
                  key: 'status',
                  label: '状态',
                  render: (enrollment) => (
                    <span className={`status-badge status-${enrollment.status.toLowerCase()}`}>
                      {statusLabel(enrollment.status)}
                    </span>
                  ),
                },
              ]}
            />
          </div>
        </div>
      </section>
    </section>
  );
}
