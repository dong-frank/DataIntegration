import { describe, expect, it } from 'vitest';
import { landingPathForUser } from './routing';
import type { LoginResponse } from '../types/domain';

describe('landingPathForUser', () => {
  it('routes college users to their own college system', () => {
    const user: LoginResponse = {
      token: 'token-college-a',
      displayName: '学院A教务员',
      role: 'COLLEGE',
      college: 'A',
    };

    expect(landingPathForUser(user)).toBe('/college/A');
  });

  it('routes integration administrators to the integration console', () => {
    const user: LoginResponse = {
      token: 'token-integration',
      displayName: '集成服务器管理员',
      role: 'INTEGRATION_ADMIN',
      college: null,
    };

    expect(landingPathForUser(user)).toBe('/integration');
  });
});
