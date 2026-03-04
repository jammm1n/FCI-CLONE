export default function Skeleton({ className = '' }) {
  return <div className={`rounded-lg bg-surface-200 dark:bg-surface-700 animate-shimmer ${className}`} />;
}
