import { capitalize, statusColor, caseTypeColor } from '../../utils/formatters';

export default function CaseHeader({ caseData }) {
  if (!caseData) return null;

  return (
    <div className="px-4 py-3 border-b border-surface-700 bg-surface-800 shrink-0">
      <div className="flex items-center gap-2 mb-1">
        <span className="text-sm font-mono font-medium text-surface-200">
          {caseData.subject_user_id}
        </span>
        <span className={`px-2 py-0.5 rounded text-xs font-medium ${caseTypeColor(caseData.case_type)}`}>
          {capitalize(caseData.case_type)}
        </span>
        <span className={`px-2 py-0.5 rounded text-xs font-medium ${statusColor(caseData.status)}`}>
          {capitalize(caseData.status?.replace('_', ' '))}
        </span>
      </div>
      <p className="text-xs text-surface-500 line-clamp-2">{caseData.summary}</p>
    </div>
  );
}
