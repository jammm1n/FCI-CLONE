const PHASE_LABELS = {
  setup: 'Setup',
  analysis: 'Analysis',
  decision: 'Decision',
  post: 'Post-Decision',
  qc_check: 'QC Check',
};

export default function StepIndicator({ currentStep, phase }) {
  if (!currentStep) return null;

  const label = PHASE_LABELS[phase] || phase;

  return (
    <div className="flex items-center gap-2.5">
      {/* Step dots */}
      <div className="flex items-center gap-1">
        {[1, 2, 3, 4, 5].map((s) => (
          <div
            key={s}
            className={`w-1.5 h-1.5 rounded-full transition-colors ${
              s < currentStep
                ? 'bg-gold-500'
                : s === currentStep
                  ? 'bg-gold-400 ring-2 ring-gold-500/30'
                  : 'bg-surface-300 dark:bg-surface-600'
            }`}
          />
        ))}
      </div>
      <span className="text-sm font-medium text-surface-600 dark:text-surface-400">
        Step {currentStep} of 5: <span className="text-gold-600 dark:text-gold-400">{label}</span>
      </span>
    </div>
  );
}
