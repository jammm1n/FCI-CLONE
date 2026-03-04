import { capitalize, statusColor, caseTypeColor } from '../../utils/formatters';

export default function CaseHeader({ caseData }) {
  if (!caseData) return null;

  return (
    <div className="px-6 py-5 border-b border-surface-200 dark:border-surface-700 bg-surface-50 dark:bg-surface-800 shrink-0 animate-fade-in">
      <div className="flex items-center gap-2 mb-2">
        <span className="text-lg font-bold font-mono text-surface-800 dark:text-surface-100">
          {caseData.subject_user_id}
        </span>
        <span className={`${caseTypeColor(caseData.case_type)}`}>
          {capitalize(caseData.case_type)}
        </span>
        <span className={`${statusColor(caseData.status)}`}>
          {capitalize(caseData.status?.replace('_', ' '))}
        </span>
      </div>
      <p className="text-sm text-surface-500 dark:text-surface-400 leading-relaxed line-clamp-2">
        {caseData.summary}
      </p>
    </div>
  );
}
