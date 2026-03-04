/**
 * Format an ISO timestamp to a readable date/time string.
 */
export function formatTimestamp(isoString) {
  if (!isoString) return '';
  const d = new Date(isoString);
  return d.toLocaleString('en-GB', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

/**
 * Format token counts for display.
 */
export function formatTokens(count) {
  if (count == null) return '—';
  if (count >= 1000) return `${(count / 1000).toFixed(1)}K`;
  return String(count);
}

/**
 * Capitalise first letter.
 */
export function capitalize(str) {
  if (!str) return '';
  return str.charAt(0).toUpperCase() + str.slice(1);
}

/**
 * Map status to display colour class.
 */
export function statusColor(status) {
  switch (status) {
    case 'open':
      return 'bg-yellow-600/20 text-yellow-400';
    case 'in_progress':
      return 'bg-blue-600/20 text-blue-400';
    case 'completed':
      return 'bg-green-600/20 text-green-400';
    default:
      return 'bg-surface-600/20 text-surface-400';
  }
}

/**
 * Map case type to display colour class.
 */
export function caseTypeColor(caseType) {
  switch (caseType) {
    case 'scam':
      return 'bg-red-600/20 text-red-400';
    case 'ctm':
      return 'bg-orange-600/20 text-orange-400';
    case 'ftm':
      return 'bg-purple-600/20 text-purple-400';
    case 'fraud':
      return 'bg-pink-600/20 text-pink-400';
    default:
      return 'bg-surface-600/20 text-surface-400';
  }
}
