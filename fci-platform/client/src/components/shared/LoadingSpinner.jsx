export default function LoadingSpinner({ size = 'md', className = '' }) {
  const sizeClasses = {
    sm: 'h-4 w-4 border-2',
    md: 'h-6 w-6 border-2',
    lg: 'h-10 w-10 border-3',
  };

  return (
    <div
      className={`animate-spin rounded-full border-surface-300 dark:border-surface-600 border-t-gold-500 ${sizeClasses[size]} ${className}`}
    />
  );
}
