import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    if (!username.trim() || !password) return;

    setError('');
    setLoading(true);
    try {
      await login(username.trim(), password);
      navigate('/cases');
    } catch (err) {
      setError(err.message || 'Login failed');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center relative overflow-hidden">
      {/* Atmospheric background */}
      <div
        className="absolute inset-0 animate-fade-in"
        style={{
          background: 'radial-gradient(ellipse at center, var(--bg-secondary) 0%, var(--bg-primary) 70%)',
        }}
      />
      {/* Dot-grid pattern overlay */}
      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          backgroundImage: 'radial-gradient(rgba(240, 185, 11, 0.04) 1px, transparent 1px)',
          backgroundSize: '24px 24px',
        }}
      />

      {/* Login card */}
      <div
        className="relative w-full max-w-md animate-scale-in"
        style={{ animationDelay: '100ms' }}
      >
        {/* Gold top accent bar */}
        <div className="h-1 bg-gradient-to-r from-gold-600 to-gold-400 rounded-t-2xl" />

        <div className="bg-surface-50 dark:bg-surface-800 rounded-b-2xl shadow-soft-xl dark:shadow-none dark:border dark:border-surface-700 p-8">
          {/* Title */}
          <div
            className="text-center mb-8 animate-fade-in"
            style={{ animationDelay: '250ms' }}
          >
            <h1 className="text-2xl font-bold bg-gradient-to-r from-gold-500 to-gold-400 bg-clip-text text-transparent">
              FCI Investigation Platform
            </h1>
            <p className="text-sm text-surface-500 dark:text-surface-400 mt-1">
              Level 2 Compliance
            </p>
          </div>

          <form onSubmit={handleSubmit}>
            {/* Input */}
            <div
              className="animate-fade-in-up"
              style={{ animationDelay: '350ms' }}
            >
              <label className="block text-sm font-medium text-surface-600 dark:text-surface-400 mb-1.5">
                Username
              </label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="ben.investigator"
                autoFocus
                className="w-full h-11 px-4 text-base rounded-xl bg-surface-100 dark:bg-surface-900 border border-surface-200 dark:border-surface-600 text-surface-900 dark:text-surface-100 placeholder-surface-400 focus:outline-none focus:ring-2 focus:ring-gold-500/30 focus:border-gold-500"
              />
            </div>

            <div
              className="mt-4 animate-fade-in-up"
              style={{ animationDelay: '400ms' }}
            >
              <label className="block text-sm font-medium text-surface-600 dark:text-surface-400 mb-1.5">
                Password
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full h-11 px-4 text-base rounded-xl bg-surface-100 dark:bg-surface-900 border border-surface-200 dark:border-surface-600 text-surface-900 dark:text-surface-100 placeholder-surface-400 focus:outline-none focus:ring-2 focus:ring-gold-500/30 focus:border-gold-500"
              />
            </div>

            {/* Error message */}
            {error && (
              <p className="mt-3 text-sm text-red-500 dark:text-red-400 animate-fade-in-up">
                {error}
              </p>
            )}

            {/* Submit button */}
            <div
              className="animate-fade-in-up"
              style={{ animationDelay: '450ms' }}
            >
              <button
                type="submit"
                disabled={loading || !username.trim() || !password}
                className="w-full mt-5 h-11 text-base font-semibold rounded-xl bg-gradient-to-r from-gold-500 to-gold-400 text-surface-950 shadow-lg shadow-gold-500/25 hover:shadow-gold-500/40 active:scale-[0.98] disabled:from-surface-300 disabled:to-surface-400 dark:disabled:from-surface-700 dark:disabled:to-surface-600 disabled:text-surface-500 disabled:shadow-none"
              >
                {loading ? (
                  <span className="inline-flex items-center gap-2">
                    <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                    </svg>
                    Logging in...
                  </span>
                ) : (
                  'Log In'
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
