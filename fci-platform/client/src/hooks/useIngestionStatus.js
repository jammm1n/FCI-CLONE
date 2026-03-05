import { useEffect, useRef, useCallback, useState } from 'react';
import { getCaseStatus } from '../services/ingestion_api';

/**
 * Polls the lightweight /status endpoint while any section is processing.
 * Stops polling when all sections are terminal or on unmount.
 *
 * @param {string} token - Auth token
 * @param {string|null} caseId - Case ID to poll, or null to disable
 * @param {function} onUpdate - Called with the status response on each poll
 * @param {number} intervalMs - Polling interval (default 2500ms)
 */
export default function useIngestionStatus(token, caseId, onUpdate, intervalMs = 2500) {
  const [polling, setPolling] = useState(false);
  const timerRef = useRef(null);
  const mountedRef = useRef(true);

  const startPolling = useCallback(() => setPolling(true), []);
  const stopPolling = useCallback(() => setPolling(false), []);

  useEffect(() => {
    mountedRef.current = true;
    return () => { mountedRef.current = false; };
  }, []);

  useEffect(() => {
    if (!polling || !caseId || !token) {
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
      return;
    }

    async function poll() {
      try {
        const status = await getCaseStatus(token, caseId);
        if (!mountedRef.current) return;
        onUpdate(status);

        // Auto-stop when nothing is processing
        const sections = status.sections || {};
        const anyProcessing = Object.values(sections).some(
          (s) => s.status === 'processing'
        );
        if (!anyProcessing) {
          setPolling(false);
        }
      } catch (err) {
        // Silently continue polling on transient errors
        console.warn('Status poll failed:', err.message);
      }
    }

    // Poll immediately, then on interval
    poll();
    timerRef.current = setInterval(poll, intervalMs);

    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
    };
  }, [polling, caseId, token, onUpdate, intervalMs]);

  return { polling, startPolling, stopPolling };
}
