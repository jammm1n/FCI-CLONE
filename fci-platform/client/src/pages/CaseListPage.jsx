import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import * as api from '../services/api';
import AppLayout from '../components/AppLayout';
import CaseCard from '../components/cases/CaseCard';
import LoadingSpinner from '../components/shared/LoadingSpinner';

export default function CaseListPage() {
  const { token } = useAuth();
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showArchived, setShowArchived] = useState(false);

  useEffect(() => {
    async function fetchCases() {
      setLoading(true);
      try {
        const data = await api.getCases(token, showArchived);
        setCases(data.cases);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    fetchCases();
  }, [token, showArchived]);

  function handleArchive(caseId) {
    setCases((prev) => prev.filter((c) => c.case_id !== caseId));
  }

  return (
    <AppLayout>
      <div className="max-w-4xl mx-auto px-6 py-6 animate-fade-in">
        {/* Page header */}
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-surface-900 dark:text-surface-100">Investigations</h2>
            {!loading && !error && (
              <p className="text-sm text-surface-500 mt-1">
                {cases.filter((c) => c.status !== 'archived').length} active case{cases.filter((c) => c.status !== 'archived').length !== 1 ? 's' : ''}
                {showArchived && cases.some((c) => c.status === 'archived') && (
                  <span className="text-surface-400"> + {cases.filter((c) => c.status === 'archived').length} archived</span>
                )}
              </p>
            )}
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => setShowArchived((v) => !v)}
              className={`inline-flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                showArchived
                  ? 'bg-surface-200 dark:bg-surface-700 text-surface-700 dark:text-surface-300'
                  : 'text-surface-400 hover:text-surface-600 dark:hover:text-surface-300 hover:bg-surface-100 dark:hover:bg-surface-800'
              }`}
              title={showArchived ? 'Hide archived cases' : 'Show archived cases'}
            >
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" className="w-4 h-4">
                <path d="M2 3a1 1 0 0 1 1-1h10a1 1 0 0 1 1 1v1a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V3Z" />
                <path fillRule="evenodd" d="M13 6H3v5a2 2 0 0 0 2 2h6a2 2 0 0 0 2-2V6Zm-5.5 2a.5.5 0 0 0 0 1h1a.5.5 0 0 0 0-1h-1Z" clipRule="evenodd" />
              </svg>
              Archive
            </button>
            <Link
              to="/ingest"
              className="inline-flex items-center gap-2.5 px-5 py-2.5 rounded-xl text-base font-semibold border border-gold-500/40 text-gold-600 dark:text-gold-400 hover:bg-gold-500/10 hover:border-gold-500/60 transition-colors"
            >
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-5 h-5">
                <path d="M10.75 2.75a.75.75 0 0 0-1.5 0v8.614L6.295 8.235a.75.75 0 1 0-1.09 1.03l4.25 4.5a.75.75 0 0 0 1.09 0l4.25-4.5a.75.75 0 0 0-1.09-1.03l-2.955 3.129V2.75Z" />
                <path d="M3.5 12.75a.75.75 0 0 0-1.5 0v2.5A2.75 2.75 0 0 0 4.75 18h10.5A2.75 2.75 0 0 0 18 15.25v-2.5a.75.75 0 0 0-1.5 0v2.5c0 .69-.56 1.25-1.25 1.25H4.75c-.69 0-1.25-.56-1.25-1.25v-2.5Z" />
              </svg>
              Ingest
            </Link>
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
            <p className="text-sm mt-1">Assemble a case from the Ingest page to begin investigating.</p>
          </div>
        )}

        <div className="grid grid-cols-1 gap-4">
          {cases.map((c, index) => (
            <CaseCard key={c.case_id} caseData={c} index={index} onArchive={handleArchive} />
          ))}
        </div>
      </div>
    </AppLayout>
  );
}
