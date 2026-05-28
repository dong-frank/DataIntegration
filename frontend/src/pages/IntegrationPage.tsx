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
import { collegeLabel, displayCollegeText } from '../utils/collegeLabels';

const collegeOptions: Array<{ code: CollegeCode; label: string; dbms: string }> = [
  { code: 'A', label: collegeLabel('A'), dbms: 'SQL Server' },
  { code: 'B', label: collegeLabel('B'), dbms: 'Oracle' },
  { code: 'C', label: collegeLabel('C'), dbms: 'MySQL' },
];

const defaultEnrollForm: EnrollmentCreatePayload = {
  studentCollege: 'A',
  studentId: '202300000001',
  courseCollege: 'B',
  courseId: 'B0001',
};

type Notification = { type: 'success' | 'error'; text: string };

export function IntegrationPage() {
  const [courses, setCourses] = useState<CourseRecord[]>([]);
  const [students, setStudents] = useState<StudentRecord[]>([]);
  const [allCourses, setAllCourses] = useState<CourseRecord[]>([]);
  const [allStudents, setAllStudents] = useState<StudentRecord[]>([]);
  const [allEnrollments, setAllEnrollments] = useState<EnrollmentRecord[]>([]);
  const [withdrawStudents, setWithdrawStudents] = useState<StudentRecord[]>([]);
  const [withdrawCourses, setWithdrawCourses] = useState<CourseRecord[]>([]);
  const [stats, setStats] = useState<StatsSummary | null>(null);
  const [enrollmentId, setEnrollmentId] = useState('B0001-202200001');
  const [enrollForm, setEnrollForm] = useState<EnrollmentCreatePayload>(defaultEnrollForm);
  const [notification, setNotification] = useState<Notification | null>(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const [loadingStudents, setLoadingStudents] = useState(true);
  const [loadingWithdrawDetails, setLoadingWithdrawDetails] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const [nextCourses, nextStats, nextAllStudents, nextAllCourses, nextAllEnrollments] = await Promise.all([
        api.sharedCourses(enrollForm.courseCollege),
        api.stats(),
        Promise.all(collegeOptions.map((college) => api.students(college.code))),
        Promise.all(collegeOptions.map((college) => api.courses(college.code))),
        Promise.all(collegeOptions.map((college) => api.enrollments(college.code))),
      ]);
      setCourses(nextCourses);
      setStats(nextStats);
      setAllStudents(nextAllStudents.flat());
      setAllCourses(nextAllCourses.flat());
      setAllEnrollments(nextAllEnrollments.flat());
    } catch (err) {
      setError(err instanceof Error ? err.message : '集成数据加载失败');
    } finally {
      setLoading(false);
    }
  }, [enrollForm.courseCollege]);

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

  useEffect(() => {
    void load();
  }, [load]);

  useEffect(() => {
    void loadStudents();
  }, [loadStudents]);

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
    () => allEnrollments.filter((record) => record.status !== 'WITHDRAWN'),
    [allEnrollments],
  );
  const selectedWithdrawal = useMemo(
    () => allEnrollments.find((record) => record.id === enrollmentId),
    [allEnrollments, enrollmentId],
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

  const enroll = async (event: FormEvent) => {
    event.preventDefault();
    setSubmitting(true);
    setError('');
    setNotification(null);
    try {
      const records = await api.enrollXml(enrollmentXml);
      const firstRecord = records[0];
      await load();
      if (firstRecord) {
        setEnrollmentId(firstRecord.id);
      }
      setNotification({
        type: firstRecord ? 'success' : 'error',
        text: firstRecord ? `已通过 XML 创建选课记录 ${firstRecord.id}` : 'XML 请求未创建选课记录',
      });
    } catch (err) {
      setNotification({
        type: 'error',
        text: actionErrorMessage(err, '选课创建失败，请检查是否重复选课或后端服务状态'),
      });
    } finally {
      setSubmitting(false);
    }
  };

  const withdraw = async (event: FormEvent) => {
    event.preventDefault();
    setSubmitting(true);
    setError('');
    setNotification(null);
    try {
      const results = await api.withdrawXml(withdrawalXml);
      const firstResult = results[0];
      await load();
      setNotification({
        type: firstResult?.withdrawn ? 'success' : 'error',
        text: firstResult?.withdrawn ? `${firstResult.enrollmentId} 已通过 XML 完成退选` : `${enrollmentId} 未找到`,
      });
    } catch (err) {
      setNotification({
        type: 'error',
        text: actionErrorMessage(err, '退课失败，请检查选课记录是否仍然有效或后端服务状态'),
      });
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

      <section className="panel">
        <div className="panel-heading">
          <h2>课程信息</h2>
          <span>
            {loading
              ? '加载中'
              : `${allCourses.length} 门课程 / ${allCourses.filter((course) => course.shared).length} 门可跨院选修`}
          </span>
        </div>
        <div className="scroll-table">
          <DataTable
            rows={allCourses}
            emptyText={loading ? '正在加载课程' : '暂无课程'}
            columns={[
              { key: 'college', label: '学院', render: (course) => collegeLabel(course.college) },
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
        </div>
      </section>

      <section className="split-grid">
        <div className="panel">
          <div className="panel-heading">
            <h2>学生信息</h2>
            <span>{loading ? '加载中' : `${allStudents.length} 条`}</span>
          </div>
          <div className="scroll-table">
            <DataTable
              rows={allStudents}
              emptyText={loading ? '正在加载学生' : '暂无学生'}
              columns={[
                { key: 'college', label: '学院', render: (student) => collegeLabel(student.college) },
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
            <span>{loading ? '加载中' : `${allEnrollments.length} 条`}</span>
          </div>
          <div className="scroll-table">
            <DataTable
              rows={allEnrollments}
              emptyText={loading ? '正在加载选课' : '暂无选课'}
              columns={[
                { key: 'id', label: '记录号', render: (enrollment) => enrollment.id },
                { key: 'studentCollege', label: '学生学院', render: (enrollment) => collegeLabel(enrollment.studentCollege) },
                { key: 'studentId', label: '学生', render: (enrollment) => enrollment.studentId },
                { key: 'courseCollege', label: '课程学院', render: (enrollment) => collegeLabel(enrollment.courseCollege) },
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
              <select
                value={enrollForm.courseId}
                disabled={loading || courses.length === 0}
                onChange={(event) => updateEnrollForm('courseId', event.target.value)}
              >
                {courses.length === 0 ? (
                  <option value={enrollForm.courseId}>{loading ? '加载课程中' : '暂无可跨院选修课程'}</option>
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
                  <dd>{selectedStudent ? displayCollegeText(selectedStudent.major) : '暂无'}</dd>
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
            <label className="form-action">
              选课记录号
              <select
                value={enrollmentId}
                disabled={loading || withdrawEnrollmentOptions.length === 0}
                onChange={(event) => setEnrollmentId(event.target.value)}
              >
                {withdrawEnrollmentOptions.length === 0 ? (
                  <option value={enrollmentId}>{loading ? '加载选课记录中' : '暂无可退选记录'}</option>
                ) : (
                  withdrawEnrollmentOptions.map((record) => (
                    <option key={record.id} value={record.id}>
                      {record.id} / {collegeLabel(record.studentCollege)} {record.studentId} /{' '}
                      {collegeLabel(record.courseCollege)} {record.courseId}
                    </option>
                  ))
                )}
              </select>
            </label>
            <button
              className="danger-button form-action"
              disabled={submitting || !selectedWithdrawal || selectedWithdrawal.status === 'WITHDRAWN'}
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
                  <dd>{selectedWithdrawalStudent ? displayCollegeText(selectedWithdrawalStudent.major) : '暂无'}</dd>
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

      {notification && (
        <div className="notification-backdrop">
          <div
            aria-labelledby="integration-notification-title"
            aria-modal="true"
            className="notification-dialog"
            role="alertdialog"
          >
            <span className={`notification-status notification-status-${notification.type}`}>
              {notification.type === 'success' ? '操作成功' : '操作失败'}
            </span>
            <h2 id="integration-notification-title">
              {notification.type === 'success' ? '处理完成' : '需要处理'}
            </h2>
            <p>{notification.text}</p>
            <div className="notification-actions">
              <button className="primary-button" onClick={() => setNotification(null)} type="button">
                知道了
              </button>
            </div>
          </div>
        </div>
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

function statusLabel(status: string) {
  if (status === 'ACTIVE') {
    return '有效';
  }
  if (status === 'WITHDRAWN') {
    return '已退选';
  }
  return status || '暂无';
}

function actionErrorMessage(err: unknown, fallback: string) {
  if (!(err instanceof Error) || !err.message || err.message === 'Internal Server Error') {
    return fallback;
  }
  return err.message;
}

function escapeXml(value: string) {
  return value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;');
}
