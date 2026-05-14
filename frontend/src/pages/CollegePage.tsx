import { useEffect, useMemo, useState } from 'react';
import { RefreshCw } from 'lucide-react';
import { useParams } from 'react-router-dom';
import { api } from '../api/client';
import { DataTable } from '../components/DataTable';
import type { CollegeCode, CourseRecord, EnrollmentRecord, LoginResponse, StudentRecord } from '../types/domain';

interface CollegePageProps {
  session: LoginResponse;
}

const dbmsByCollege: Record<CollegeCode, string> = {
  A: 'SQL Server',
  B: 'Oracle',
  C: 'MySQL',
};

export function CollegePage({ session }: CollegePageProps) {
  const params = useParams();
  const college = (params.college ?? session.college ?? 'A') as CollegeCode;
  const [students, setStudents] = useState<StudentRecord[]>([]);
  const [courses, setCourses] = useState<CourseRecord[]>([]);
  const [enrollments, setEnrollments] = useState<EnrollmentRecord[]>([]);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    const [nextStudents, nextCourses, nextEnrollments] = await Promise.all([
      api.students(college),
      api.courses(college),
      api.enrollments(college),
    ]);
    setStudents(nextStudents);
    setCourses(nextCourses);
    setEnrollments(nextEnrollments);
    setLoading(false);
  };

  useEffect(() => {
    void load();
  }, [college]);

  const visibleEnrollments = useMemo(() => enrollments.slice(0, 8), [enrollments]);

  return (
    <section className="page-stack">
      <header className="page-header">
        <div>
          <p className="eyebrow">College {college}</p>
          <h1>学院{college} 教务系统</h1>
        </div>
        <button className="secondary-button" onClick={load} type="button">
          <RefreshCw size={17} />
          刷新
        </button>
      </header>

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
          <span>选课</span>
          <strong>{enrollments.length}</strong>
        </div>
        <div className="metric-panel">
          <span>DBMS</span>
          <strong>{dbmsByCollege[college]}</strong>
        </div>
      </div>

      <section className="panel">
        <div className="panel-heading">
          <h2>课程信息</h2>
          <span>{loading ? '加载中' : `${courses.filter((course) => course.shared).length} 门共享`}</span>
        </div>
        <DataTable
          rows={courses}
          emptyText="暂无课程"
          columns={[
            { key: 'id', label: '课程号', render: (course) => course.id },
            { key: 'name', label: '课程名', render: (course) => course.name },
            { key: 'credits', label: '学分', render: (course) => course.credits },
            { key: 'teacher', label: '教师', render: (course) => course.teacher },
            { key: 'shared', label: '共享', render: (course) => (course.shared ? '是' : '否') },
          ]}
        />
      </section>

      <section className="split-grid">
        <div className="panel">
          <div className="panel-heading">
            <h2>学生样例</h2>
            <span>前 8 条</span>
          </div>
          <DataTable
            rows={students.slice(0, 8)}
            emptyText="暂无学生"
            columns={[
              { key: 'id', label: '学号', render: (student) => student.id },
              { key: 'name', label: '姓名', render: (student) => student.name },
              { key: 'major', label: '专业', render: (student) => student.major },
            ]}
          />
        </div>
        <div className="panel">
          <div className="panel-heading">
            <h2>选课样例</h2>
            <span>前 8 条</span>
          </div>
          <DataTable
            rows={visibleEnrollments}
            emptyText="暂无选课"
            columns={[
              { key: 'id', label: '记录号', render: (enrollment) => enrollment.id },
              { key: 'studentId', label: '学生', render: (enrollment) => enrollment.studentId },
              { key: 'courseId', label: '课程', render: (enrollment) => enrollment.courseId },
              { key: 'status', label: '状态', render: (enrollment) => enrollment.status },
            ]}
          />
        </div>
      </section>
    </section>
  );
}
