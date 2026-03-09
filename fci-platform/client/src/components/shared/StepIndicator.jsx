const PHASE_LABELS = {
  setup: 'Setup',
  analysis: 'Analysis',
  decision: 'Decision',
  post: 'Post-Decision',
  qc_check: 'QC Check',
};

export default function StepIndicator({ currentStep, phase, totalSteps = 5, stepLabel }) {
  if (!currentStep) return null;

  const label = stepLabel || PHASE_LABELS[phase] || phase;
  const total = totalSteps || 5;
  const dots = Array.from({ length: total }, (_, i) => i + 1);
  const blockWord = total > 5 ? 'Block' : 'Step';

  return (
    <div className="flex items-center gap-2.5">
      {/* Step dots */}
      <div className="flex items-center gap-1">
        {dots.map((s) => (
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
        {blockWord} {currentStep} of {total}: <span className="text-gold-600 dark:text-gold-400">{label}</span>
      </span>
    </div>
  );
}
