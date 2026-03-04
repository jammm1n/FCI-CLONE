const TAB_LABELS = {
  c360_analysis: 'C360',
  elliptic_analysis: 'Elliptic',
  previous_cases: 'Previous Cases',
  chat_history_summary: 'Chat History',
  kyc_summary: 'KYC',
  law_enforcement: 'Law Enforcement',
};

export default function CaseDataTabs({ preprocessedData, activeTab, onTabChange }) {
  // Only show tabs that have data
  const availableTabs = Object.entries(TAB_LABELS).filter(
    ([key]) => preprocessedData[key]
  );

  if (availableTabs.length === 0) return null;

  return (
    <div className="flex gap-0 border-b border-surface-700 bg-surface-800 px-2 shrink-0 overflow-x-auto">
      {availableTabs.map(([key, label]) => (
        <button
          key={key}
          onClick={() => onTabChange(key)}
          className={`px-3 py-2 text-xs font-medium whitespace-nowrap transition-colors border-b-2 ${
            activeTab === key
              ? 'border-primary-500 text-primary-400'
              : 'border-transparent text-surface-400 hover:text-surface-200'
          }`}
        >
          {label}
        </button>
      ))}
    </div>
  );
}
