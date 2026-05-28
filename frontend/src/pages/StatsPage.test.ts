import { describe, expect, it } from 'vitest';
import source from './StatsPage.tsx?raw';

describe('StatsPage college labels', () => {
  it('maps backend college codes to frontend real college names before rendering', () => {
    expect(source).toContain("from '../utils/collegeLabels'");
    expect(source).toContain('const collegeStats =');
    expect(source).toContain('displayName: collegeLabel(college.college)');
    expect(source).toContain('<BarChart data={collegeStats}>');
    expect(source).toContain('{collegeStats.map((college) => (');
  });
});
