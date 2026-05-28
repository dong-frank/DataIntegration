import { describe, expect, it } from 'vitest';
import source from './IntegrationPage.tsx?raw';

describe('IntegrationPage XML workflow', () => {
  it('uses XML endpoints as the only visible enrollment and withdrawal actions', () => {
    expect(source).toContain('api.enrollXml(enrollmentXml)');
    expect(source).toContain('api.withdrawXml(withdrawalXml)');
    expect(source).not.toContain('api.enroll({');
    expect(source).not.toContain('api.withdraw(enrollmentId.trim())');
    expect(source).not.toContain('XML 选课');
    expect(source).not.toContain('XML 退选');
  });

  it('labels withdrawal input as an existing enrollment record id', () => {
    expect(source).toContain('选课记录号');
    expect(source).not.toContain('退课记录');
  });

  it('uses selectable student and course fields with detail panels instead of showing enrollment XML', () => {
    expect(source).toContain('api.students(enrollForm.studentCollege)');
    expect(source).toContain('api.sharedCourses(enrollForm.courseCollege)');
    expect(source).toContain('selectedStudent');
    expect(source).toContain('学生信息');
    expect(source).toContain('课程信息');
    expect(source).toContain('student.id');
    expect(source).toContain('course.id');
    expect(source).not.toContain('选课 XML 报文');
  });

  it('loads and renders all college data in integration overview tables', () => {
    expect(source).toContain("from '../components/DataTable'");
    expect(source).toContain('setAllStudents(nextAllStudents.flat())');
    expect(source).toContain('setAllCourses(nextAllCourses.flat())');
    expect(source).toContain('setAllEnrollments(nextAllEnrollments.flat())');
    expect(source).toContain('<h2>课程信息</h2>');
    expect(source).toContain('<h2>学生信息</h2>');
    expect(source).toContain('<h2>选课信息</h2>');
    expect(source).toContain('可跨院选修');
    expect(source).toContain('displayCollegeText(student.major)');
    expect(source).not.toContain("label: '共享'");
    expect(source.indexOf('<h2>课程信息</h2>')).toBeGreaterThan(source.indexOf('重叠课程'));
    expect(source.indexOf('<h2>跨学院选课</h2>')).toBeGreaterThan(source.indexOf('<h2>选课信息</h2>'));
  });

  it('uses all-college enrollment records for withdrawal instead of requiring a record college', () => {
    expect(source).toContain("allEnrollments.filter((record) => record.status !== 'WITHDRAWN')");
    expect(source).toContain('withdrawEnrollmentOptions');
    expect(source).toContain('selectedWithdrawal');
    expect(source).toContain('collegeLabel(record.studentCollege)');
    expect(source).toContain('collegeLabel(record.courseCollege)');
    expect(source).toContain('选课信息');
    expect(source).toContain('退选学生');
    expect(source).not.toContain('api.enrollments(withdrawCollege)');
    expect(source).not.toContain('记录学院');
    expect(source).not.toContain('退课 XML 报文');
  });

  it('does not show XML previews in the shared courses section', () => {
    expect(source).not.toContain('XML 课程共享报文');
    expect(source).not.toContain('sharedCourseXml');
    expect(source).not.toContain('api.sharedCoursesXml(source,');
  });

  it('does not render the shared-course toolbar or standalone shared-course table', () => {
    expect(source).not.toContain('共享课程来源');
    expect(source).not.toContain('toolbar-summary');
    expect(source).not.toContain('selectCourse');
  });

  it('shows integration summary metric cards before the workflow panels', () => {
    expect(source.indexOf('总学生')).toBeGreaterThan(-1);
    expect(source.indexOf('总课程')).toBeGreaterThan(source.indexOf('总学生'));
    expect(source.indexOf('总选课')).toBeGreaterThan(source.indexOf('总课程'));
    expect(source.indexOf('重叠课程')).toBeGreaterThan(source.indexOf('总选课'));
    expect(source.indexOf('<h2>课程信息</h2>')).toBeGreaterThan(source.indexOf('重叠课程'));
  });

  it('keeps load errors inline but shows enrollment and withdrawal results in a modal', () => {
    expect(source).toContain('{error && <div className="form-error">{error}</div>}');
    expect(source).toContain("type Notification = { type: 'success' | 'error'; text: string };");
    expect(source).toContain('role="alertdialog"');
    expect(source).toContain('notification.text');
    expect(source).toContain('setNotification({');
    expect(source).toContain('知道了');
    expect(source).toContain("actionErrorMessage(err, '选课创建失败，请检查是否重复选课或后端服务状态')");
    expect(source).toContain("actionErrorMessage(err, '退课失败，请检查选课记录是否仍然有效或后端服务状态')");
    expect(source).toContain("err.message === 'Internal Server Error'");
    expect(source).not.toContain('const [message');
    expect(source).not.toContain('{message && <div className="notice">{message}</div>}');
  });
});
