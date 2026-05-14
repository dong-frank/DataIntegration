import type { LoginResponse } from '../types/domain';

export function landingPathForUser(user: LoginResponse): string {
  if (user.role === 'INTEGRATION_ADMIN') {
    return '/integration';
  }
  return `/college/${user.college}`;
}
