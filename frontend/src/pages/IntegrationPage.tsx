import { FormEvent, useCallback, useEffect, useMemo, useState } from 'react';
import { Plus, RefreshCw, Trash2 } from 'lucide-react';
import { api } from '../api/client';
import { DataTable } from '../components/DataTable';
import type {
  CollegeCode,
  CourseRecord,
  EnrollmentCreatePayload,
  EnrollmentRecord,
  StatsSummary,
  StudentRecord,
} from '../types/domain';

const collegeOptions: Array<{ code: CollegeCode; label: string; dbms: string }> = [
  { code: 'A', label: '学院A', dbms: 'SQL Server' },
  { code: 'B', label: '学院B', dbms: 'Oracle' },
  { code: 'C', label: '学院C', dbms: 'MySQL' },
];

const defaultEnrollForm: EnrollmentCreatePayload = {
  studentCollege: 'A',
  studentId: '202300000001',
  courseCollege: 'B',
  courseId: 'B0001',
};

export function IntegrationPage() {
  const [source, setSource] = useState<CollegeCode>('B');
  const [courses, setCourses] = useState<CourseRecord[]>([]);
  const [students, setStudents] = useState<StudentRecord[]>([]);
  const [withdrawCollege, setWithdrawCollege] = useState<CollegeCode>('B');
  const [withdrawEnrollments, setWithdrawEnrollments] = useState<EnrollmentRecord[]>([]);
  const [withdrawStudents, setWithdrawStudents] = useState<StudentRecord[]>([]);
  const [withdrawCourses, setWithdrawCourses] = useState<CourseRecord[]>([]);
  const [stats, setStats] = useState<StatsSummary | null>(null);
  const [enrollmentId, setEnrollmentId] = useState('B0001-202200001');
  const [enrollForm, setEnrollForm] = useState<EnrollmentCreatePayload>(defaultEnrollForm);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const [loadingStudents, setLoadingStudents] = useState(true);
  const [loadingWithdrawEnrollments, setLoadingWithdrawEnrollments] = useState(true);
  const [loadingWithdrawDetails, setLoadingWithdrawDetails] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const [nextCourses, nextStats] = await Promise.all([
        api.sharedCourses(source),
        api.stats(),
      ]);
      setCourses(nextCourses);
      setStats(nextStats);
    } catch (err) {
      setError(err instanceof Error ? err.message : '集成数据加载失败');
    } finally {
      setLoading(false);
    }
  }, [source]);

  const loadStudents = useCallback(async () => {
    setLoadingStudents(true);
    setError('');
    try {
      const nextStudents = await api.students(enrollForm.studentCollege);
      setStudents(nextStudents);
    } catch (err) {
      setStudents([]);
      setError(err instanceof Error ? err.message : '学生列表加载失败');
    } finally {
      setLoadingStudents(false);
    }
  }, [enrollForm.studentCollege]);

  const loadWithdrawEnrollments = useCallback(async () => {
    setLoadingWithdrawEnrollments(true);
    setError('');
    try {
      const nextEnrollments = await api.enrollments(withdrawCollege);
      setWithdrawEnrollments(nextEnrollments);
    } catch (err) {
      setWithdrawEnrollments([]);
      setError(err instanceof Error ? err.message : '退选记录加载失败');
    } finally {
      setLoadingWithdrawEnrollments(false);
    }
  }, [withdrawCollege]);

  useEffect(() => {
    void load();
  }, [load]);

  useEffect(() => {
    void loadStudents();
  }, [loadStudents]);

  useEffect(() => {
    void loadWithdrawEnrollments();
  }, [loadWithdrawEnrollments]);

  useEffect(() => {
    setEnrollForm((form) => {
      const stillVisible = students.some((student) => student.college === form.studentCollege && student.id === form.studentId);
      if (stillVisible || students.length === 0) {
        return form;
      }

      const firstStudent = students[0];
      return {
        ...form,
        studentCollege: firstStudent.college,
        studentId: firstStudent.id,
      };
    });
  }, [students]);

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

  const withdrawEnrollmentOptions = useMemo(
    () => withdrawEnrollments.filter((record) => record.status !== 'WITHDRAWN'),
    [withdrawEnrollments],
  );
  const selectedWithdrawal = useMemo(
    () => withdrawEnrollments.find((record) => record.id === enrollmentId),
    [withdrawEnrollments, enrollmentId],
  );
  const selectedStudent = useMemo(
    () => students.find((student) => student.college === enrollForm.studentCollege && student.id === enrollForm.studentId),
    [students, enrollForm.studentCollege, enrollForm.studentId],
  );
  const selectedCourse = useMemo(
    () => courses.find((course) => course.college === enrollForm.courseCollege && course.id === enrollForm.courseId),
    [courses, enrollForm.courseCollege, enrollForm.courseId],
  );
  const enrollmentXml = useMemo(() => toEnrollmentXml(enrollForm), [enrollForm]);
  const withdrawalXml = useMemo(() => toWithdrawalXml(enrollmentId), [enrollmentId]);
  const selectedWithdrawalStudentCollege = selectedWithdrawal?.studentCollege;
  const selectedWithdrawalStudentId = selectedWithdrawal?.studentId;
  const selectedWithdrawalCourseCollege = selectedWithdrawal?.courseCollege;
  const selectedWithdrawalCourseId = selectedWithdrawal?.courseId;
  const selectedWithdrawalStudent = useMemo(
    () =>
      withdrawStudents.find(
        (student) => student.college === selectedWithdrawalStudentCollege && student.id === selectedWithdrawalStudentId,
      ),
    [withdrawStudents, selectedWithdrawalStudentCollege, selectedWithdrawalStudentId],
  );
  const selectedWithdrawalCourse = useMemo(
    () =>
      withdrawCourses.find(
        (course) => course.college === selectedWithdrawalCourseCollege && course.id === selectedWithdrawalCourseId,
      ),
    [withdrawCourses, selectedWithdrawalCourseCollege, selectedWithdrawalCourseId],
  );

  useEffect(() => {
    const stillVisible = withdrawEnrollmentOptions.some((record) => record.id === enrollmentId);
    if (stillVisible || withdrawEnrollmentOptions.length === 0) {
      return;
    }

    setEnrollmentId(withdrawEnrollmentOptions[0].id);
  }, [withdrawEnrollmentOptions, enrollmentId]);

  useEffect(() => {
    if (!selectedWithdrawalStudentCollege || !selectedWithdrawalCourseCollege) {
      setWithdrawStudents([]);
      setWithdrawCourses([]);
      return;
    }

    const loadWithdrawalDetails = async () => {
      setLoadingWithdrawDetails(true);
      try {
        const [nextStudents, nextCourses] = await Promise.all([
          api.students(selectedWithdrawalStudentCollege),
          api.courses(selectedWithdrawalCourseCollege),
        ]);
        setWithdrawStudents(nextStudents);
        setWithdrawCourses(nextCourses);
      } catch (err) {
        setWithdrawStudents([]);
        setWithdrawCourses([]);
        setError(err instanceof Error ? err.message : '退选明细加载失败');
      } finally {
        setLoadingWithdrawDetails(false);
      }
    };

    void loadWithdrawalDetails();
  }, [selectedWithdrawalStudentCollege, selectedWithdrawalCourseCollege]);

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
      const records = await api.enrollXml(enrollmentXml);
      const firstRecord = records[0];
      setMessage(firstRecord ? `已通过 XML 创建选课记录 ${firstRecord.id}` : 'XML 请求未创建选课记录');
      if (firstRecord) {
        setEnrollmentId(firstRecord.id);
        setWithdrawCollege(firstRecord.courseCollege);
      }
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'XML 跨学院选课失败');
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
      const results = await api.withdrawXml(withdrawalXml);
      const firstResult = results[0];
      setMessage(
        firstResult?.withdrawn
          ? `${firstResult.enrollmentId} 已通过 XML 完成退选`
          : `${enrollmentId} 未找到`,
      );
      await Promise.all([load(), loadWithdrawEnrollments()]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'XML 退课失败');
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
            <span>
              {selectedStudent && selectedCourse ? `${selectedStudent.name} / ${selectedCourse.name}` : '选择学生和课程'}
            </span>
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
              <select
                value={enrollForm.studentId}
                disabled={loadingStudents || students.length === 0}
                onChange={(event) => updateEnrollForm('studentId', event.target.value)}
              >
                {students.length === 0 ? (
                  <option value={enrollForm.studentId}>{loadingStudents ? '加载学生中' : '暂无学生'}</option>
                ) : (
                  students.map((student) => (
                    <option key={student.id} value={student.id}>
                      {student.id} / {student.name}
                    </option>
                  ))
                )}
              </select>
            </label>
            <label>
              课程学院
              <select
                value={enrollForm.courseCollege}
                onChange={(event) => {
                  const nextCollege = event.target.value as CollegeCode;
                  setSource(nextCollege);
                  updateEnrollForm('courseCollege', nextCollege);
                }}
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
              <select
                value={enrollForm.courseId}
                disabled={loading || courses.length === 0}
                onChange={(event) => updateEnrollForm('courseId', event.target.value)}
              >
                {courses.length === 0 ? (
                  <option value={enrollForm.courseId}>{loading ? '加载课程中' : '暂无共享课程'}</option>
                ) : (
                  courses.map((course) => (
                    <option key={course.id} value={course.id}>
                      {course.id} / {course.name}
                    </option>
                  ))
                )}
              </select>
            </label>
            <button className="primary-button form-action" disabled={submitting} type="submit">
              <Plus size={17} />
              创建选课
            </button>
          </form>
          <div className="selection-details">
            <section className="selection-detail-section">
              <div className="detail-heading">
                <span>学生信息</span>
                <strong>{selectedStudent?.name ?? '未选择学生'}</strong>
              </div>
              <dl className="detail-grid">
                <div>
                  <dt>学院</dt>
                  <dd>{collegeLabel(selectedStudent?.college ?? enrollForm.studentCollege)}</dd>
                </div>
                <div>
                  <dt>学号</dt>
                  <dd>{selectedStudent?.id ?? enrollForm.studentId}</dd>
                </div>
                <div>
                  <dt>性别</dt>
                  <dd>{selectedStudent?.gender ?? '暂无'}</dd>
                </div>
                <div>
                  <dt>专业</dt>
                  <dd>{selectedStudent?.major ?? '暂无'}</dd>
                </div>
                <div>
                  <dt>年级</dt>
                  <dd>{selectedStudent ? `${selectedStudent.grade}级` : '暂无'}</dd>
                </div>
              </dl>
            </section>
            <section className="selection-detail-section">
              <div className="detail-heading">
                <span>课程信息</span>
                <strong>{selectedCourse?.name ?? '未选择课程'}</strong>
              </div>
              <dl className="detail-grid">
                <div>
                  <dt>学院</dt>
                  <dd>{collegeLabel(selectedCourse?.college ?? enrollForm.courseCollege)}</dd>
                </div>
                <div>
                  <dt>课程号</dt>
                  <dd>{selectedCourse?.id ?? enrollForm.courseId}</dd>
                </div>
                <div>
                  <dt>课时</dt>
                  <dd>{selectedCourse?.hours ?? '暂无'}</dd>
                </div>
                <div>
                  <dt>学分</dt>
                  <dd>{selectedCourse?.credits ?? '暂无'}</dd>
                </div>
                <div>
                  <dt>老师</dt>
                  <dd>{selectedCourse?.teacher ?? '暂无'}</dd>
                </div>
                <div>
                  <dt>地点</dt>
                  <dd>{selectedCourse?.location ?? '暂无'}</dd>
                </div>
              </dl>
            </section>
          </div>
        </div>

        <div className="panel">
          <div className="panel-heading">
            <h2>退课处理</h2>
            <span>{selectedWithdrawal ? statusLabel(selectedWithdrawal.status) : '选择选课记录'}</span>
          </div>
          <form className="form-grid" onSubmit={withdraw}>
            <label>
              记录学院
              <select value={withdrawCollege} onChange={(event) => setWithdrawCollege(event.target.value as CollegeCode)}>
                {collegeOptions.map((college) => (
                  <option key={college.code} value={college.code}>
                    {college.label}
                  </option>
                ))}
              </select>
            </label>
            <label>
              选课记录号
              <select
                value={enrollmentId}
                disabled={loadingWithdrawEnrollments || withdrawEnrollmentOptions.length === 0}
                onChange={(event) => setEnrollmentId(event.target.value)}
              >
                {withdrawEnrollmentOptions.length === 0 ? (
                  <option value={enrollmentId}>
                    {loadingWithdrawEnrollments ? '加载选课记录中' : '暂无可退选记录'}
                  </option>
                ) : (
                  withdrawEnrollmentOptions.map((record) => (
                    <option key={record.id} value={record.id}>
                      {record.id} / {record.studentId} / {record.courseId}
                    </option>
                  ))
                )}
              </select>
            </label>
            <button
              className="danger-button form-action"
              disabled={submitting || !selectedWithdrawal}
              title="退选课程"
              type="submit"
            >
              <Trash2 size={17} />
              退选
            </button>
          </form>
          <div className="selection-details">
            <section className="selection-detail-section">
              <div className="detail-heading">
                <span>选课信息</span>
                <strong>{selectedWithdrawal?.id ?? '未选择记录'}</strong>
              </div>
              <dl className="detail-grid">
                <div>
                  <dt>状态</dt>
                  <dd>{selectedWithdrawal ? statusLabel(selectedWithdrawal.status) : '暂无'}</dd>
                </div>
                <div>
                  <dt>成绩</dt>
                  <dd>{selectedWithdrawal?.score || '暂无'}</dd>
                </div>
                <div>
                  <dt>学生学院</dt>
                  <dd>{selectedWithdrawal ? collegeLabel(selectedWithdrawal.studentCollege) : '暂无'}</dd>
                </div>
                <div>
                  <dt>课程学院</dt>
                  <dd>{selectedWithdrawal ? collegeLabel(selectedWithdrawal.courseCollege) : '暂无'}</dd>
                </div>
                <div>
                  <dt>选课时间</dt>
                  <dd>{selectedWithdrawal?.enrolledAt || '暂无'}</dd>
                </div>
              </dl>
            </section>
            <section className="selection-detail-section">
              <div className="detail-heading">
                <span>退选学生</span>
                <strong>
                  {loadingWithdrawDetails
                    ? '加载中'
                    : selectedWithdrawalStudent?.name ?? selectedWithdrawal?.studentId ?? '未选择记录'}
                </strong>
              </div>
              <dl className="detail-grid">
                <div>
                  <dt>学号</dt>
                  <dd>{selectedWithdrawalStudent?.id ?? selectedWithdrawal?.studentId ?? '暂无'}</dd>
                </div>
                <div>
                  <dt>性别</dt>
                  <dd>{selectedWithdrawalStudent?.gender ?? '暂无'}</dd>
                </div>
                <div>
                  <dt>专业</dt>
                  <dd>{selectedWithdrawalStudent?.major ?? '暂无'}</dd>
                </div>
                <div>
                  <dt>年级</dt>
                  <dd>{selectedWithdrawalStudent ? `${selectedWithdrawalStudent.grade}级` : '暂无'}</dd>
                </div>
              </dl>
            </section>
            <section className="selection-detail-section">
              <div className="detail-heading">
                <span>退选课程</span>
                <strong>
                  {loadingWithdrawDetails
                    ? '加载中'
                    : selectedWithdrawalCourse?.name ?? selectedWithdrawal?.courseId ?? '未选择记录'}
                </strong>
              </div>
              <dl className="detail-grid">
                <div>
                  <dt>课程号</dt>
                  <dd>{selectedWithdrawalCourse?.id ?? selectedWithdrawal?.courseId ?? '暂无'}</dd>
                </div>
                <div>
                  <dt>课时</dt>
                  <dd>{selectedWithdrawalCourse?.hours ?? '暂无'}</dd>
                </div>
                <div>
                  <dt>学分</dt>
                  <dd>{selectedWithdrawalCourse?.credits ?? '暂无'}</dd>
                </div>
                <div>
                  <dt>老师</dt>
                  <dd>{selectedWithdrawalCourse?.teacher ?? '暂无'}</dd>
                </div>
                <div>
                  <dt>地点</dt>
                  <dd>{selectedWithdrawalCourse?.location ?? '暂无'}</dd>
                </div>
              </dl>
            </section>
          </div>
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

function toEnrollmentXml(payload: EnrollmentCreatePayload) {
  return `<enrollmentRequests>
  <enrollmentRequest>
    <studentCollege>${escapeXml(payload.studentCollege)}</studentCollege>
    <studentId>${escapeXml(payload.studentId.trim())}</studentId>
    <courseCollege>${escapeXml(payload.courseCollege)}</courseCollege>
    <courseId>${escapeXml(payload.courseId.trim())}</courseId>
  </enrollmentRequest>
</enrollmentRequests>`;
}

function toWithdrawalXml(enrollmentId: string) {
  return `<withdrawRequests>
  <withdrawRequest>
    <enrollmentId>${escapeXml(enrollmentId.trim())}</enrollmentId>
  </withdrawRequest>
</withdrawRequests>`;
}

function collegeLabel(code: CollegeCode) {
  return collegeOptions.find((college) => college.code === code)?.label ?? `学院${code}`;
}

function statusLabel(status: string) {
  if (status === 'ACTIVE') {
    return '有效';
  }
  if (status === 'WITHDRAWN') {
    return '已退选';
  }
  return status || '暂无';
}

function escapeXml(value: string) {
  return value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;');
}
