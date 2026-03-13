import { useState, useCallback } from 'react';
import { useAuth } from '../../context/AuthContext';
import { submitKBFeedback } from '../../services/api';

export default function SubmitFeedbackButton({ conversationId, disabled, alreadySubmitted }) {
  const [submitted, setSubmitted] = useState(false);
  const { token } = useAuth();

  const done = alreadySubmitted || submitted;

  const handleClick = useCallback(() => {
    if (done || !conversationId) return;
    // Fire-and-forget with keepalive — survives page navigation
    submitKBFeedback(token, conversationId);
    setSubmitted(true);
  }, [token, conversationId, done]);

  const isDisabled = disabled || !conversationId || done;

  const title = done
    ? 'Feedback submitted'
    : 'Submit this conversation for quality analysis';

  const label = done ? 'Submitted' : 'Feedback';

  return (
    <button
      onClick={handleClick}
      disabled={isDisabled}
      title={title}
      className={`flex items-center gap-1.5 px-2.5 h-8 rounded-lg transition-colors duration-200 ${
        done
          ? 'text-emerald-500 cursor-not-allowed'
          : isDisabled
            ? 'text-surface-400 dark:text-surface-600 cursor-not-allowed'
            : 'text-surface-500 dark:text-surface-400 hover:text-gold-500 dark:hover:text-gold-500 hover:bg-surface-100 dark:hover:bg-surface-700'
      }`}
    >
      {done ? (
        <svg className="w-3.5 h-3.5 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
          <polyline points="20 6 9 17 4 12" />
        </svg>
      ) : (
        <svg className="w-3.5 h-3.5 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M9 18h6" />
          <path d="M10 22h4" />
          <path d="M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z" />
        </svg>
      )}
      <span className="text-xs font-medium">{label}</span>
    </button>
  );
}
