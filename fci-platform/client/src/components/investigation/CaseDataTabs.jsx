const TAB_LABELS = {
  l1_referral_narrative: 'L1 Referral',
  hexa_dump: 'HEXA Dump',
  kyc_id_document: 'KYC / ID',
  c360_transaction_summary: 'C360',
  web_app_outputs: 'Web App',
  elliptic_screening: 'Elliptic',
  prior_icr_summary: 'Prior ICR',
  le_kodex_extraction: 'LE / Kodex',
  rfi_user_communication: 'RFI / Comms',
  case_intake_extraction: 'Case Intake',
  osint_results: 'OSINT',
  investigator_notes: 'Notes',
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
