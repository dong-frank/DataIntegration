import { FormEvent, useState } from 'react';
import { LogIn } from 'lucide-react';
import { api } from '../api/client';
import type { LoginResponse } from '../types/domain';

const demoUsers = [
  { username: 'college-a', label: '学院A', hint: 'SQL Server' },
  { username: 'college-b', label: '学院B', hint: 'Oracle' },
  { username: 'college-c', label: '学院C', hint: 'MySQL' },
  { username: 'integration-admin', label: '集成服务器', hint: 'Admin' },
];

interface LoginPageProps {
  onLogin: (user: LoginResponse) => void;
}

export function LoginPage({ onLogin }: LoginPageProps) {
  const [username, setUsername] = useState('college-a');
  const [password, setPassword] = useState('password');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    setLoading(true);
    setError('');
    try {
      onLogin(await api.login(username, password));
    } catch (err) {
      setError(err instanceof Error ? err.message : '登录失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="login-screen">
      <section className="login-panel">
        <div>
          <p className="eyebrow">Data Integration</p>
          <h1>教务数据集成系统</h1>
        </div>
        <div className="demo-account-grid" aria-label="演示账号">
          {demoUsers.map((user) => (
            <button
              className={username === user.username ? 'demo-account active' : 'demo-account'}
              key={user.username}
              onClick={() => setUsername(user.username)}
              type="button"
            >
              <strong>{user.label}</strong>
              <span>{user.hint}</span>
            </button>
          ))}
        </div>
        <form onSubmit={submit} className="login-form">
          <label>
            密码
            <input
              autoComplete="current-password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              type="password"
            />
          </label>
          {error && <p className="form-error">{error}</p>}
          <button className="primary-button" disabled={loading} type="submit">
            <LogIn size={18} />
            {loading ? '登录中' : '登录'}
          </button>
        </form>
      </section>
    </main>
  );
}
