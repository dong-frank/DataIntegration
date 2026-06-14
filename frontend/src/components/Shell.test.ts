import { describe, expect, it } from 'vitest';
import source from './Shell.tsx?raw';

describe('Shell college labels', () => {
  it('derives college display names in the frontend instead of trusting backend display text', () => {
    expect(source).toContain("from '../utils/collegeLabels'");
    expect(source).toContain('const displayName =');
    expect(source).toContain('`${collegeLabel(session.college)}教务员`');
    expect(source).toContain('<span>{displayName}</span>');
    expect(source).toContain('<small>{roleLabel}</small>');
  });
});
