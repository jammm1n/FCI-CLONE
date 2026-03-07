import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { capitalize, statusColor, caseTypeColor, formatTimestamp } from '../../utils/formatters';
import * as api from '../../services/api';

export default function CaseCard({ caseData, index = 0 }) {
  const navigate = useNavigate();
  const { token } = useAuth();
  const hasConversation = caseData.conversation_id !== null;
  const [exporting, setExporting] = useState(false);

  async function handleExport(e) {
    e.stopPropagation();
    setExporting(true);
    try {
      await api.exportCase(token, caseData.case_id);
    } catch (err) {
      console.error('Export failed:', err);
    } finally {
      setExporting(false);
    }
  }

  return (
    <div
      onClick={() => navigate(`/investigation/${caseData.case_id}`)}
      className="animate-fade-in-up bg-surface-50 dark:bg-surface-800 rounded-xl border border-surface-200 dark:border-surface-700 border-l-2 border-l-gold-500/30 p-6 hover:border-gold-300 dark:hover:border-gold-500/50 hover:shadow-glow-gold hover:-translate-y-0.5 cursor-pointer group"
      style={{ animationDelay: `${index * 100}ms` }}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1 min-w-0">
          {/* Header row */}
          <div className="flex items-center gap-2 mb-3">
            <span className="text-lg font-semibold font-mono text-surface-800 dark:text-surface-100">
              {caseData.case_id}
            </span>
            <span className={`${caseTypeColor(caseData.case_type)}`}>
              {capitalize(caseData.case_type)}
            </span>
            <span className={`${statusColor(caseData.status)}`}>
              {capitalize(caseData.status?.replace('_', ' '))}
            </span>
          </div>

          {/* Summary */}
          {caseData.summary && (
            <p className="text-base text-surface-600 dark:text-surface-300 leading-relaxed line-clamp-2">
              {caseData.summary}
            </p>
          )}

          {/* Meta row */}
          <div className="flex items-center gap-4 text-sm text-surface-500 dark:text-surface-400 mt-4">
            <span className="inline-flex items-center gap-1.5">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" className="w-3.5 h-3.5 opacity-60">
                <path d="M8 8a3 3 0 1 0 0-6 3 3 0 0 0 0 6ZM12.735 14c.618 0 1.093-.561.872-1.139a6.002 6.002 0 0 0-11.215 0c-.22.578.254 1.139.872 1.139h9.47Z" />
              </svg>
              {caseData.subject_user_id}
            </span>
            {caseData.created_at && (
              <span className="inline-flex items-center gap-1.5">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" className="w-3.5 h-3.5 opacity-60">
                  <path fillRule="evenodd" d="M4 1.75a.75.75 0 0 1 1.5 0V3h5V1.75a.75.75 0 0 1 1.5 0V3a2 2 0 0 1 2 2v7a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2V1.75ZM4.5 7a.75.75 0 0 0 0 1.5h7a.75.75 0 0 0 0-1.5h-7Z" clipRule="evenodd" />
                </svg>
                {formatTimestamp(caseData.created_at)}
              </span>
            )}
          </div>
        </div>

        {/* Action buttons */}
        <div className="ml-4 shrink-0 flex items-center gap-2">
          <button
            onClick={handleExport}
            disabled={exporting}
            title="Export case data as markdown"
            className="p-2 rounded-lg text-surface-400 hover:text-gold-500 hover:bg-surface-100 dark:hover:bg-surface-700 transition-colors disabled:opacity-50"
          >
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" className="w-4 h-4">
              <path d="M8.75 2.75a.75.75 0 0 0-1.5 0v5.69L5.03 6.22a.75.75 0 0 0-1.06 1.06l3.5 3.5a.75.75 0 0 0 1.06 0l3.5-3.5a.75.75 0 0 0-1.06-1.06L8.75 8.44V2.75Z" />
              <path d="M3.5 9.75a.75.75 0 0 0-1.5 0v1.5A2.75 2.75 0 0 0 4.75 14h6.5A2.75 2.75 0 0 0 14 11.25v-1.5a.75.75 0 0 0-1.5 0v1.5c0 .69-.56 1.25-1.25 1.25h-6.5c-.69 0-1.25-.56-1.25-1.25v-1.5Z" />
            </svg>
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation();
              navigate(`/investigation/${caseData.case_id}`);
            }}
            className="px-5 py-2.5 text-sm font-medium rounded-xl border border-gold-500 text-gold-500 hover:bg-gold-500 hover:text-surface-950 group-hover:bg-gold-500 group-hover:text-surface-950"
          >
            {hasConversation ? 'Continue' : 'Open Case'}
          </button>
        </div>
      </div>
    </div>
  );
}
