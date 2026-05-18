import type { ReactNode } from 'react';
import { BarChart3, Database, LogOut, Network } from 'lucide-react';
import { Link, NavLink } from 'react-router-dom';
import type { LoginResponse } from '../types/domain';

interface ShellProps {
  session: LoginResponse;
  onLogout: () => void;
  children: ReactNode;
}

export function Shell({ session, onLogout, children }: ShellProps) {
  const isAdmin = session.role === 'INTEGRATION_ADMIN';
  const home = isAdmin ? '/integration' : `/college/${session.college}`;
  const roleLabel = isAdmin ? '集成管理员' : `学院${session.college}`;

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <Link className="brand" to={home}>
          <Database size={22} />
          <span>教务集成</span>
        </Link>
        <nav className="nav-list">
          {!isAdmin && session.college && (
            <NavLink to={`/college/${session.college}`}>
              <Database size={18} />
              学院系统
            </NavLink>
          )}
          <NavLink to="/integration">
            <Network size={18} />
            集成服务器
          </NavLink>
          <NavLink to="/stats">
            <BarChart3 size={18} />
            统计可视化
          </NavLink>
        </nav>
        <div className="session-box">
          <div>
            <span>{session.displayName}</span>
            <small>{roleLabel}</small>
          </div>
          <button className="icon-button" onClick={onLogout} title="退出登录" type="button">
            <LogOut size={18} />
          </button>
        </div>
      </aside>
      <main className="content">{children}</main>
    </div>
  );
}
