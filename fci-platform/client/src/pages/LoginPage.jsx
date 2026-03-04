import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function LoginPage() {
  const [username, setUsername] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    if (!username.trim()) return;

    setError('');
    setLoading(true);
    try {
      await login(username.trim());
      navigate('/cases');
    } catch (err) {
      setError(err.message || 'Login failed');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-surface-900">
      <div className="w-full max-w-sm">
        <div className="bg-surface-800 rounded-lg border border-surface-700 p-8">
          <h1 className="text-xl font-semibold text-center text-surface-100 mb-1">
            FCI Investigation Platform
          </h1>
          <p className="text-sm text-center text-surface-500 mb-8">
            Level 2 Compliance
          </p>

          <form onSubmit={handleSubmit}>
            <label className="block text-xs font-medium text-surface-400 mb-1.5">
              Username
            </label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="ben.investigator"
              autoFocus
              className="w-full px-3 py-2 bg-surface-900 border border-surface-600 rounded text-sm text-surface-100 placeholder-surface-500 focus:outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
            />

            {error && (
              <p className="mt-2 text-xs text-red-400">{error}</p>
            )}

            <button
              type="submit"
              disabled={loading || !username.trim()}
              className="w-full mt-4 px-4 py-2 bg-primary-700 hover:bg-primary-600 disabled:bg-surface-700 disabled:text-surface-500 text-sm font-medium text-white rounded transition-colors"
            >
              {loading ? 'Logging in...' : 'Log In'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
