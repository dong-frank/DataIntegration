import { describe, expect, it } from 'vitest';
import source from './CollegePage.tsx?raw';

describe('CollegePage full data tables', () => {
  it('shows all students and enrollments in scrollable tables instead of sample rows', () => {
    expect(source).toContain('<h2>学生信息</h2>');
    expect(source).toContain('<h2>选课信息</h2>');
    expect(source).toContain('rows={students}');
    expect(source).toContain('rows={enrollments}');
    expect(source).toContain('className="scroll-table"');
    expect(source).not.toContain('学生样例');
    expect(source).not.toContain('选课样例');
    expect(source).not.toContain('前 8 条');
    expect(source).not.toContain('slice(0, 8)');
    expect(source).not.toContain('visibleEnrollments');
  });
});
