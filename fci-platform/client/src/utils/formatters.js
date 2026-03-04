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
  if (count == null) return '\u2014';
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
 * Badge base classes (shared).
 */
const BADGE_BASE = 'inline-flex items-center px-2.5 py-1 rounded-full text-sm font-medium';

/**
 * Map status to badge colour classes (ring-based, Binance palette).
 */
export function statusColor(status) {
  switch (status) {
    case 'open':
      return `${BADGE_BASE} bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 ring-1 ring-emerald-500/20`;
    case 'in_progress':
      return `${BADGE_BASE} bg-gold-500/10 text-gold-700 dark:text-gold-500 ring-1 ring-gold-500/20`;
    case 'completed':
    case 'closed':
      return `${BADGE_BASE} bg-surface-500/10 text-surface-600 dark:text-surface-400 ring-1 ring-surface-500/20`;
    case 'escalated':
      return `${BADGE_BASE} bg-red-500/10 text-red-700 dark:text-red-400 ring-1 ring-red-500/20`;
    default:
      return `${BADGE_BASE} bg-surface-500/10 text-surface-600 dark:text-surface-400 ring-1 ring-surface-500/20`;
  }
}

/**
 * Map case type to badge colour classes (ring-based).
 */
export function caseTypeColor(caseType) {
  switch (caseType) {
    case 'scam':
      return `${BADGE_BASE} bg-red-500/10 text-red-700 dark:text-red-400 ring-1 ring-red-500/20`;
    case 'ctm':
      return `${BADGE_BASE} bg-amber-500/10 text-amber-700 dark:text-amber-400 ring-1 ring-amber-500/20`;
    case 'ftm':
      return `${BADGE_BASE} bg-blue-500/10 text-blue-700 dark:text-blue-400 ring-1 ring-blue-500/20`;
    case 'fraud':
      return `${BADGE_BASE} bg-purple-500/10 text-purple-700 dark:text-purple-400 ring-1 ring-purple-500/20`;
    default:
      return `${BADGE_BASE} bg-surface-500/10 text-surface-600 dark:text-surface-400 ring-1 ring-surface-500/20`;
  }
}
