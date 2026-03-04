import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { capitalize } from '../utils/formatters';

export default function AppLayout({ children, caseInfo }) {
  const { user, logout } = useAuth();

  return (
    <div className="flex flex-col h-screen bg-surface-900">
      {/* Top navigation bar */}
      <header className="flex items-center justify-between px-4 py-2 bg-surface-800 border-b border-surface-700 shrink-0">
        <div className="flex items-center gap-3">
          {caseInfo && (
            <Link to="/cases" className="text-surface-500 hover:text-surface-200 transition-colors" title="Back to cases">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-4 h-4">
                <path fillRule="evenodd" d="M17 10a.75.75 0 0 1-.75.75H5.612l4.158 3.96a.75.75 0 1 1-1.04 1.08l-5.5-5.25a.75.75 0 0 1 0-1.08l5.5-5.25a.75.75 0 1 1 1.04 1.08L5.612 9.25H16.25A.75.75 0 0 1 17 10Z" clipRule="evenodd" />
              </svg>
            </Link>
          )}
          <Link to="/cases" className="text-sm font-semibold text-surface-100 tracking-wide hover:text-primary-400 transition-colors">
            FCI Investigation Platform
          </Link>
        </div>

        {caseInfo && (
          <div className="flex items-center gap-2 text-sm">
            <span className="text-surface-400">{caseInfo.case_id}</span>
            <span className="px-2 py-0.5 rounded text-xs font-medium bg-surface-700 text-surface-300">
              {capitalize(caseInfo.case_type)}
            </span>
          </div>
        )}

        <div className="flex items-center gap-3">
          {user && (
            <span className="text-sm text-surface-400">{user.display_name}</span>
          )}
          <button
            onClick={logout}
            className="text-xs text-surface-500 hover:text-surface-300 transition-colors"
          >
            Logout
          </button>
        </div>
      </header>

      {/* Page content */}
      <main className="flex-1 min-h-0">{children}</main>
    </div>
  );
}
