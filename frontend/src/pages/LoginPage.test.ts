import { describe, expect, it } from 'vitest';
import source from './LoginPage.tsx?raw';

describe('LoginPage account selection', () => {
  it('uses the demo account cards as the only account selector', () => {
    expect(source).toContain('aria-label="演示账号"');
    expect(source).toContain('onClick={() => setUsername(user.username)}');
    expect(source).not.toContain('<select value={username}');
    expect(source).not.toContain('<option key={user.username}');
  });
});
