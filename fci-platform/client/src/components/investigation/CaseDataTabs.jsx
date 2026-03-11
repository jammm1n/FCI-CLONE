const TAB_GROUPS = [
  {
    id: 'c360',
    label: 'C360',
    tabs: [
      { key: 'tx_summary', label: 'Transactions' },
      { key: 'user_profile', label: 'User Profile' },
      { key: 'privacy_coin', label: 'Privacy Coin' },
      { key: 'counterparty', label: 'Counterparty' },
      { key: 'device_ip', label: 'Device / IP' },
      { key: 'failed_fiat', label: 'Failed Fiat' },
      { key: 'ctm_alerts', label: 'CTM Alerts' },
      { key: 'ftm_alerts', label: 'FTM Alerts' },
      { key: 'account_blocks', label: 'Blocks' },
      { key: 'address_xref', label: 'Address Xref' },
      { key: 'uid_search', label: 'UID Search' },
      { key: 'elliptic_addresses', label: 'Addresses' },
    ],
  },
  { id: 'elliptic', label: 'Elliptic', tabs: [{ key: 'elliptic', label: 'Elliptic' }] },
  { id: 'l1_referral', label: 'L1 Referral', tabs: [{ key: 'l1_referral', label: 'L1 Referral' }] },
  { id: 'haoDesk', label: 'HaoDesk', tabs: [{ key: 'haoDesk', label: 'HaoDesk' }] },
  { id: 'kyc', label: 'KYC', tabs: [{ key: 'kyc', label: 'KYC' }] },
  { id: 'prior_icr', label: 'Prior ICR', tabs: [{ key: 'prior_icr', label: 'Prior ICR' }] },
  { id: 'rfi', label: 'RFI', tabs: [{ key: 'rfi', label: 'RFI' }] },
  { id: 'kodex', label: 'LE / Kodex', tabs: [{ key: 'kodex', label: 'LE / Kodex' }] },
  { id: 'l1_victim', label: 'L1 Victim', tabs: [{ key: 'l1_victim', label: 'L1 Victim' }] },
  { id: 'l1_suspect', label: 'L1 Suspect', tabs: [{ key: 'l1_suspect', label: 'L1 Suspect' }] },
  { id: 'notes', label: 'Notes & OSINT', tabs: [{ key: 'investigator_notes', label: 'Notes & OSINT' }] },
];

export default function CaseDataTabs({
  preprocessedData,
  activeGroup,
  activeSubTab,
  onGroupChange,
  onSubTabChange,
}) {
  // Filter to groups that have at least one sub-tab with data
  const availableGroups = TAB_GROUPS.filter((group) =>
    group.tabs.some((tab) => preprocessedData[tab.key])
  );

  if (availableGroups.length === 0) return null;

  const currentGroup = availableGroups.find((g) => g.id === activeGroup);
  const showSubTabs =
    currentGroup && currentGroup.tabs.length > 1 &&
    currentGroup.tabs.filter((t) => preprocessedData[t.key]).length > 1;

  return (
    <div className="shrink-0">
      {/* Top-level group tabs */}
      <div className="flex gap-0 border-b border-surface-200 dark:border-surface-700 bg-surface-50 dark:bg-surface-800 px-4 overflow-x-auto">
        {availableGroups.map((group) => (
          <button
            key={group.id}
            onClick={() => onGroupChange(group.id)}
            className={`px-4 py-3 text-sm font-medium whitespace-nowrap border-b-[3px] rounded-t-lg ${
              activeGroup === group.id
                ? 'border-gold-500 text-gold-600 dark:text-gold-500'
                : 'border-transparent text-surface-500 dark:text-surface-400 hover:text-gold-400 hover:bg-surface-100 dark:hover:bg-surface-700/50'
            }`}
          >
            {group.label}
          </button>
        ))}
      </div>

      {/* Sub-tabs for multi-tab groups (C360) */}
      {showSubTabs && (
        <div className="flex gap-0 border-b border-surface-200 dark:border-surface-700 bg-surface-100/50 dark:bg-surface-850 px-4 overflow-x-auto">
          {currentGroup.tabs
            .filter((tab) => preprocessedData[tab.key])
            .map((tab) => (
              <button
                key={tab.key}
                onClick={() => onSubTabChange(tab.key)}
                className={`px-3 py-2 text-xs font-medium whitespace-nowrap border-b-2 ${
                  activeSubTab === tab.key
                    ? 'border-gold-400 text-gold-500 dark:text-gold-400'
                    : 'border-transparent text-surface-400 dark:text-surface-500 hover:text-gold-400'
                }`}
              >
                {tab.label}
              </button>
            ))}
        </div>
      )}
    </div>
  );
}

export { TAB_GROUPS };
