import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import * as api from '../services/api';
import AppLayout from '../components/AppLayout';
import CaseCard from '../components/cases/CaseCard';
import LoadingSpinner from '../components/shared/LoadingSpinner';

function ResetDemoButton() {
  const { token, logout } = useAuth();
  const [resetting, setResetting] = useState(false);
  const [error, setError] = useState('');

  async function handleReset() {
    if (!window.confirm('Reset all data and reseed demo cases? You will be logged out.')) return;
    setResetting(true);
    setError('');
    try {
      await api.reseedDatabase(token);
      logout();
    } catch (err) {
      setError(err.message);
      setResetting(false);
    }
  }

  return (
    <div className="mt-10 flex flex-col items-center gap-1">
      <button
        onClick={handleReset}
        disabled={resetting}
        className="inline-flex items-center gap-1.5 text-xs text-surface-400 hover:text-gold-500 transition-colors disabled:opacity-50"
      >
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" className={`w-3.5 h-3.5 ${resetting ? 'animate-spin' : ''}`}>
          <path fillRule="evenodd" d="M13.836 2.477a.75.75 0 0 1 .75.75v3.182a.75.75 0 0 1-.75.75h-3.182a.75.75 0 0 1 0-1.5h1.37l-.84-.841a4.5 4.5 0 0 0-7.08.932.75.75 0 0 1-1.3-.75 6 6 0 0 1 9.44-1.242l.842.84V3.227a.75.75 0 0 1 .75-.75Zm-.911 7.5A.75.75 0 0 1 13.199 11a6 6 0 0 1-9.44 1.241l-.84-.84v1.371a.75.75 0 0 1-1.5 0V9.591a.75.75 0 0 1 .75-.75H5.35a.75.75 0 0 1 0 1.5H3.98l.841.841a4.5 4.5 0 0 0 7.08-.932.75.75 0 0 1 1.025-.273Z" clipRule="evenodd" />
        </svg>
        {resetting ? 'Reseeding...' : 'Reset demo data'}
      </button>
      {error && <p className="text-xs text-red-400">{error}</p>}
    </div>
  );
}

export default function CaseListPage() {
  const { token } = useAuth();
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    async function fetchCases() {
      try {
        const data = await api.getCases(token);
        setCases(data.cases);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    fetchCases();
  }, [token]);

  return (
    <AppLayout>
      <div className="max-w-4xl mx-auto px-6 py-6 animate-fade-in">
        {/* Page header */}
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-surface-900 dark:text-surface-100">Investigations</h2>
            {!loading && !error && (
              <p className="text-sm text-surface-500 mt-1">
                {cases.length} active case{cases.length !== 1 ? 's' : ''}
              </p>
            )}
          </div>
          <Link
            to="/chat"
            className="inline-flex items-center gap-2.5 px-5 py-2.5 rounded-xl text-base font-semibold border border-gold-500/40 text-gold-600 dark:text-gold-400 hover:bg-gold-500/10 hover:border-gold-500/60 transition-colors"
          >
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-5 h-5">
              <path fillRule="evenodd" d="M10 3c-4.31 0-8 3.033-8 7 0 2.024.978 3.825 2.499 5.085a3.478 3.478 0 01-.522 1.756.75.75 0 00.584 1.143 5.976 5.976 0 003.243-1.028c.659.103 1.357.169 2.196.169 4.31 0 8-3.033 8-7s-3.69-7-8-7z" clipRule="evenodd" />
            </svg>
            Free Chat
          </Link>
        </div>

        {loading && (
          <div className="flex justify-center py-12">
            <LoadingSpinner size="lg" />
          </div>
        )}

        {error && (
          <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-4 text-sm text-red-500 dark:text-red-400">
            {error}
          </div>
        )}

        {!loading && !error && cases.length === 0 && (
          <div className="flex flex-col items-center justify-center py-16 text-surface-400">
            <svg xmlns="http://www.w3.org/2000/svg" className="w-12 h-12 mb-3 opacity-50" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
            </svg>
            <p className="text-base">No cases assigned</p>
          </div>
        )}

        <div className="grid grid-cols-1 gap-4">
          {cases.map((c, index) => (
            <CaseCard key={c.case_id} caseData={c} index={index} />
          ))}
        </div>

        <ResetDemoButton />
      </div>
    </AppLayout>
  );
}
