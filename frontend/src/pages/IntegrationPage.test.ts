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
    expect(source).toContain('selectedStudent');
    expect(source).toContain('学生信息');
    expect(source).toContain('课程信息');
    expect(source).toContain('student.id');
    expect(source).toContain('course.id');
    expect(source).not.toContain('选课 XML 报文');
  });

  it('uses selectable enrollment records with detail panels instead of showing withdrawal XML', () => {
    expect(source).toContain('api.enrollments(withdrawCollege)');
    expect(source).toContain('withdrawEnrollmentOptions');
    expect(source).toContain('selectedWithdrawal');
    expect(source).toContain('选课信息');
    expect(source).toContain('退选学生');
    expect(source).not.toContain('退课 XML 报文');
  });

  it('does not show XML previews in the shared courses section', () => {
    expect(source).not.toContain('XML 课程共享报文');
    expect(source).not.toContain('sharedCourseXml');
    expect(source).not.toContain('api.sharedCoursesXml(source,');
  });
});
