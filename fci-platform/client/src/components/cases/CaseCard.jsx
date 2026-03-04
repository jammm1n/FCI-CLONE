import { useNavigate } from 'react-router-dom';
import { capitalize, statusColor, caseTypeColor, formatTimestamp } from '../../utils/formatters';

export default function CaseCard({ caseData }) {
  const navigate = useNavigate();
  const hasConversation = caseData.conversation_id !== null;

  return (
    <div className="bg-surface-800 border border-surface-700 rounded-lg p-4 hover:border-surface-600 transition-colors">
      <div className="flex items-start justify-between">
        <div className="flex-1 min-w-0">
          {/* Header row: case ID, type badge, status badge */}
          <div className="flex items-center gap-2 mb-2">
            <span className="text-sm font-mono font-medium text-surface-200">
              {caseData.case_id}
            </span>
            <span className={`px-2 py-0.5 rounded text-xs font-medium ${caseTypeColor(caseData.case_type)}`}>
              {capitalize(caseData.case_type)}
            </span>
            <span className={`px-2 py-0.5 rounded text-xs font-medium ${statusColor(caseData.status)}`}>
              {capitalize(caseData.status?.replace('_', ' '))}
            </span>
          </div>

          {/* Summary */}
          <p className="text-sm text-surface-400 mb-2 line-clamp-2">{caseData.summary}</p>

          {/* Meta */}
          <div className="flex items-center gap-4 text-xs text-surface-500">
            <span>Subject: {caseData.subject_user_id}</span>
            {caseData.created_at && (
              <span>{formatTimestamp(caseData.created_at)}</span>
            )}
          </div>
        </div>

        {/* Action button */}
        <button
          onClick={() => navigate(`/investigation/${caseData.case_id}`)}
          className="ml-4 shrink-0 px-4 py-2 text-sm font-medium rounded transition-colors bg-primary-700 hover:bg-primary-600 text-white"
        >
          {hasConversation ? 'Continue Investigation' : 'Open Case'}
        </button>
      </div>
    </div>
  );
}
