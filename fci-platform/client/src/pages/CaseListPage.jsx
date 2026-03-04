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
      <div className="max-w-4xl mx-auto px-6 py-8">
        <h2 className="text-lg font-semibold text-surface-100 mb-6">Your Cases</h2>

        {loading && (
          <div className="flex justify-center py-12">
            <LoadingSpinner size="lg" />
          </div>
        )}

        {error && (
          <div className="bg-red-900/20 border border-red-800 rounded p-4 text-sm text-red-400">
            {error}
          </div>
        )}

        {!loading && !error && cases.length === 0 && (
          <p className="text-surface-500 text-sm">No cases assigned.</p>
        )}

        <div className="space-y-4">
          {cases.map((c) => (
            <CaseCard key={c.case_id} caseData={c} />
          ))}
        </div>
      </div>
    </AppLayout>
  );
}
