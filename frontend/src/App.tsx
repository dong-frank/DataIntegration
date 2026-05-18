import { Navigate, Route, Routes, useNavigate } from 'react-router-dom';
import { useEffect, useState } from 'react';
import type { LoginResponse } from './types/domain';
import { landingPathForUser } from './api/routing';
import { LoginPage } from './pages/LoginPage';
import { CollegePage } from './pages/CollegePage';
import { IntegrationPage } from './pages/IntegrationPage';
import { StatsPage } from './pages/StatsPage';
import { Shell } from './components/Shell';

const SESSION_KEY = 'data-integration-session';

function isStoredSession(value: unknown): value is LoginResponse {
  if (!value || typeof value !== 'object') {
    return false;
  }

  const session = value as Partial<LoginResponse>;
  const validCollege = session.college === 'A' || session.college === 'B' || session.college === 'C';
  const validAdmin = session.role === 'INTEGRATION_ADMIN' && session.college === null;
  const validCollegeUser = session.role === 'COLLEGE' && validCollege;

  return typeof session.token === 'string' && typeof session.displayName === 'string' && (validAdmin || validCollegeUser);
}

function readSession(): LoginResponse | null {
  const raw = window.localStorage.getItem(SESSION_KEY);
  if (!raw) {
    return null;
  }

  try {
    const session = JSON.parse(raw);
    if (isStoredSession(session)) {
      return session;
    }

    window.localStorage.removeItem(SESSION_KEY);
    return null;
  } catch {
    window.localStorage.removeItem(SESSION_KEY);
    return null;
  }
}

export function App() {
  const [session, setSession] = useState<LoginResponse | null>(() => readSession());
  const navigate = useNavigate();

  useEffect(() => {
    if (session) {
      window.localStorage.setItem(SESSION_KEY, JSON.stringify(session));
    } else {
      window.localStorage.removeItem(SESSION_KEY);
    }
  }, [session]);

  const handleLogin = (user: LoginResponse) => {
    setSession(user);
    navigate(landingPathForUser(user));
  };

  const handleLogout = () => {
    setSession(null);
    navigate('/login');
  };

  if (!session) {
    return (
      <Routes>
        <Route path="/login" element={<LoginPage onLogin={handleLogin} />} />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    );
  }

  return (
    <Shell session={session} onLogout={handleLogout}>
      <Routes>
        <Route path="/college/:college" element={<CollegePage session={session} />} />
        <Route path="/integration" element={<IntegrationPage />} />
        <Route path="/stats" element={<StatsPage />} />
        <Route path="*" element={<Navigate to={landingPathForUser(session)} replace />} />
      </Routes>
    </Shell>
  );
}
