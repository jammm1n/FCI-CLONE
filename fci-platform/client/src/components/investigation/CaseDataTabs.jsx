const TAB_LABELS = {
  c360_analysis: 'C360',
  elliptic_analysis: 'Elliptic',
  previous_cases: 'Previous Cases',
  chat_history_summary: 'Chat History',
  kyc_summary: 'KYC',
  law_enforcement: 'Law Enforcement',
};

export default function CaseDataTabs({ preprocessedData, activeTab, onTabChange }) {
  const availableTabs = Object.entries(TAB_LABELS).filter(
    ([key]) => preprocessedData[key]
  );

  if (availableTabs.length === 0) return null;

  return (
    <div className="flex gap-0 border-b border-surface-200 dark:border-surface-700 bg-surface-50 dark:bg-surface-800 px-4 shrink-0 overflow-x-auto">
      {availableTabs.map(([key, label]) => (
        <button
          key={key}
          onClick={() => onTabChange(key)}
          className={`px-4 py-3 text-sm font-medium whitespace-nowrap border-b-[3px] rounded-t-lg ${
            activeTab === key
              ? 'border-gold-500 text-gold-600 dark:text-gold-500'
              : 'border-transparent text-surface-500 dark:text-surface-400 hover:text-gold-400 hover:bg-surface-100 dark:hover:bg-surface-700/50'
          }`}
        >
          {label}
        </button>
      ))}
    </div>
  );
}
