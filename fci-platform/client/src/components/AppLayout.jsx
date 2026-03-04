import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import { capitalize } from '../utils/formatters';

export default function AppLayout({ children, caseInfo }) {
  const { user, logout } = useAuth();
  const { isDark, toggleTheme } = useTheme();

  return (
    <div className="flex flex-col h-screen bg-surface-50 dark:bg-surface-900">
      {/* Frosted glass header */}
      <header className="flex items-center justify-between px-4 h-14 bg-surface-50/80 dark:bg-surface-900/80 glass border-b border-surface-200 dark:border-surface-700/50 shadow-soft-sm sticky top-0 z-50 shrink-0 animate-fade-in-down">
        <div className="flex items-center gap-3">
          {caseInfo && (
            <Link
              to="/cases"
              className="w-8 h-8 rounded-lg hover:bg-surface-100 dark:hover:bg-surface-800 flex items-center justify-center text-surface-500 hover:text-surface-900 dark:hover:text-surface-200"
              title="Back to cases"
            >
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-5 h-5">
                <path fillRule="evenodd" d="M17 10a.75.75 0 0 1-.75.75H5.612l4.158 3.96a.75.75 0 1 1-1.04 1.08l-5.5-5.25a.75.75 0 0 1 0-1.08l5.5-5.25a.75.75 0 1 1 1.04 1.08L5.612 9.25H16.25A.75.75 0 0 1 17 10Z" clipRule="evenodd" />
              </svg>
            </Link>
          )}
          <Link to="/cases" className="text-base font-semibold tracking-tight text-surface-900 dark:text-surface-100 hover:text-gold-500 dark:hover:text-gold-400">
            FCI Investigation Platform
          </Link>
        </div>

        {caseInfo && (
          <div className="flex items-center gap-2 text-sm">
            <span className="text-surface-500 dark:text-surface-400 font-mono">{caseInfo.case_id}</span>
            <span className="inline-flex items-center px-2.5 py-1 rounded-full text-sm font-medium bg-surface-100 dark:bg-surface-750 text-surface-600 dark:text-surface-300 ring-1 ring-surface-200 dark:ring-surface-600">
              {capitalize(caseInfo.case_type)}
            </span>
          </div>
        )}

        <div className="flex items-center gap-2">
          {/* Free chat link */}
          <Link
            to="/chat"
            className="w-8 h-8 rounded-lg hover:bg-surface-100 dark:hover:bg-surface-800 flex items-center justify-center text-surface-500 hover:text-gold-500"
            title="Free Chat"
          >
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-5 h-5">
              <path fillRule="evenodd" d="M10 3c-4.31 0-8 3.033-8 7 0 2.024.978 3.825 2.499 5.085a3.478 3.478 0 01-.522 1.756.75.75 0 00.584 1.143 5.976 5.976 0 003.243-1.028c.659.103 1.357.169 2.196.169 4.31 0 8-3.033 8-7s-3.69-7-8-7z" clipRule="evenodd" />
            </svg>
          </Link>

          {/* Theme toggle */}
          <button
            onClick={toggleTheme}
            className="w-8 h-8 rounded-lg hover:bg-surface-100 dark:hover:bg-surface-800 flex items-center justify-center text-surface-500 hover:text-gold-500"
            title={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
          >
            {isDark ? (
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-5 h-5">
                <path d="M10 2a.75.75 0 01.75.75v1.5a.75.75 0 01-1.5 0v-1.5A.75.75 0 0110 2zM10 15a.75.75 0 01.75.75v1.5a.75.75 0 01-1.5 0v-1.5A.75.75 0 0110 15zM10 7a3 3 0 100 6 3 3 0 000-6zM15.657 5.404a.75.75 0 10-1.06-1.06l-1.061 1.06a.75.75 0 001.06 1.06l1.06-1.06zM6.464 14.596a.75.75 0 10-1.06-1.06l-1.06 1.06a.75.75 0 001.06 1.06l1.06-1.06zM18 10a.75.75 0 01-.75.75h-1.5a.75.75 0 010-1.5h1.5A.75.75 0 0118 10zM5 10a.75.75 0 01-.75.75h-1.5a.75.75 0 010-1.5h1.5A.75.75 0 015 10zM14.596 15.657a.75.75 0 001.06-1.06l-1.06-1.061a.75.75 0 10-1.06 1.06l1.06 1.06zM5.404 6.464a.75.75 0 001.06-1.06l-1.06-1.06a.75.75 0 10-1.06 1.06l1.06 1.06z" />
              </svg>
            ) : (
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-5 h-5">
                <path fillRule="evenodd" d="M7.455 2.004a.75.75 0 01.26.77 7 7 0 009.958 7.967.75.75 0 011.067.853A8.5 8.5 0 116.647 1.921a.75.75 0 01.808.083z" clipRule="evenodd" />
              </svg>
            )}
          </button>

          {user && (
            <span className="text-sm font-medium text-surface-600 dark:text-surface-400">{user.display_name}</span>
          )}
          <button
            onClick={logout}
            className="text-sm text-surface-500 hover:text-surface-900 dark:hover:text-surface-200"
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
