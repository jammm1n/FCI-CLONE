import { useEffect, useState } from 'react';
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
        <div className="mb-6">
          <h2 className="text-2xl font-bold text-surface-900 dark:text-surface-100">Investigations</h2>
          {!loading && !error && (
            <p className="text-sm text-surface-500 mt-1">
              {cases.length} active case{cases.length !== 1 ? 's' : ''}
            </p>
          )}
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
      </div>
    </AppLayout>
  );
}
