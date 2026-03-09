import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { capitalize, statusColor, caseTypeColor, formatTimestamp } from '../../utils/formatters';
import * as api from '../../services/api';

export default function CaseCard({ caseData, index = 0, onArchive }) {
  const navigate = useNavigate();
  const { token } = useAuth();
  const hasConversation = caseData.conversation_id !== null;
  const isArchived = caseData.status === 'archived';
  const [exporting, setExporting] = useState(false);
  const [archiving, setArchiving] = useState(false);

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

  async function handleArchive(e) {
    e.stopPropagation();
    if (!confirm('Archive this case? It will be hidden from the active list.')) return;
    setArchiving(true);
    try {
      await api.archiveCase(token, caseData.case_id);
      onArchive?.(caseData.case_id);
    } catch (err) {
      console.error('Archive failed:', err);
    } finally {
      setArchiving(false);
    }
  }

  async function handleUnarchive(e) {
    e.stopPropagation();
    setArchiving(true);
    try {
      const result = await api.unarchiveCase(token, caseData.case_id);
      onArchive?.(caseData.case_id, result.status);
    } catch (err) {
      console.error('Unarchive failed:', err);
    } finally {
      setArchiving(false);
    }
  }

  return (
    <div
      onClick={() => navigate(`/investigation/${caseData.case_id}`)}
      className={`animate-fade-in-up rounded-xl border border-l-2 p-6 cursor-pointer group ${
        isArchived
          ? 'bg-surface-50/50 dark:bg-surface-800/50 border-surface-200 dark:border-surface-700 border-l-surface-300/30 opacity-60'
          : 'bg-surface-50 dark:bg-surface-800 border-surface-200 dark:border-surface-700 border-l-gold-500/30 hover:border-gold-300 dark:hover:border-gold-500/50 hover:shadow-glow-gold hover:-translate-y-0.5'
      }`}
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
            {caseData.case_mode === 'multi' && (
              <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-blue-500/20 text-blue-400 border border-blue-500/30">
                Multi-User ({caseData.total_subjects || caseData.subjects?.length || 0})
              </span>
            )}
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
              {caseData.case_mode === 'multi' && caseData.subjects?.length
                ? caseData.subjects.map((s) => s.user_id || 'Unknown').join(', ')
                : caseData.subject_user_id}
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
          {isArchived ? (
            <button
              onClick={handleUnarchive}
              disabled={archiving}
              title="Restore case"
              className="p-2 rounded-lg text-surface-400 hover:text-gold-500 hover:bg-surface-100 dark:hover:bg-surface-700 transition-colors disabled:opacity-50"
            >
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" className="w-4 h-4">
                <path fillRule="evenodd" d="M8 1a.75.75 0 0 1 .75.75v6.5a.75.75 0 0 1-1.5 0v-6.5A.75.75 0 0 1 8 1ZM4.11 3.05a.75.75 0 0 1 0 1.06 5.5 5.5 0 1 0 7.78 0 .75.75 0 0 1 1.06-1.06 7 7 0 1 1-9.9 0 .75.75 0 0 1 1.06 0Z" clipRule="evenodd" />
              </svg>
            </button>
          ) : (
            <button
              onClick={handleArchive}
              disabled={archiving}
              title="Archive case"
              className="p-2 rounded-lg text-surface-400 hover:text-surface-600 dark:hover:text-surface-300 hover:bg-surface-100 dark:hover:bg-surface-700 transition-colors disabled:opacity-50"
            >
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" className="w-4 h-4">
                <path d="M2 3a1 1 0 0 1 1-1h10a1 1 0 0 1 1 1v1a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V3Z" />
                <path fillRule="evenodd" d="M13 6H3v5a2 2 0 0 0 2 2h6a2 2 0 0 0 2-2V6Zm-5.5 2a.5.5 0 0 0 0 1h1a.5.5 0 0 0 0-1h-1Z" clipRule="evenodd" />
              </svg>
            </button>
          )}
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
          {!hasConversation && !isArchived && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                navigate(`/investigation/${caseData.case_id}?mode=oneshot`);
              }}
              className="px-4 py-2.5 text-sm font-medium rounded-xl border border-amber-500/40 text-amber-500 hover:bg-amber-500/10 hover:border-amber-500/60 transition-colors"
              title="Autopilot: AI produces the full ICR autonomously"
            >
              Autopilot
            </button>
          )}
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
