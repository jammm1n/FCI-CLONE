import { useEffect, useState, useCallback, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import AppLayout from '../components/AppLayout';
import LoadingSpinner from '../components/shared/LoadingSpinner';
import useIngestionStatus from '../hooks/useIngestionStatus';
import * as ingestionApi from '../services/ingestion_api';
import { getMarkdownFromPaste } from '../utils/pasteMarkdown';

// ── Section Key Labels ───────────────────────────────────────────

const SECTION_LABELS = {
  c360: 'C360 Data Processing',
  elliptic: 'Elliptic Wallet Screening',
  hexa_dump: 'L1 Referral Narrative',
  raw_hex_dump: 'HaoDesk Case Data',
  kyc: 'KYC Document Summary',
  previous_icrs: 'Prior ICR Summary',
  rfis: 'RFI Summary',
  kodex: 'Law Enforcement / Kodex',
  l1_victim: 'L1 Victim Communications',
  l1_suspect: 'L1 Suspect Communications',
  investigator_notes: 'Investigator Notes & OSINT',
};


// ── Status Indicator ─────────────────────────────────────────────

function StatusDot({ status }) {
  const config = {
    empty: { color: 'bg-surface-500', label: 'Empty' },
    downloading: { color: 'bg-blue-400 animate-pulse', label: 'Downloading' },
    processing: { color: 'bg-gold-400 animate-pulse', label: 'Processing' },
    complete: { color: 'bg-emerald-500', label: 'Complete' },
    extracted: { color: 'bg-blue-500', label: 'Extracted' },
    error: { color: 'bg-red-500', label: 'Error' },
    none: { color: 'bg-surface-400', label: 'N/A' },
  };
  const c = config[status] || config.empty;
  return (
    <span className="inline-flex items-center gap-1.5 text-xs text-surface-400">
      <span className={`w-2 h-2 rounded-full ${c.color}`} />
      {c.label}
    </span>
  );
}

// ── Preview Modal (simple — used for non-C360 sections) ─────────

function PreviewModal({ title, content, onClose }) {
  const [copied, setCopied] = useState(false);

  function handleCopy() {
    navigator.clipboard.writeText(content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  useEffect(() => {
    function handleKey(e) {
      if (e.key === 'Escape') onClose();
    }
    window.addEventListener('keydown', handleKey);
    return () => window.removeEventListener('keydown', handleKey);
  }, [onClose]);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60" onClick={onClose}>
      <div
        className="bg-white dark:bg-surface-800 rounded-2xl w-[90%] max-w-4xl max-h-[85vh] flex flex-col border border-surface-200 dark:border-surface-700 shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between p-4 border-b border-surface-200 dark:border-surface-700">
          <h3 className="text-lg font-semibold text-surface-900 dark:text-surface-100">
            {title}
          </h3>
          <div className="flex items-center gap-2">
            <button
              onClick={handleCopy}
              className="px-3 py-1.5 rounded-lg text-xs font-medium border border-surface-300 dark:border-surface-600 text-surface-600 dark:text-surface-300 hover:bg-surface-100 dark:hover:bg-surface-700 transition-colors"
            >
              {copied ? 'Copied!' : 'Copy'}
            </button>
            <button
              onClick={onClose}
              className="w-8 h-8 rounded-lg hover:bg-surface-100 dark:hover:bg-surface-700 flex items-center justify-center text-surface-500"
            >
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-5 h-5">
                <path d="M6.28 5.22a.75.75 0 0 0-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 1 0 1.06 1.06L10 11.06l3.72 3.72a.75.75 0 1 0 1.06-1.06L11.06 10l3.72-3.72a.75.75 0 0 0-1.06-1.06L10 8.94 6.28 5.22Z" />
              </svg>
            </button>
          </div>
        </div>
        <div className="flex-1 overflow-y-auto p-4">
          <pre className="whitespace-pre-wrap text-sm text-surface-800 dark:text-surface-200 font-mono leading-relaxed">
            {content || 'No output available.'}
          </pre>
        </div>
      </div>
    </div>
  );
}

// ── C360 Per-Processor Preview Modal ────────────────────────────

const PROCESSOR_LABELS = {
  tx_summary: 'Transaction Summary',
  user_profile: 'User Profile',
  privacy_coin: 'Privacy Coin Breakdown',
  counterparty: 'Counterparty Analysis',
  device: 'Device & IP Analysis',
  elliptic: 'Wallet Address Extraction',
  fiat: 'Failed Fiat Withdrawals',
  ctm: 'CTM Alerts',
  ftm: 'FTM Alerts',
  blocks: 'Account Blocks',
};

const PROCESSOR_ORDER = [
  'tx_summary', 'user_profile', 'privacy_coin', 'counterparty',
  'device', 'fiat', 'ctm', 'ftm', 'blocks',
];

// Processors that go through AI (excludes user_profile and elliptic)
const AI_PROCESSORS = new Set([
  'tx_summary', 'blocks', 'ctm', 'privacy_coin', 'fiat',
  'counterparty', 'device', 'ftm',
]);

function ProcessorSection({ processorId, processorOutputs, aiOutputs }) {
  const [showRaw, setShowRaw] = useState(false);

  const po = processorOutputs[processorId] || {};
  const ai = aiOutputs[processorId] || {};
  const label = po.label || PROCESSOR_LABELS[processorId] || processorId;
  const hasAI = AI_PROCESSORS.has(processorId);

  // Determine what to show
  const aiOutput = ai.ai_output || null;
  const rawOutput = po.content || null;
  const skipped = po.skipped || ai.skipped;
  const hasError = ai.error && !ai.ai_output;

  // Status indicator
  let statusText = '';
  let statusColor = '';
  if (skipped) {
    statusText = 'No data';
    statusColor = 'text-surface-400';
  } else if (hasError) {
    statusText = 'AI error';
    statusColor = 'text-red-400';
  } else if (aiOutput) {
    statusText = 'AI processed';
    statusColor = 'text-emerald-400';
  } else if (!hasAI && rawOutput) {
    statusText = 'Raw (no AI)';
    statusColor = 'text-surface-400';
  } else if (rawOutput) {
    statusText = 'Raw fallback';
    statusColor = 'text-amber-400';
  }

  return (
    <div className="border border-surface-200 dark:border-surface-700 rounded-lg overflow-hidden">
      <div className="flex items-center justify-between px-4 py-2.5 bg-surface-100 dark:bg-surface-750">
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium text-surface-800 dark:text-surface-200">{label}</span>
          <span className={`text-[10px] ${statusColor}`}>{statusText}</span>
        </div>
        {rawOutput && hasAI && (
          <button
            onClick={() => setShowRaw(!showRaw)}
            className="text-[10px] px-2 py-0.5 rounded border border-surface-300 dark:border-surface-600 text-surface-500 hover:text-surface-700 dark:hover:text-surface-300 transition-colors"
          >
            {showRaw ? 'Show AI' : 'Show Raw'}
          </button>
        )}
      </div>
      <div className="px-4 py-3">
        {skipped && !rawOutput && (
          <p className="text-sm text-surface-400 italic">Data was not uploaded for this section.</p>
        )}
        {hasError && (
          <p className="text-xs text-red-400 mb-2">AI processing error: {ai.error}</p>
        )}
        {showRaw && rawOutput ? (
          <pre className="whitespace-pre-wrap text-sm text-surface-600 dark:text-surface-400 font-mono leading-relaxed">
            {rawOutput}
          </pre>
        ) : aiOutput ? (
          <pre className="whitespace-pre-wrap text-sm text-surface-800 dark:text-surface-200 font-mono leading-relaxed">
            {aiOutput}
          </pre>
        ) : rawOutput ? (
          <pre className="whitespace-pre-wrap text-sm text-surface-600 dark:text-surface-400 font-mono leading-relaxed">
            {rawOutput}
          </pre>
        ) : null}
      </div>
    </div>
  );
}

function C360PreviewModal({ title, data, onClose }) {
  const [copied, setCopied] = useState(false);

  const processorOutputs = data.processor_outputs || {};
  const aiOutputs = data.ai_outputs || {};
  const fullOutput = data.output || '';

  function handleCopy() {
    navigator.clipboard.writeText(fullOutput);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  useEffect(() => {
    function handleKey(e) {
      if (e.key === 'Escape') onClose();
    }
    window.addEventListener('keydown', handleKey);
    return () => window.removeEventListener('keydown', handleKey);
  }, [onClose]);

  const hasPerProcessor = Object.keys(processorOutputs).length > 0 || Object.keys(aiOutputs).length > 0;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60" onClick={onClose}>
      <div
        className="bg-white dark:bg-surface-800 rounded-2xl w-[90%] max-w-5xl max-h-[85vh] flex flex-col border border-surface-200 dark:border-surface-700 shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between p-4 border-b border-surface-200 dark:border-surface-700">
          <h3 className="text-lg font-semibold text-surface-900 dark:text-surface-100">
            {title}
          </h3>
          <div className="flex items-center gap-2">
            <button
              onClick={handleCopy}
              className="px-3 py-1.5 rounded-lg text-xs font-medium border border-surface-300 dark:border-surface-600 text-surface-600 dark:text-surface-300 hover:bg-surface-100 dark:hover:bg-surface-700 transition-colors"
            >
              {copied ? 'Copied!' : 'Copy All'}
            </button>
            <button
              onClick={onClose}
              className="w-8 h-8 rounded-lg hover:bg-surface-100 dark:hover:bg-surface-700 flex items-center justify-center text-surface-500"
            >
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-5 h-5">
                <path d="M6.28 5.22a.75.75 0 0 0-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 1 0 1.06 1.06L10 11.06l3.72 3.72a.75.75 0 1 0 1.06-1.06L11.06 10l3.72-3.72a.75.75 0 0 0-1.06-1.06L10 8.94 6.28 5.22Z" />
              </svg>
            </button>
          </div>
        </div>
        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {hasPerProcessor ? (
            <>
              {PROCESSOR_ORDER.map((pid) => (
                <ProcessorSection
                  key={pid}
                  processorId={pid}
                  processorOutputs={processorOutputs}
                  aiOutputs={aiOutputs}
                />
              ))}
              {/* Address Cross-Reference */}
              {data.address_xref && (
                <div className="border border-surface-200 dark:border-surface-700 rounded-lg overflow-hidden">
                  <div className="px-4 py-2.5 bg-surface-100 dark:bg-surface-750">
                    <span className="text-sm font-medium text-surface-800 dark:text-surface-200">Address Cross-Reference</span>
                  </div>
                  <div className="px-4 py-3">
                    <pre className="whitespace-pre-wrap text-sm text-surface-800 dark:text-surface-200 font-mono leading-relaxed">
                      {data.address_xref}
                    </pre>
                  </div>
                </div>
              )}
              {/* UID Search */}
              {data.uid_search && (
                <div className="border border-surface-200 dark:border-surface-700 rounded-lg overflow-hidden">
                  <div className="px-4 py-2.5 bg-surface-100 dark:bg-surface-750">
                    <span className="text-sm font-medium text-surface-800 dark:text-surface-200">UID Search Results</span>
                  </div>
                  <div className="px-4 py-3">
                    <pre className="whitespace-pre-wrap text-sm text-surface-800 dark:text-surface-200 font-mono leading-relaxed">
                      {data.uid_search}
                    </pre>
                  </div>
                </div>
              )}
            </>
          ) : (
            <pre className="whitespace-pre-wrap text-sm text-surface-800 dark:text-surface-200 font-mono leading-relaxed">
              {fullOutput || 'No output available.'}
            </pre>
          )}
        </div>
      </div>
    </div>
  );
}

// ── Preview Button (simple — used for non-C360 sections) ────────

function PreviewButton({ token, caseId, sectionKey, label, subjectIndex }) {
  const [loading, setLoading] = useState(false);
  const [preview, setPreview] = useState(null);

  async function handleClick() {
    setLoading(true);
    try {
      const data = await ingestionApi.getSectionOutput(token, caseId, sectionKey, subjectIndex);
      setPreview(data.output || 'No output available.');
    } catch (err) {
      setPreview(`Error loading preview: ${err.message}`);
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <button
        onClick={handleClick}
        disabled={loading}
        title="Preview output"
        className="p-1 rounded hover:bg-surface-200 dark:hover:bg-surface-700 text-surface-400 hover:text-gold-500 transition-colors disabled:opacity-50"
      >
        {loading ? (
          <LoadingSpinner size="sm" />
        ) : (
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-4 h-4">
            <path d="M10 12.5a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5Z" />
            <path fillRule="evenodd" d="M.664 10.59a1.651 1.651 0 0 1 0-1.186A10.004 10.004 0 0 1 10 3c4.257 0 7.893 2.66 9.336 6.41.147.381.146.804 0 1.186A10.004 10.004 0 0 1 10 17c-4.257 0-7.893-2.66-9.336-6.41ZM14 10a4 4 0 1 1-8 0 4 4 0 0 1 8 0Z" clipRule="evenodd" />
          </svg>
        )}
      </button>
      {preview !== null && (
        <PreviewModal
          title={label}
          content={preview}
          onClose={() => setPreview(null)}
        />
      )}
    </>
  );
}

// ── C360 Preview Button (per-processor modal) ────────────────────

function C360PreviewButton({ token, caseId, label, subjectIndex }) {
  const [loading, setLoading] = useState(false);
  const [previewData, setPreviewData] = useState(null);

  async function handleClick() {
    setLoading(true);
    try {
      const data = await ingestionApi.getC360Output(token, caseId, subjectIndex);
      setPreviewData(data);
    } catch (err) {
      setPreviewData({ output: `Error loading preview: ${err.message}` });
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <button
        onClick={handleClick}
        disabled={loading}
        title="Preview output"
        className="p-1 rounded hover:bg-surface-200 dark:hover:bg-surface-700 text-surface-400 hover:text-gold-500 transition-colors disabled:opacity-50"
      >
        {loading ? (
          <LoadingSpinner size="sm" />
        ) : (
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-4 h-4">
            <path d="M10 12.5a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5Z" />
            <path fillRule="evenodd" d="M.664 10.59a1.651 1.651 0 0 1 0-1.186A10.004 10.004 0 0 1 10 3c4.257 0 7.893 2.66 9.336 6.41.147.381.146.804 0 1.186A10.004 10.004 0 0 1 10 17c-4.257 0-7.893-2.66-9.336-6.41ZM14 10a4 4 0 1 1-8 0 4 4 0 0 1 8 0Z" clipRule="evenodd" />
          </svg>
        )}
      </button>
      {previewData !== null && (
        <C360PreviewModal
          title={label}
          data={previewData}
          onClose={() => setPreviewData(null)}
        />
      )}
    </>
  );
}

// ── User Info Card ───────────────────────────────────────────────

function UserInfoCard({ userInfo, uid }) {
  if (!userInfo && !uid) return null;

  const fields = [];
  if (uid) fields.push(['User ID', uid]);
  if (userInfo) {
    if (userInfo.full_name) fields.push(['Name', userInfo.full_name]);
    if (userInfo.email) fields.push(['Email', userInfo.email]);
    if (userInfo.nationality) fields.push(['Nationality', userInfo.nationality]);
    if (userInfo.auth_type) fields.push(['Account Type', userInfo.auth_type]);
    if (userInfo.registration_time) fields.push(['Registered', userInfo.registration_time]);
    if (userInfo.status) fields.push(['Status', userInfo.status]);
  }

  if (fields.length === 0) return null;

  return (
    <div className="rounded-lg bg-surface-200/50 dark:bg-surface-700/50 border border-surface-300/50 dark:border-surface-600/50 p-3 space-y-1.5">
      {fields.map(([label, value]) => (
        <div key={label} className="flex items-baseline gap-2 text-xs">
          <span className="text-surface-500 dark:text-surface-400 min-w-[90px]">{label}</span>
          <span className={`font-mono ${label === 'User ID' ? 'text-gold-500 font-semibold text-sm' : 'text-surface-800 dark:text-surface-200'}`}>
            {value}
          </span>
        </div>
      ))}
    </div>
  );
}

// ── Case Creation Form ───────────────────────────────────────────

function CaseCreationForm({ onCreated }) {
  const { token } = useAuth();
  const [caseId, setCaseId] = useState('');
  const [caseMode, setCaseMode] = useState('single');
  const [totalSubjects, setTotalSubjects] = useState(2);
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState('');

  const isMulti = caseMode === 'multi';

  async function handleSubmit(e) {
    e.preventDefault();
    if (!caseId.trim()) return;
    setCreating(true);
    setError('');
    try {
      const opts = isMulti
        ? { caseMode: 'multi', totalSubjects }
        : {};
      const result = await ingestionApi.createCase(token, caseId.trim(), opts);
      onCreated(result);
    } catch (err) {
      if (err.data?.existing_case_id) {
        setError(`Active case exists: ${err.data.existing_case_id}`);
      } else {
        setError(err.message);
      }
    } finally {
      setCreating(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="bg-surface-100 dark:bg-surface-800 rounded-xl p-6 border border-surface-200 dark:border-surface-700">
      <h3 className="text-lg font-semibold text-surface-900 dark:text-surface-100 mb-4">Create New Case</h3>

      {/* Case Mode Toggle */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-surface-600 dark:text-surface-400 mb-2">
          Case Type
        </label>
        <div className="flex bg-surface-200 dark:bg-surface-900 rounded-lg p-0.5 w-fit">
          <button
            type="button"
            onClick={() => setCaseMode('single')}
            className={`px-4 py-1.5 rounded-md text-sm font-medium transition-colors ${
              !isMulti
                ? 'bg-gold-500 text-surface-900'
                : 'text-surface-500 hover:text-surface-700 dark:hover:text-surface-300'
            }`}
          >
            Single User
          </button>
          <button
            type="button"
            onClick={() => setCaseMode('multi')}
            className={`px-4 py-1.5 rounded-md text-sm font-medium transition-colors ${
              isMulti
                ? 'bg-gold-500 text-surface-900'
                : 'text-surface-500 hover:text-surface-700 dark:hover:text-surface-300'
            }`}
          >
            Multi-User
          </button>
        </div>
      </div>

      <div className="mb-4">
        <label className="block text-sm font-medium text-surface-600 dark:text-surface-400 mb-1">
          HowDesk Case Number
        </label>
        <input
          type="text"
          value={caseId}
          onChange={(e) => setCaseId(e.target.value)}
          placeholder="CASE-2026-0451"
          className="w-full max-w-sm px-3 py-2 rounded-lg bg-white dark:bg-surface-900 border border-surface-300 dark:border-surface-600 text-surface-900 dark:text-surface-100 placeholder-surface-400 focus:outline-none focus:ring-2 focus:ring-gold-500/50 focus:border-gold-500"
        />
      </div>

      {/* Subject count (multi-user only) */}
      {isMulti && (
        <div className="mb-4">
          <label className="block text-sm font-medium text-surface-600 dark:text-surface-400 mb-1">
            Total Subjects
          </label>
          <input
            type="number"
            min={2}
            value={totalSubjects}
            onChange={(e) => setTotalSubjects(Math.max(2, parseInt(e.target.value, 10) || 2))}
            className="w-20 px-3 py-2 rounded-lg bg-white dark:bg-surface-900 border border-surface-300 dark:border-surface-600 text-surface-900 dark:text-surface-100 text-sm text-center focus:outline-none focus:ring-2 focus:ring-gold-500/50 focus:border-gold-500"
          />
          <p className="text-xs text-surface-400 mt-1">
            Subjects are ingested one at a time, sequentially.
          </p>
        </div>
      )}

      {error && (
        <p className="text-sm text-red-500 dark:text-red-400 mb-3">{error}</p>
      )}
      <button
        type="submit"
        disabled={creating || !caseId.trim()}
        className="px-5 py-2 rounded-lg bg-gold-500 hover:bg-gold-600 text-surface-900 font-semibold text-sm transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {creating ? 'Creating...' : 'Create Case'}
      </button>
    </form>
  );
}

// ── C360 Download Progress ───────────────────────────────────────

function C360DownloadProgress({ c360 }) {
  const dp = c360.download_progress || {};
  const current = dp.current || 0;
  const total = dp.total || 26;
  const currentSheet = dp.current_sheet || '';
  const succeeded = dp.succeeded || 0;
  const failed = dp.failed || 0;

  return (
    <div className="space-y-2">
      <div className="flex items-center gap-2 text-sm text-blue-500 dark:text-blue-400">
        <LoadingSpinner size="sm" />
        Downloading C360 sheets ({succeeded}/{total})
      </div>
      {currentSheet && (
        <p className="text-xs text-surface-500 dark:text-surface-400 truncate">
          Downloading: {currentSheet}...
        </p>
      )}
      <div className="w-full h-1.5 bg-surface-200 dark:bg-surface-700 rounded-full overflow-hidden">
        <div
          className="h-full bg-blue-500 rounded-full transition-all duration-500"
          style={{ width: `${(current / total) * 100}%` }}
        />
      </div>
      {failed > 0 && (
        <p className="text-xs text-amber-500">
          {failed} sheet{failed !== 1 ? 's' : ''} failed (will continue with remaining)
        </p>
      )}
    </div>
  );
}

// ── C360 Processing Status ───────────────────────────────────────

function C360ProcessingStatus({ c360 }) {
  const aiStatus = c360.ai_status || 'pending';
  const aiProgress = c360.ai_progress || {};

  if (aiStatus === 'pending') {
    return (
      <div className="flex items-center gap-2 text-sm text-gold-500">
        <LoadingSpinner size="sm" />
        Processing C360 data...
      </div>
    );
  }

  // AI is processing — show per-processor progress
  const total = Object.keys(aiProgress).length;
  const done = Object.values(aiProgress).filter(
    (s) => s === 'complete' || s === 'skipped' || s === 'error'
  ).length;

  return (
    <div className="space-y-2">
      <div className="flex items-center gap-2 text-sm text-gold-500">
        <LoadingSpinner size="sm" />
        AI Processing{total > 0 ? ` (${done}/${total})` : '...'}
      </div>
      {total > 0 && (
        <div className="flex flex-wrap gap-1.5">
          {Object.entries(aiProgress).map(([pid, pstatus]) => {
            const label = PROCESSOR_LABELS[pid] || pid;
            let dotColor = 'bg-surface-500';
            if (pstatus === 'complete') dotColor = 'bg-emerald-500';
            else if (pstatus === 'processing') dotColor = 'bg-gold-400 animate-pulse';
            else if (pstatus === 'error') dotColor = 'bg-red-500';
            else if (pstatus === 'skipped') dotColor = 'bg-surface-400';
            return (
              <span
                key={pid}
                className="inline-flex items-center gap-1 text-[10px] text-surface-400 px-1.5 py-0.5 rounded bg-surface-200/50 dark:bg-surface-700/50"
              >
                <span className={`w-1.5 h-1.5 rounded-full ${dotColor}`} />
                {label}
              </span>
            );
          })}
        </div>
      )}
    </div>
  );
}

// ── C360 Upload Section ──────────────────────────────────────────

function C360Section({ caseData, onProcessingStarted, subjectIndex }) {
  const { token } = useAuth();
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const [dragging, setDragging] = useState(false);
  const fileInputRef = useRef(null);

  // Quick info returned synchronously from upload
  const [quickInfo, setQuickInfo] = useState(null);

  // Toggle between 'upload' and 'fetch' input modes
  const [inputMode, setInputMode] = useState('upload');

  // C360 auto-fetch fields
  const [fetchUid, setFetchUid] = useState(caseData.subject_uid || '');
  const [fetchCookie, setFetchCookie] = useState(() => sessionStorage.getItem('c360_cookie') || '');
  const [fetching, setFetching] = useState(false);

  const c360 = caseData.sections?.c360 || {};
  const status = c360.status || 'empty';

  // Reconstruct quick info from stored c360 data (for page reload during processing)
  const userInfo = quickInfo?.user_info || c360.user_info || null;
  const detectedUid = quickInfo?.file_uid || c360.detected_uid || caseData.subject_uid || '';

  function filterValidFiles(fileList) {
    return Array.from(fileList).filter((f) => {
      const name = f.name.toLowerCase();
      return name.endsWith('.xlsx') || name.endsWith('.xls') || name.endsWith('.csv');
    });
  }

  async function handleUpload() {
    if (!files.length) return;
    setUploading(true);
    setError('');
    try {
      const result = await ingestionApi.uploadC360(token, caseData.case_id, files, subjectIndex);
      // Store quick info from synchronous response
      setQuickInfo({
        file_uid: result.file_uid || '',
        user_info: result.user_info || null,
        detected_file_types: result.detected_file_types || [],
      });
      setFiles([]);
      if (fileInputRef.current) fileInputRef.current.value = '';
      onProcessingStarted();
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
    }
  }

  async function handleFetch() {
    if (!fetchUid.trim() || !fetchCookie.trim()) return;
    setFetching(true);
    setError('');
    try {
      await ingestionApi.fetchC360(token, caseData.case_id, fetchUid.trim(), fetchCookie.trim(), subjectIndex);
      sessionStorage.setItem('c360_cookie', fetchCookie.trim());
      onProcessingStarted();
    } catch (err) {
      setError(err.message);
    } finally {
      setFetching(false);
    }
  }

  function handleFileChange(e) {
    setFiles(filterValidFiles(e.target.files || []));
  }

  function handleDrop(e) {
    e.preventDefault();
    setDragging(false);
    const dropped = filterValidFiles(e.dataTransfer.files || []);
    if (dropped.length > 0) setFiles(dropped);
  }

  function handleDragOver(e) {
    e.preventDefault();
    setDragging(true);
  }

  function handleDragLeave(e) {
    e.preventDefault();
    setDragging(false);
  }

  // Shared input UI for empty and error states
  function renderInputUI() {
    return (
      <>
        {/* Mode toggle */}
        <div className="flex gap-1 mb-3 p-0.5 rounded-lg bg-surface-200 dark:bg-surface-700 w-fit">
          <button
            onClick={() => setInputMode('upload')}
            className={`px-3 py-1 rounded-md text-xs font-medium transition-colors ${
              inputMode === 'upload'
                ? 'bg-white dark:bg-surface-600 text-surface-900 dark:text-surface-100 shadow-sm'
                : 'text-surface-500 hover:text-surface-700 dark:hover:text-surface-300'
            }`}
          >
            Upload Files
          </button>
          <button
            onClick={() => setInputMode('fetch')}
            className={`px-3 py-1 rounded-md text-xs font-medium transition-colors ${
              inputMode === 'fetch'
                ? 'bg-white dark:bg-surface-600 text-surface-900 dark:text-surface-100 shadow-sm'
                : 'text-surface-500 hover:text-surface-700 dark:hover:text-surface-300'
            }`}
          >
            Fetch from C360
          </button>
        </div>

        {inputMode === 'upload' && (
          <>
            <div
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onClick={() => fileInputRef.current?.click()}
              className={`
                flex flex-col items-center justify-center gap-2 p-6 mb-3 rounded-lg border-2 border-dashed cursor-pointer transition-colors
                ${dragging
                  ? 'border-gold-500 bg-gold-500/10'
                  : 'border-surface-300 dark:border-surface-600 hover:border-gold-500/50 hover:bg-surface-200/50 dark:hover:bg-surface-700/50'
                }
              `}
            >
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-8 h-8 text-surface-400">
                <path d="M9.25 13.25a.75.75 0 0 0 1.5 0V4.636l2.955 3.129a.75.75 0 0 0 1.09-1.03l-4.25-4.5a.75.75 0 0 0-1.09 0l-4.25 4.5a.75.75 0 1 0 1.09 1.03L9.25 4.636v8.614Z" />
                <path d="M3.5 12.75a.75.75 0 0 0-1.5 0v2.5A2.75 2.75 0 0 0 4.75 18h10.5A2.75 2.75 0 0 0 18 15.25v-2.5a.75.75 0 0 0-1.5 0v2.5c0 .69-.56 1.25-1.25 1.25H4.75c-.69 0-1.25-.56-1.25-1.25v-2.5Z" />
              </svg>
              <p className="text-sm text-surface-500">
                {dragging ? 'Drop files here' : 'Drag & drop C360 spreadsheets here, or click to browse'}
              </p>
              <p className="text-xs text-surface-400">.xlsx, .xls, .csv</p>
              <input
                ref={fileInputRef}
                type="file"
                multiple
                accept=".xlsx,.xls,.csv"
                onChange={handleFileChange}
                className="hidden"
              />
            </div>
            {files.length > 0 && (
              <p className="text-sm text-surface-400 mb-3">
                {files.length} file{files.length !== 1 ? 's' : ''} selected: {files.map((f) => f.name).join(', ')}
              </p>
            )}
            <button
              onClick={handleUpload}
              disabled={uploading || !files.length}
              className="px-4 py-1.5 rounded-lg bg-gold-500 hover:bg-gold-600 text-surface-900 font-semibold text-sm transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {uploading ? 'Uploading...' : 'Upload & Process'}
            </button>
          </>
        )}

        {inputMode === 'fetch' && (
          <div className="space-y-3">
            <div>
              <label className="block text-xs font-medium text-surface-500 dark:text-surface-400 mb-1">
                User ID
              </label>
              <input
                type="text"
                value={fetchUid}
                onChange={(e) => setFetchUid(e.target.value)}
                placeholder="e.g. 466492707"
                className="w-full px-3 py-1.5 rounded-lg bg-white dark:bg-surface-700 border border-surface-300 dark:border-surface-600 text-sm text-surface-900 dark:text-surface-100 placeholder-surface-400 focus:outline-none focus:border-gold-500 focus:ring-1 focus:ring-gold-500"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-surface-500 dark:text-surface-400 mb-1">
                Session Cookie
              </label>
              <textarea
                value={fetchCookie}
                onChange={(e) => setFetchCookie(e.target.value)}
                placeholder="Paste the full Cookie header from your browser (Network tab)"
                rows={3}
                className="w-full px-3 py-1.5 rounded-lg bg-white dark:bg-surface-700 border border-surface-300 dark:border-surface-600 text-xs font-mono text-surface-900 dark:text-surface-100 placeholder-surface-400 focus:outline-none focus:border-gold-500 focus:ring-1 focus:ring-gold-500 resize-none"
              />
            </div>
            <button
              onClick={handleFetch}
              disabled={fetching || !fetchUid.trim() || !fetchCookie.trim()}
              className="px-4 py-1.5 rounded-lg bg-gold-500 hover:bg-gold-600 text-surface-900 font-semibold text-sm transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {fetching ? 'Starting...' : 'Fetch & Process'}
            </button>
          </div>
        )}

        {error && <p className="text-sm text-red-500 dark:text-red-400 mt-3">{error}</p>}
      </>
    );
  }

  return (
    <div className="bg-surface-100 dark:bg-surface-800 rounded-xl p-5 border border-surface-200 dark:border-surface-700">
      <div className="flex items-center justify-between mb-3">
        <h4 className="text-base font-semibold text-surface-900 dark:text-surface-100">
          {SECTION_LABELS.c360}
        </h4>
        <div className="flex items-center gap-2">
          {status === 'complete' && (
            <C360PreviewButton
              token={token}
              caseId={caseData.case_id}
              label={SECTION_LABELS.c360}
              subjectIndex={subjectIndex}
            />
          )}
          <StatusDot status={status} />
        </div>
      </div>

      {status === 'empty' && renderInputUI()}

      {status === 'downloading' && (
        <div className="space-y-3">
          <C360DownloadProgress c360={c360} />
        </div>
      )}

      {status === 'processing' && (
        <div className="space-y-3">
          <UserInfoCard userInfo={userInfo} uid={detectedUid} />
          {detectedUid && (
            <p className="text-sm text-surface-400 italic">
              Verify this is the correct user ID for the case you are investigating.
            </p>
          )}
          <C360ProcessingStatus c360={c360} />
        </div>
      )}

      {status === 'complete' && (
        <div className="space-y-3">
          <UserInfoCard userInfo={userInfo} uid={detectedUid} />
          {detectedUid && (
            <p className="text-sm text-surface-400 italic">
              Verify this is the correct user ID for the case you are investigating.
            </p>
          )}
          <p className="text-sm text-emerald-500 dark:text-emerald-400">
            Processing complete. {(c360.detected_file_types || []).length} file types detected.
          </p>
          {(c360.warnings || []).length > 0 && (
            <div className="text-sm text-amber-500 space-y-1">
              {c360.warnings.map((w, i) => (
                <p key={i}>{w.message}</p>
              ))}
            </div>
          )}
          <CsvDownloadButton caseId={caseData.case_id} filename={c360.csv_filename} subjectIndex={subjectIndex} />
        </div>
      )}

      {status === 'error' && (
        <div className="space-y-3">
          <p className="text-sm text-red-500 dark:text-red-400">
            {c360.error_message || 'Processing failed.'}
          </p>
          {renderInputUI()}
        </div>
      )}
    </div>
  );
}

// ── CSV Download Button ──────────────────────────────────────────

function CsvDownloadButton({ caseId, filename, subjectIndex }) {
  const { token } = useAuth();
  const [downloading, setDownloading] = useState(false);

  async function handleDownload() {
    setDownloading(true);
    try {
      const res = await fetch(ingestionApi.c360CsvUrl(caseId, subjectIndex), {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) throw new Error('Download failed');
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename || 'elliptic_screening.csv';
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error('CSV download failed:', err);
    } finally {
      setDownloading(false);
    }
  }

  return (
    <button
      onClick={handleDownload}
      disabled={downloading}
      className="inline-flex items-center gap-1.5 text-xs text-gold-500 hover:text-gold-400 transition-colors disabled:opacity-50"
    >
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" className="w-3.5 h-3.5">
        <path d="M2 8a.75.75 0 0 1 .75-.75h5.69L6.22 5.03a.75.75 0 0 1 1.06-1.06l3.5 3.5a.75.75 0 0 1 0 1.06l-3.5 3.5a.75.75 0 0 1-1.06-1.06l2.22-2.22H2.75A.75.75 0 0 1 2 8Z" />
        <path d="M14 12.25v-4.5a.75.75 0 0 0-1.5 0v4.5a.25.25 0 0 1-.25.25h-8.5a.25.25 0 0 1-.25-.25v-4.5a.75.75 0 0 0-1.5 0v4.5A1.75 1.75 0 0 0 3.75 14h8.5A1.75 1.75 0 0 0 14 12.25Z" />
      </svg>
      {downloading ? 'Downloading...' : 'Download Elliptic CSV'}
    </button>
  );
}

// ── Additional Inputs Section ─────────────────────────────────────

function UolUploadArea({ caseData, onSaved, subjectIndex }) {
  const { token } = useAuth();
  const hasUol = caseData.has_uol || false;
  const uolInfo = caseData.sections?.c360?.uol_info;

  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState(null);
  const [dragOver, setDragOver] = useState(false);
  const fileInputRef = useRef(null);

  async function handleFile(file) {
    if (!file) return;
    if (!file.name.toLowerCase().endsWith('.xlsx') && !file.name.toLowerCase().endsWith('.xls')) {
      setError('Only .xlsx files are accepted.');
      return;
    }
    setUploading(true);
    setError('');
    setResult(null);
    try {
      const res = await ingestionApi.uploadUol(token, caseData.case_id, file, subjectIndex);
      setResult(res);
      if (onSaved) onSaved();
    } catch (err) {
      setError(err.message || 'Upload failed');
    } finally {
      setUploading(false);
    }
  }

  function handleDrop(e) {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer?.files?.[0];
    if (file) handleFile(file);
  }

  function handleInputChange(e) {
    const file = e.target.files?.[0];
    if (file) handleFile(file);
    e.target.value = '';
  }

  // Show summary if UOL was uploaded (from backend or just now)
  const displayInfo = result?.uol_info || (hasUol ? uolInfo : null);

  return (
    <div className="mt-4 pt-4 border-t border-surface-200 dark:border-surface-700">
      <div className="flex items-center justify-between mb-2">
        <h5 className="text-sm font-semibold text-surface-900 dark:text-surface-200">
          UOL (User Operation Log)
        </h5>
        {(hasUol || result) && (
          <span className="text-xs text-emerald-500 font-medium">Uploaded</span>
        )}
      </div>

      {displayInfo ? (
        <div className="text-xs text-surface-400 space-y-0.5 mb-2">
          <p>Fiat withdrawals: {displayInfo.fiat_withdrawal_count ?? 0} ({displayInfo.fiat_withdrawal_failed ?? 0} failed)</p>
          <p>Crypto: {displayInfo.crypto_withdrawal_count ?? 0} withdrawals, {displayInfo.crypto_deposit_count ?? 0} deposits</p>
          <p>Binance Pay: {displayInfo.binance_pay_count ?? 0} | P2P: {displayInfo.p2p_count ?? 0}</p>
          {result?.xref_stats && (
            <p className="text-emerald-500">
              Address xref: {result.xref_stats.uol_matched ?? 0} matched / {result.xref_stats.total_addresses ?? 0} total
            </p>
          )}
        </div>
      ) : (
        <p className="text-xs text-surface-400 mb-2">
          Upload the UOL spreadsheet to enable address cross-referencing and failed fiat analysis.
        </p>
      )}

      {/* Upload area */}
      <div
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`flex items-center justify-center gap-2 px-3 py-2 rounded-lg border border-dashed cursor-pointer transition-colors text-xs ${
          dragOver
            ? 'border-gold-500 bg-gold-500/10 text-gold-400'
            : 'border-surface-300 dark:border-surface-600 text-surface-400 hover:border-gold-500/50 hover:text-surface-300'
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".xlsx,.xls"
          onChange={handleInputChange}
          className="hidden"
        />
        {uploading ? (
          <>
            <svg className="animate-spin h-3.5 w-3.5" viewBox="0 0 24 24" fill="none">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            <span>Uploading & processing...</span>
          </>
        ) : (
          <span>{hasUol || result ? 'Replace UOL file' : 'Drop UOL .xlsx here or click to browse'}</span>
        )}
      </div>

      {error && <p className="text-xs text-red-500 dark:text-red-400 mt-1">{error}</p>}
    </div>
  );
}

function AdditionalInputsSection({ caseData, onSaved, subjectIndex }) {
  const { token } = useAuth();
  const isMulti = caseData.case_mode === 'multi';

  const existingUids = isMulti ? [] : (caseData.coconspirator_uids || []);
  const existingWallets = caseData.sections?.elliptic?.manual_addresses || [];
  const hasSavedData = existingUids.length > 0 || existingWallets.length > 0;

  const [editing, setEditing] = useState(!hasSavedData);
  const [extraUids, setExtraUids] = useState(existingUids.join('\n'));
  const [extraWallets, setExtraWallets] = useState(existingWallets.join('\n'));
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [xrefStats, setXrefStats] = useState(null);

  const c360Complete = caseData.sections?.c360?.status === 'complete';
  if (!c360Complete) return null;

  // Check if UOL was already included in C360 upload (has uol_info on c360 section)
  const uolInC360 = !!caseData.sections?.c360?.uol_info;

  async function handleSave() {
    setSaving(true);
    setError('');
    setXrefStats(null);
    try {
      // Save extra UIDs (single-user only — multi-user uses subjects array)
      const uids = isMulti ? [] : extraUids.split('\n').map((u) => u.trim()).filter(Boolean);
      if (!isMulti) {
        await fetch(`/api/ingestion/cases/${caseData.case_id}/uids`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
          body: JSON.stringify({ coconspirator_uids: uids }),
        });
      }

      // Save extra wallets
      const wallets = extraWallets.split('\n').map((w) => w.trim()).filter(Boolean);
      await ingestionApi.addManualAddresses(token, caseData.case_id, wallets, subjectIndex);

      // Run address cross-reference (includes manual wallets vs UOL)
      const xrefResult = await ingestionApi.runAddressXref(token, caseData.case_id, subjectIndex);
      setXrefStats(xrefResult.stats || null);

      // Run UID search if UIDs were provided
      if (uids.length > 0) {
        await ingestionApi.runUidSearch(token, caseData.case_id, subjectIndex);
      }

      setEditing(false);
      if (onSaved) onSaved();
    } catch (err) {
      setError(err.message || 'Failed to save');
    } finally {
      setSaving(false);
    }
  }

  function handleSkip() {
    setEditing(false);
  }

  return (
    <div className="bg-surface-100 dark:bg-surface-800 rounded-xl p-5 border border-surface-200 dark:border-surface-700">
      <div className="flex items-center justify-between mb-3">
        <h4 className="text-base font-semibold text-surface-900 dark:text-surface-100">
          Additional Inputs
        </h4>
        {!editing && (
          <button
            onClick={() => setEditing(true)}
            className="text-xs text-gold-500 hover:text-gold-400 transition-colors"
          >
            Edit
          </button>
        )}
      </div>

      {!editing && (
        <div className="text-sm text-surface-400 space-y-1">
          <p>
            UIDs: {existingUids.length > 0 ? existingUids.join(', ') : 'None'}
          </p>
          <p>
            Extra wallets: {existingWallets.length > 0 ? `${existingWallets.length} address${existingWallets.length !== 1 ? 'es' : ''}` : 'None'}
          </p>
          {xrefStats && (
            <p className="text-emerald-500">
              Address xref: {xrefStats.uol_matched ?? 0} matched / {xrefStats.total_addresses ?? 0} total
            </p>
          )}
        </div>
      )}

      {editing && (
        <>
          <p className="text-sm text-surface-400 mb-4">
            Optional. Add any additional UIDs of interest (victims, co-suspects) and extra wallet addresses not in the C360 data.
          </p>

          <div className={`grid grid-cols-1 ${isMulti ? '' : 'sm:grid-cols-2'} gap-4 mb-4`}>
            {!isMulti && (
              <div>
                <label className="block text-sm font-medium text-surface-500 dark:text-surface-400 mb-1">
                  Additional UIDs (one per line)
                </label>
                <textarea
                  value={extraUids}
                  onChange={(e) => setExtraUids(e.target.value)}
                  placeholder="e.g. BIN-12345678"
                  rows={3}
                  className="w-full px-3 py-2 rounded-lg bg-white dark:bg-surface-900 border border-surface-300 dark:border-surface-600 text-surface-900 dark:text-surface-100 placeholder-surface-400 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-gold-500/50 focus:border-gold-500"
                />
              </div>
            )}
            <div>
              <label className="block text-sm font-medium text-surface-500 dark:text-surface-400 mb-1">
                Additional Wallets (one per line)
              </label>
              <textarea
                value={extraWallets}
                onChange={(e) => setExtraWallets(e.target.value)}
                placeholder="e.g. bc1qxy2k..."
                rows={3}
                className="w-full px-3 py-2 rounded-lg bg-white dark:bg-surface-900 border border-surface-300 dark:border-surface-600 text-surface-900 dark:text-surface-100 placeholder-surface-400 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-gold-500/50 focus:border-gold-500"
              />
            </div>
          </div>

          {error && <p className="text-sm text-red-500 dark:text-red-400 mb-3">{error}</p>}

          <div className="flex items-center gap-2">
            <button
              onClick={handleSave}
              disabled={saving}
              className="px-4 py-1.5 rounded-lg bg-gold-500 hover:bg-gold-600 text-surface-900 font-semibold text-sm transition-colors disabled:opacity-50"
            >
              {saving ? 'Saving...' : 'Save'}
            </button>
            <button
              onClick={handleSkip}
              className="px-4 py-1.5 rounded-lg border border-surface-300 dark:border-surface-600 text-surface-500 hover:text-surface-700 dark:hover:text-surface-300 text-sm transition-colors"
            >
              Skip
            </button>
          </div>
        </>
      )}

      {/* UOL Upload — shown when UOL wasn't part of the C360 upload */}
      {!uolInC360 && (
        <UolUploadArea
          caseData={caseData}
          onSaved={onSaved}
          subjectIndex={subjectIndex}
        />
      )}
    </div>
  );
}

// ── Elliptic Section ─────────────────────────────────────────────

function EllipticSection({ caseData, onProcessingStarted, subjectIndex }) {
  const { token } = useAuth();
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const c360 = caseData.sections?.c360 || {};
  const elliptic = caseData.sections?.elliptic || {};
  const ellStatus = elliptic.status || 'empty';
  const c360Complete = c360.status === 'complete';
  const walletCount = (c360.wallet_addresses || []).length + (elliptic.manual_addresses || []).length;

  async function handleSubmit() {
    setSubmitting(true);
    setError('');
    try {
      await ingestionApi.submitElliptic(token, caseData.case_id, subjectIndex);
      onProcessingStarted();
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  async function handleMarkNone() {
    try {
      await ingestionApi.markSectionNone(token, caseData.case_id, 'elliptic', subjectIndex);
      onProcessingStarted();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="bg-surface-100 dark:bg-surface-800 rounded-xl p-5 border border-surface-200 dark:border-surface-700">
      <div className="flex items-center justify-between mb-3">
        <h4 className="text-base font-semibold text-surface-900 dark:text-surface-100">
          {SECTION_LABELS.elliptic}
        </h4>
        <div className="flex items-center gap-2">
          {ellStatus === 'complete' && (
            <PreviewButton
              token={token}
              caseId={caseData.case_id}
              sectionKey="elliptic"
              label={SECTION_LABELS.elliptic}
              subjectIndex={subjectIndex}
            />
          )}
          <StatusDot status={ellStatus} />
        </div>
      </div>

      {!c360Complete && ellStatus === 'empty' && (
        <p className="text-xs text-surface-400">
          Upload C360 data first to extract wallet addresses.
        </p>
      )}

      {c360Complete && ellStatus === 'empty' && (
        <>
          <p className="text-sm text-surface-400 mb-3">
            {walletCount} wallet address{walletCount !== 1 ? 'es' : ''} ready for screening.
          </p>
          {error && <p className="text-sm text-red-500 dark:text-red-400 mb-3">{error}</p>}
          <div className="flex gap-2">
            <button
              onClick={handleSubmit}
              disabled={submitting || walletCount === 0}
              className="px-4 py-1.5 rounded-lg bg-gold-500 hover:bg-gold-600 text-surface-900 font-semibold text-sm transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {submitting ? 'Submitting...' : 'Submit to Elliptic'}
            </button>
            <button
              onClick={handleMarkNone}
              className="px-4 py-1.5 rounded-lg border border-surface-300 dark:border-surface-600 text-surface-500 hover:text-surface-700 dark:hover:text-surface-300 text-sm transition-colors"
            >
              Not Applicable
            </button>
          </div>
        </>
      )}

      {ellStatus === 'processing' && (
        <div className="flex items-center gap-2 text-sm text-gold-500">
          <LoadingSpinner size="sm" />
          Screening addresses via Elliptic API...
        </div>
      )}

      {ellStatus === 'complete' && (
        <p className="text-sm text-emerald-500 dark:text-emerald-400">
          Elliptic screening complete.
        </p>
      )}

      {ellStatus === 'none' && (
        <div className="flex items-center justify-between">
          <p className="text-xs text-surface-400">Marked as not applicable.</p>
          <button
            onClick={async () => {
              try {
                await ingestionApi.reopenSection(token, caseData.case_id, 'elliptic', subjectIndex);
                onProcessingStarted();
              } catch (err) {
                setError(err.message);
              }
            }}
            className="text-[10px] text-surface-400 hover:text-surface-600 dark:hover:text-surface-300 transition-colors"
          >
            Reopen
          </button>
        </div>
      )}

      {ellStatus === 'error' && (
        <div className="space-y-2">
          <p className="text-sm text-red-500 dark:text-red-400">
            {elliptic.error_message || 'Screening failed.'}
          </p>
          <div className="flex gap-2">
            <button
              onClick={handleSubmit}
              disabled={submitting}
              className="px-4 py-1.5 rounded-lg border border-amber-500/50 text-amber-500 hover:bg-amber-500/10 font-semibold text-sm transition-colors disabled:opacity-50"
            >
              {submitting ? 'Retrying...' : 'Retry'}
            </button>
            <button
              onClick={handleMarkNone}
              className="px-3 py-1.5 rounded-lg text-xs text-surface-400 hover:text-surface-600 dark:hover:text-surface-300 border border-surface-300 dark:border-surface-600 hover:bg-surface-200 dark:hover:bg-surface-700 transition-colors"
            >
              Mark N/A
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

// ── Notes Section ────────────────────────────────────────────────

function NotesSection({ caseData, onSaved, subjectIndex }) {
  const sectionKey = 'investigator_notes';
  const { token } = useAuth();
  const section = caseData.sections?.[sectionKey] || {};
  const [notes, setNotes] = useState(section.output || '');
  const [saving, setSaving] = useState(false);

  const status = section.status || 'empty';
  const isComplete = status === 'complete';
  const isNone = status === 'none';

  // Sync local state when section data changes (e.g., after reopen refreshes case)
  useEffect(() => {
    if (section.output && !isComplete) {
      setNotes(section.output);
    }
  }, [section.output, isComplete]);

  async function handleSave() {
    if (!notes.trim()) return;
    setSaving(true);
    try {
      await ingestionApi.saveNotes(token, caseData.case_id, notes, subjectIndex);
      if (onSaved) onSaved();
    } catch (err) {
      console.error('Failed to save notes:', err);
    } finally {
      setSaving(false);
    }
  }

  async function handleReopen() {
    try {
      await ingestionApi.reopenSection(token, caseData.case_id, sectionKey, subjectIndex);
      if (onSaved) onSaved();
    } catch (err) {
      console.error('Failed to reopen notes:', err);
    }
  }

  async function handleMarkNone() {
    try {
      await ingestionApi.markSectionNone(token, caseData.case_id, sectionKey, subjectIndex);
      if (onSaved) onSaved();
    } catch (err) {
      console.error('Failed to mark notes N/A:', err);
    }
  }

  if (isNone) {
    async function handleReopenNone() {
      try {
        await ingestionApi.reopenSection(token, caseData.case_id, sectionKey, subjectIndex);
        if (onSaved) onSaved();
      } catch (err) {
        console.error('Failed to reopen notes:', err);
      }
    }
    return (
      <div className="bg-surface-100/50 dark:bg-surface-800/50 rounded-xl p-5 border border-surface-200/50 dark:border-surface-700/50">
        <div className="flex items-center justify-between">
          <h4 className="text-base font-semibold text-surface-500 dark:text-surface-400">
            {SECTION_LABELS[sectionKey]}
          </h4>
          <div className="flex items-center gap-2">
            <button
              onClick={handleReopenNone}
              className="text-[10px] text-surface-400 hover:text-surface-600 dark:hover:text-surface-300 transition-colors"
            >
              Reopen
            </button>
            <StatusDot status="none" />
          </div>
        </div>
      </div>
    );
  }

  if (isComplete) {
    return (
      <div className="bg-surface-100 dark:bg-surface-800 rounded-xl p-5 border border-surface-200 dark:border-surface-700">
        <div className="flex items-center justify-between mb-3">
          <h4 className="text-base font-semibold text-surface-900 dark:text-surface-100">
            {SECTION_LABELS[sectionKey]}
          </h4>
          <StatusDot status="complete" />
        </div>
        <pre className="w-full px-3 py-2 rounded-lg bg-white dark:bg-surface-900 border border-surface-200 dark:border-surface-700 text-surface-700 dark:text-surface-300 text-sm whitespace-pre-wrap mb-3 opacity-70">
          {section.output}
        </pre>
        <button
          onClick={handleReopen}
          className="px-3 py-1.5 rounded-lg border border-surface-300 dark:border-surface-600 text-surface-700 dark:text-surface-300 hover:bg-surface-200 dark:hover:bg-surface-700 text-sm transition-colors"
        >
          Edit
        </button>
      </div>
    );
  }

  return (
    <div className="bg-surface-100 dark:bg-surface-800 rounded-xl p-5 border border-surface-200 dark:border-surface-700">
      <div className="flex items-center justify-between mb-3">
        <h4 className="text-base font-semibold text-surface-900 dark:text-surface-100">
          {SECTION_LABELS[sectionKey]}
        </h4>
        <StatusDot status={status} />
      </div>
      <textarea
        value={notes}
        onChange={(e) => setNotes(e.target.value)}
        placeholder="Add any investigator notes here..."
        rows={4}
        className="w-full px-3 py-2 rounded-lg bg-white dark:bg-surface-900 border border-surface-300 dark:border-surface-600 text-surface-900 dark:text-surface-100 placeholder-surface-400 text-sm focus:outline-none focus:ring-2 focus:ring-gold-500/50 focus:border-gold-500 mb-3"
      />
      <div className="flex items-center gap-3">
        <button
          onClick={handleSave}
          disabled={saving || !notes.trim()}
          className="px-4 py-1.5 rounded-lg bg-gold-500 hover:bg-gold-600 text-surface-900 font-semibold text-sm transition-colors disabled:opacity-50"
        >
          {saving ? 'Saving...' : 'Save Notes'}
        </button>
        {!notes.trim() && (
          <button
            onClick={handleMarkNone}
            className="px-3 py-1.5 rounded-lg text-xs text-surface-400 hover:text-surface-600 dark:hover:text-surface-300 border border-surface-300 dark:border-surface-600 hover:bg-surface-200 dark:hover:bg-surface-700 transition-colors"
          >
            No Data
          </button>
        )}
      </div>
    </div>
  );
}

// ── Text Section with AI Processing ──────────────────────────────

function TextAISection({ sectionKey, caseData, placeholder, onSaved, subjectIndex }) {
  const { token } = useAuth();
  const section = caseData.sections?.[sectionKey] || {};
  const [text, setText] = useState(section.raw_text || section.output || '');
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [showPreview, setShowPreview] = useState(false);
  const [previewData, setPreviewData] = useState(null);
  const [previewTab, setPreviewTab] = useState('ai');

  const status = section.status || 'empty';
  const aiStatus = section.ai_status;
  const isComplete = status === 'complete';
  const isNone = status === 'none';

  async function handleSave() {
    setSaving(true);
    setSaved(false);
    try {
      await ingestionApi.saveTextSection(token, caseData.case_id, sectionKey, text, subjectIndex);
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
      if (onSaved) onSaved();
    } catch (err) {
      console.error(`Failed to save ${sectionKey}:`, err);
    } finally {
      setSaving(false);
    }
  }

  async function handleReset() {
    try {
      await ingestionApi.saveTextSection(token, caseData.case_id, sectionKey, '', subjectIndex);
      setText('');
      if (onSaved) onSaved();
    } catch (err) {
      console.error(`Failed to reset ${sectionKey}:`, err);
    }
  }

  async function handlePreview() {
    try {
      const data = await ingestionApi.getTextSection(token, caseData.case_id, sectionKey, subjectIndex);
      setPreviewData(data);
      setPreviewTab('ai');
      setShowPreview(true);
    } catch (err) {
      console.error(`Failed to load preview for ${sectionKey}:`, err);
    }
  }

  async function handleMarkNone() {
    try {
      await ingestionApi.markSectionNone(token, caseData.case_id, sectionKey, subjectIndex);
      if (onSaved) onSaved();
    } catch (err) {
      console.error(`Failed to mark ${sectionKey} N/A:`, err);
    }
  }

  if (isNone) {
    async function handleReopen() {
      try {
        await ingestionApi.reopenSection(token, caseData.case_id, sectionKey, subjectIndex);
        if (onSaved) onSaved();
      } catch (err) {
        console.error(`Failed to reopen ${sectionKey}:`, err);
      }
    }
    return (
      <div className="bg-surface-100/50 dark:bg-surface-800/50 rounded-xl p-5 border border-surface-200/50 dark:border-surface-700/50">
        <div className="flex items-center justify-between">
          <h4 className="text-base font-semibold text-surface-500 dark:text-surface-400">
            {SECTION_LABELS[sectionKey]}
          </h4>
          <div className="flex items-center gap-2">
            <button
              onClick={handleReopen}
              className="text-[10px] text-surface-400 hover:text-surface-600 dark:hover:text-surface-300 transition-colors"
            >
              Reopen
            </button>
            <StatusDot status="none" />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-surface-100 dark:bg-surface-800 rounded-xl p-5 border border-surface-200 dark:border-surface-700">
      <div className="flex items-center justify-between mb-3">
        <h4 className="text-base font-semibold text-surface-900 dark:text-surface-100">
          {SECTION_LABELS[sectionKey]}
        </h4>
        <div className="flex items-center gap-2">
          {aiStatus && (
            <span className={`text-[10px] px-2 py-0.5 rounded-full ${
              aiStatus === 'complete' ? 'bg-emerald-500/20 text-emerald-400' :
              aiStatus === 'processing' ? 'bg-gold-500/20 text-gold-400' :
              aiStatus === 'error' ? 'bg-red-500/20 text-red-400' : ''
            }`}>
              {aiStatus === 'complete' ? 'AI processed' :
               aiStatus === 'processing' ? 'AI processing...' :
               aiStatus === 'error' ? 'AI failed (raw saved)' : ''}
            </span>
          )}
          <StatusDot status={status} />
        </div>
      </div>

      {/* Input area (hidden when complete) */}
      {!isComplete && (
        <>
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder={placeholder}
            rows={6}
            className="w-full px-3 py-2 rounded-lg bg-white dark:bg-surface-900 border border-surface-300 dark:border-surface-600 text-surface-900 dark:text-surface-100 placeholder-surface-400 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-gold-500/50 focus:border-gold-500 mb-3"
          />
          <div className="flex items-center gap-3">
            <button
              onClick={handleSave}
              disabled={saving}
              className="px-4 py-1.5 rounded-lg bg-gold-500 hover:bg-gold-600 text-surface-900 font-semibold text-sm transition-colors disabled:opacity-50"
            >
              {saving ? 'Saving & Processing...' : 'Save & Process'}
            </button>
            {saved && <span className="text-xs text-emerald-500">Saved</span>}
            {status === 'empty' && !text.trim() && (
              <button
                onClick={handleMarkNone}
                className="px-3 py-1.5 rounded-lg text-xs text-surface-400 hover:text-surface-600 dark:hover:text-surface-300 border border-surface-300 dark:border-surface-600 hover:bg-surface-200 dark:hover:bg-surface-700 transition-colors"
              >
                No Data
              </button>
            )}
          </div>
        </>
      )}

      {/* Actions when complete */}
      {isComplete && (
        <div className="flex items-center gap-3">
          <button
            onClick={handlePreview}
            className="px-3 py-1.5 rounded-lg border border-surface-300 dark:border-surface-600 text-surface-700 dark:text-surface-300 hover:bg-surface-200 dark:hover:bg-surface-700 text-sm transition-colors"
          >
            Preview
          </button>
          <button
            onClick={handleReset}
            className="px-3 py-1.5 rounded-lg border border-red-500/30 text-red-500 hover:bg-red-500/10 text-sm transition-colors"
          >
            Reset
          </button>
        </div>
      )}

      {showPreview && previewData && (
        <TextPreviewModal
          title={SECTION_LABELS[sectionKey]}
          data={previewData}
          activeTab={previewTab}
          onTabChange={setPreviewTab}
          onClose={() => setShowPreview(false)}
        />
      )}
    </div>
  );
}


// ── Text Section Preview Modal ──────────────────────────────────

function TextPreviewModal({ title, data, activeTab, onTabChange, onClose }) {
  const content = activeTab === 'ai' ? data.output : data.raw_text;
  const [copied, setCopied] = useState(false);

  function handleCopy() {
    if (content) {
      navigator.clipboard.writeText(content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
      <div className="bg-white dark:bg-surface-800 rounded-xl w-full max-w-3xl max-h-[80vh] flex flex-col border border-surface-200 dark:border-surface-700 shadow-2xl">
        <div className="flex items-center justify-between px-5 py-3 border-b border-surface-200 dark:border-surface-700">
          <h3 className="text-base font-semibold text-surface-900 dark:text-surface-100">{title}</h3>
          <div className="flex items-center gap-3">
            <div className="flex bg-surface-100 dark:bg-surface-900 rounded-lg p-0.5">
              <button
                onClick={() => onTabChange('ai')}
                className={`px-3 py-1 rounded-md text-xs font-medium transition-colors ${
                  activeTab === 'ai'
                    ? 'bg-gold-500 text-surface-900'
                    : 'text-surface-500 hover:text-surface-700 dark:hover:text-surface-300'
                }`}
              >
                AI Output
              </button>
              <button
                onClick={() => onTabChange('raw')}
                className={`px-3 py-1 rounded-md text-xs font-medium transition-colors ${
                  activeTab === 'raw'
                    ? 'bg-gold-500 text-surface-900'
                    : 'text-surface-500 hover:text-surface-700 dark:hover:text-surface-300'
                }`}
              >
                Raw Input
              </button>
            </div>
            <button onClick={handleCopy} className="text-xs text-surface-400 hover:text-surface-200 transition-colors">
              {copied ? 'Copied!' : 'Copy'}
            </button>
            <button onClick={onClose} className="text-surface-400 hover:text-surface-200 text-lg">&times;</button>
          </div>
        </div>
        <div className="flex-1 overflow-y-auto p-5">
          {data.ai_error && activeTab === 'ai' && (
            <div className="mb-3 text-xs text-red-400 bg-red-500/10 rounded-lg px-3 py-2">
              AI Error: {data.ai_error}
            </div>
          )}
          <pre className="text-sm text-surface-800 dark:text-surface-200 whitespace-pre-wrap font-mono leading-relaxed">
            {content || 'No content available.'}
          </pre>
        </div>
      </div>
    </div>
  );
}

// ── Iterative Entry Section (Prior ICR) ──────────────────────────

function IterativeEntrySection({ sectionKey, caseData, placeholder, onSaved, showTotalCount = false, subjectIndex }) {
  const { token } = useAuth();
  const section = caseData.sections?.[sectionKey] || {};
  const [text, setText] = useState('');
  const [adding, setAdding] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [showPreview, setShowPreview] = useState(false);
  const [previewData, setPreviewData] = useState(null);
  const [previewTab, setPreviewTab] = useState('ai');
  const [totalCount, setTotalCount] = useState(section.total_count ?? '');

  const entries = section.entries || [];
  const status = section.status || 'empty';
  const aiStatus = section.ai_status;
  const isComplete = status === 'complete';
  const isNone = status === 'none';

  // Sync totalCount from section data when it changes externally
  useEffect(() => {
    setTotalCount(section.total_count ?? '');
  }, [section.total_count]);

  async function handleMarkNone() {
    try {
      await ingestionApi.markSectionNone(token, caseData.case_id, sectionKey, subjectIndex);
      if (onSaved) onSaved();
    } catch (err) {
      console.error(`Failed to mark ${sectionKey} N/A:`, err);
    }
  }

  async function handleAddEntry() {
    if (!text.trim()) return;
    setAdding(true);
    try {
      await ingestionApi.addEntry(token, caseData.case_id, sectionKey, text, subjectIndex);
      setText('');
      if (onSaved) onSaved();
    } catch (err) {
      console.error(`Failed to add entry to ${sectionKey}:`, err);
    } finally {
      setAdding(false);
    }
  }

  async function handleRemoveEntry(entryId) {
    try {
      await ingestionApi.removeEntry(token, caseData.case_id, sectionKey, entryId, subjectIndex);
      if (onSaved) onSaved();
    } catch (err) {
      console.error(`Failed to remove entry:`, err);
    }
  }

  async function handleProcess() {
    setProcessing(true);
    try {
      if (text.trim()) {
        await ingestionApi.addEntry(token, caseData.case_id, sectionKey, text, subjectIndex);
      }
      await ingestionApi.processEntries(token, caseData.case_id, sectionKey, subjectIndex);
      setText('');
      if (onSaved) onSaved();
    } catch (err) {
      console.error(`Failed to process ${sectionKey}:`, err);
    } finally {
      setProcessing(false);
    }
  }

  async function handleReset() {
    try {
      // Remove all entries by clearing the section
      for (const entry of entries) {
        await ingestionApi.removeEntry(token, caseData.case_id, sectionKey, entry.id, subjectIndex);
      }
      setText('');
      if (onSaved) onSaved();
    } catch (err) {
      console.error(`Failed to reset ${sectionKey}:`, err);
    }
  }

  async function handlePreview() {
    try {
      const data = await ingestionApi.getEntries(token, caseData.case_id, sectionKey, subjectIndex);
      setPreviewData(data);
      setPreviewTab('ai');
      setShowPreview(true);
    } catch (err) {
      console.error(`Failed to load preview for ${sectionKey}:`, err);
    }
  }

  async function handleTotalCountBlur() {
    const parsed = totalCount === '' ? null : parseInt(totalCount, 10);
    if (parsed !== null && (isNaN(parsed) || parsed < 0)) return;
    try {
      await ingestionApi.setTotalCount(token, caseData.case_id, sectionKey, parsed, subjectIndex);
      if (onSaved) onSaved();
    } catch (err) {
      console.error(`Failed to save total count:`, err);
    }
  }

  if (isNone) {
    async function handleReopen() {
      try {
        await ingestionApi.reopenSection(token, caseData.case_id, sectionKey, subjectIndex);
        if (onSaved) onSaved();
      } catch (err) {
        console.error(`Failed to reopen ${sectionKey}:`, err);
      }
    }
    return (
      <div className="bg-surface-100/50 dark:bg-surface-800/50 rounded-xl p-5 border border-surface-200/50 dark:border-surface-700/50">
        <div className="flex items-center justify-between">
          <h4 className="text-base font-semibold text-surface-500 dark:text-surface-400">
            {SECTION_LABELS[sectionKey]}
          </h4>
          <div className="flex items-center gap-2">
            <button
              onClick={handleReopen}
              className="text-[10px] text-surface-400 hover:text-surface-600 dark:hover:text-surface-300 transition-colors"
            >
              Reopen
            </button>
            <StatusDot status="none" />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-surface-100 dark:bg-surface-800 rounded-xl p-5 border border-surface-200 dark:border-surface-700">
      <div className="flex items-center justify-between mb-3">
        <h4 className="text-base font-semibold text-surface-900 dark:text-surface-100">
          {SECTION_LABELS[sectionKey]}
        </h4>
        <div className="flex items-center gap-2">
          {aiStatus && (
            <span className={`text-[10px] px-2 py-0.5 rounded-full ${
              aiStatus === 'complete' ? 'bg-emerald-500/20 text-emerald-400' :
              aiStatus === 'processing' ? 'bg-gold-500/20 text-gold-400' :
              aiStatus === 'error' ? 'bg-red-500/20 text-red-400' : ''
            }`}>
              {aiStatus === 'complete' ? 'AI processed' :
               aiStatus === 'processing' ? 'AI processing...' :
               aiStatus === 'error' ? 'AI failed (raw saved)' : ''}
            </span>
          )}
          <StatusDot status={status === 'incomplete' ? 'empty' : status} />
        </div>
      </div>

      {/* Total count input (e.g. "10 prior ICRs exist, 2 included below") */}
      {showTotalCount && !isNone && (
        <div className="flex items-center gap-2 mb-3">
          <label className="text-xs text-surface-500 dark:text-surface-400 whitespace-nowrap">
            Total prior ICRs for subject:
          </label>
          <input
            type="number"
            min="0"
            value={totalCount}
            onChange={(e) => setTotalCount(e.target.value)}
            onBlur={handleTotalCountBlur}
            onKeyDown={(e) => e.key === 'Enter' && e.target.blur()}
            placeholder={String(entries.length || 0)}
            className="w-16 px-2 py-1 rounded-md bg-white dark:bg-surface-900 border border-surface-300 dark:border-surface-600 text-surface-900 dark:text-surface-100 text-sm text-center focus:outline-none focus:ring-2 focus:ring-gold-500/50 focus:border-gold-500"
          />
          {entries.length > 0 && totalCount && parseInt(totalCount, 10) > entries.length && (
            <span className="text-xs text-surface-400">
              ({entries.length} included below)
            </span>
          )}
        </div>
      )}

      {/* Existing entries */}
      {entries.length > 0 && (
        <div className={`space-y-2 mb-3 ${isComplete ? 'opacity-60' : ''}`}>
          {entries.map((entry, idx) => (
            <div
              key={entry.id}
              className="flex items-start gap-2 bg-white dark:bg-surface-900 rounded-lg p-3 border border-surface-200 dark:border-surface-700"
            >
              <span className="text-xs text-surface-400 font-mono mt-0.5 shrink-0">#{idx + 1}</span>
              <p className="text-sm text-surface-700 dark:text-surface-300 flex-1 line-clamp-3">
                {entry.text}
              </p>
              {!isComplete && (
                <button
                  onClick={() => handleRemoveEntry(entry.id)}
                  className="text-surface-400 hover:text-red-400 text-xs shrink-0 transition-colors"
                  title="Remove entry"
                >
                  &times;
                </button>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Add new entry (hidden when complete) */}
      {!isComplete && (
        <>
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder={placeholder}
            rows={4}
            className="w-full px-3 py-2 rounded-lg bg-white dark:bg-surface-900 border border-surface-300 dark:border-surface-600 text-surface-900 dark:text-surface-100 placeholder-surface-400 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-gold-500/50 focus:border-gold-500 mb-3"
          />
          <div className="flex items-center gap-3">
            <button
              onClick={handleAddEntry}
              disabled={adding || !text.trim()}
              className="px-4 py-1.5 rounded-lg border border-gold-500 text-gold-500 hover:bg-gold-500/10 font-semibold text-sm transition-colors disabled:opacity-50"
            >
              {adding ? 'Adding...' : 'Add Another'}
            </button>
            {(entries.length > 0 || text.trim()) && (
              <button
                onClick={handleProcess}
                disabled={processing || (entries.length === 0 && !text.trim())}
                className="px-4 py-1.5 rounded-lg bg-gold-500 hover:bg-gold-600 text-surface-900 font-semibold text-sm transition-colors disabled:opacity-50"
              >
                {processing ? 'Processing...' : `Done — Process All (${entries.length + (text.trim() ? 1 : 0)})`}
              </button>
            )}
            {entries.length === 0 && !text.trim() && (
              <button
                onClick={handleMarkNone}
                className="px-3 py-1.5 rounded-lg text-xs text-surface-400 hover:text-surface-600 dark:hover:text-surface-300 border border-surface-300 dark:border-surface-600 hover:bg-surface-200 dark:hover:bg-surface-700 transition-colors"
              >
                No Data
              </button>
            )}
            {aiStatus === 'error' && entries.length > 0 && (
              <button
                onClick={handleProcess}
                disabled={processing}
                className="px-4 py-1.5 rounded-lg border border-amber-500/50 text-amber-500 hover:bg-amber-500/10 font-semibold text-sm transition-colors disabled:opacity-50"
              >
                {processing ? 'Retrying...' : 'Retry Processing'}
              </button>
            )}
          </div>
        </>
      )}

      {/* Actions when complete */}
      {isComplete && (
        <div className="flex items-center gap-3">
          <button
            onClick={handlePreview}
            className="px-3 py-1.5 rounded-lg border border-surface-300 dark:border-surface-600 text-surface-700 dark:text-surface-300 hover:bg-surface-200 dark:hover:bg-surface-700 text-sm transition-colors"
          >
            Preview
          </button>
          <button
            onClick={handleReset}
            className="px-3 py-1.5 rounded-lg border border-red-500/30 text-red-500 hover:bg-red-500/10 text-sm transition-colors"
          >
            Reset
          </button>
        </div>
      )}

      {showPreview && previewData && (
        <TextPreviewModal
          title={SECTION_LABELS[sectionKey]}
          data={previewData}
          activeTab={previewTab}
          onTabChange={setPreviewTab}
          onClose={() => setShowPreview(false)}
        />
      )}
    </div>
  );
}


// ── RFI Entry Section (iterative entries with image support) ─────

function RFIEntrySection({ caseData, onSaved, showTotalCount = false, subjectIndex }) {
  const sectionKey = 'rfis';
  const { token } = useAuth();
  const section = caseData.sections?.[sectionKey] || {};
  const [text, setText] = useState('');
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [adding, setAdding] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [showPreview, setShowPreview] = useState(false);
  const [previewData, setPreviewData] = useState(null);
  const [previewTab, setPreviewTab] = useState('ai');
  const [totalCount, setTotalCount] = useState(section.total_count ?? '');

  useEffect(() => {
    setTotalCount(section.total_count ?? '');
  }, [section.total_count]);

  const entries = section.entries || [];
  const status = section.status || 'empty';
  const aiStatus = section.ai_status;
  const isComplete = status === 'complete';
  const isNone = status === 'none';

  const fileInputRef = useRef(null);

  async function handleMarkNone() {
    try {
      await ingestionApi.markSectionNone(token, caseData.case_id, sectionKey, subjectIndex);
      if (onSaved) onSaved();
    } catch (err) {
      console.error('Failed to mark RFIs N/A:', err);
    }
  }

  function handleFilesSelected(e) {
    const files = Array.from(e.target.files || []);
    setSelectedFiles((prev) => [...prev, ...files]);
    if (fileInputRef.current) fileInputRef.current.value = '';
  }

  function removeSelectedFile(idx) {
    setSelectedFiles((prev) => prev.filter((_, i) => i !== idx));
  }

  function addImageFiles(files) {
    const imageFiles = files.filter((f) => f.type.startsWith('image/'));
    if (imageFiles.length > 0) {
      setSelectedFiles((prev) => [...prev, ...imageFiles]);
    }
  }

  function handlePaste(e) {
    // HTML with tables/formatting → convert to Markdown and insert
    const markdown = getMarkdownFromPaste(e.clipboardData);
    if (markdown) {
      e.preventDefault();
      const ta = e.target;
      const start = ta.selectionStart;
      const end = ta.selectionEnd;
      setText((prev) => prev.substring(0, start) + markdown + prev.substring(end));
      requestAnimationFrame(() => {
        ta.selectionStart = ta.selectionEnd = start + markdown.length;
      });
      return;
    }

    const items = e.clipboardData?.items;
    if (!items) return;
    const imageFiles = [];
    for (const item of items) {
      if (item.type.startsWith('image/')) {
        const file = item.getAsFile();
        if (file) imageFiles.push(file);
      }
    }
    if (imageFiles.length > 0) {
      e.preventDefault();
      addImageFiles(imageFiles);
    }
  }

  function handleDrop(e) {
    e.preventDefault();
    setDragOver(false);
    const files = Array.from(e.dataTransfer?.files || []);
    addImageFiles(files);
  }

  const [dragOver, setDragOver] = useState(false);

  async function handleAddEntry() {
    if (!text.trim()) return;
    setAdding(true);
    try {
      await ingestionApi.addEntryWithImages(
        token, caseData.case_id, sectionKey, text, selectedFiles, subjectIndex,
      );
      setText('');
      setSelectedFiles([]);
      if (onSaved) onSaved();
    } catch (err) {
      console.error('Failed to add RFI entry:', err);
    } finally {
      setAdding(false);
    }
  }

  async function handleRemoveEntry(entryId) {
    try {
      await ingestionApi.removeEntry(token, caseData.case_id, sectionKey, entryId, subjectIndex);
      if (onSaved) onSaved();
    } catch (err) {
      console.error('Failed to remove entry:', err);
    }
  }

  async function handleProcess() {
    setProcessing(true);
    try {
      // Auto-add pending text+files before processing
      if (text.trim()) {
        await ingestionApi.addEntryWithImages(
          token, caseData.case_id, sectionKey, text, selectedFiles, subjectIndex,
        );
        setText('');
        setSelectedFiles([]);
      }
      await ingestionApi.processEntries(token, caseData.case_id, sectionKey, subjectIndex);
      if (onSaved) onSaved();
    } catch (err) {
      console.error('Failed to process RFIs:', err);
    } finally {
      setProcessing(false);
    }
  }

  async function handleReset() {
    try {
      for (const entry of entries) {
        await ingestionApi.removeEntry(token, caseData.case_id, sectionKey, entry.id, subjectIndex);
      }
      setText('');
      setSelectedFiles([]);
      if (onSaved) onSaved();
    } catch (err) {
      console.error('Failed to reset RFIs:', err);
    }
  }

  async function handlePreview() {
    try {
      const data = await ingestionApi.getEntries(token, caseData.case_id, sectionKey, subjectIndex);
      setPreviewData(data);
      setPreviewTab('ai');
      setShowPreview(true);
    } catch (err) {
      console.error('Failed to load preview:', err);
    }
  }

  if (isNone) {
    async function handleReopen() {
      try {
        await ingestionApi.reopenSection(token, caseData.case_id, sectionKey, subjectIndex);
        if (onSaved) onSaved();
      } catch (err) {
        console.error(`Failed to reopen ${sectionKey}:`, err);
      }
    }
    return (
      <div className="bg-surface-100/50 dark:bg-surface-800/50 rounded-xl p-5 border border-surface-200/50 dark:border-surface-700/50">
        <div className="flex items-center justify-between">
          <h4 className="text-base font-semibold text-surface-500 dark:text-surface-400">
            {SECTION_LABELS[sectionKey]}
          </h4>
          <div className="flex items-center gap-2">
            <button
              onClick={handleReopen}
              className="text-[10px] text-surface-400 hover:text-surface-600 dark:hover:text-surface-300 transition-colors"
            >
              Reopen
            </button>
            <StatusDot status="none" />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-surface-100 dark:bg-surface-800 rounded-xl p-5 border border-surface-200 dark:border-surface-700">
      <div className="flex items-center justify-between mb-3">
        <h4 className="text-base font-semibold text-surface-900 dark:text-surface-100">
          {SECTION_LABELS[sectionKey]}
        </h4>
        <div className="flex items-center gap-2">
          {aiStatus && (
            <span className={`text-[10px] px-2 py-0.5 rounded-full ${
              aiStatus === 'complete' ? 'bg-emerald-500/20 text-emerald-400' :
              aiStatus === 'processing' ? 'bg-gold-500/20 text-gold-400' :
              aiStatus === 'partial' ? 'bg-amber-500/20 text-amber-400' :
              aiStatus === 'error' ? 'bg-red-500/20 text-red-400' : ''
            }`}>
              {aiStatus === 'complete' ? 'AI processed' :
               aiStatus === 'processing' ? 'AI processing...' :
               aiStatus === 'partial' ? 'AI partial' :
               aiStatus === 'error' ? 'AI failed (raw saved)' : ''}
            </span>
          )}
          <StatusDot status={status === 'incomplete' ? 'empty' : status} />
        </div>
      </div>

      {showTotalCount && !isNone && (
        <div className="flex items-center gap-2 mb-3">
          <label className="text-xs text-surface-500 dark:text-surface-400 whitespace-nowrap">
            Total RFIs for subject:
          </label>
          <input
            type="number"
            min="0"
            value={totalCount}
            onChange={(e) => setTotalCount(e.target.value)}
            onBlur={async () => {
              const parsed = totalCount === '' ? null : parseInt(totalCount, 10);
              if (parsed !== null && (isNaN(parsed) || parsed < 0)) return;
              try {
                await ingestionApi.setTotalCount(token, caseData.case_id, sectionKey, parsed, subjectIndex);
                if (onSaved) onSaved();
              } catch (err) {
                console.error('Failed to save total count:', err);
              }
            }}
            onKeyDown={(e) => e.key === 'Enter' && e.target.blur()}
            placeholder={String(entries.length || 0)}
            className="w-16 px-2 py-1 rounded-md bg-white dark:bg-surface-900 border border-surface-300 dark:border-surface-600 text-surface-900 dark:text-surface-100 text-sm text-center focus:outline-none focus:ring-2 focus:ring-gold-500/50 focus:border-gold-500"
          />
          {entries.length > 0 && totalCount && parseInt(totalCount, 10) > entries.length && (
            <span className="text-xs text-surface-400">
              ({entries.length} included below)
            </span>
          )}
        </div>
      )}

      {/* Existing entries */}
      {entries.length > 0 && (
        <div className={`space-y-2 mb-3 ${isComplete ? 'opacity-60' : ''}`}>
          {entries.map((entry, idx) => (
            <div
              key={entry.id}
              className="flex items-start gap-2 bg-white dark:bg-surface-900 rounded-lg p-3 border border-surface-200 dark:border-surface-700"
            >
              <span className="text-xs text-surface-400 font-mono mt-0.5 shrink-0">#{idx + 1}</span>
              <div className="flex-1 min-w-0">
                <p className="text-sm text-surface-700 dark:text-surface-300 line-clamp-3">
                  {entry.text}
                </p>
                {entry.images && entry.images.length > 0 && (
                  <div className="flex items-center gap-1.5 mt-1.5">
                    <svg className="w-3.5 h-3.5 text-surface-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                    <span className="text-xs text-surface-400">
                      {entry.images.length} image{entry.images.length !== 1 ? 's' : ''}
                    </span>
                    {/* Thumbnail strip */}
                    <div className="flex gap-1 ml-1">
                      {entry.images.slice(0, 4).map((img) => (
                        <img
                          key={img.image_id}
                          src={`/api/ingestion/images/${caseData.case_id}/${sectionKey}/${entry.id}/${img.image_id}`}
                          alt={img.filename || 'RFI document'}
                          className="w-8 h-8 rounded object-cover border border-surface-600"
                        />
                      ))}
                      {entry.images.length > 4 && (
                        <span className="w-8 h-8 rounded bg-surface-700 border border-surface-600 flex items-center justify-center text-[10px] text-surface-400">
                          +{entry.images.length - 4}
                        </span>
                      )}
                    </div>
                  </div>
                )}
              </div>
              {!isComplete && (
                <button
                  onClick={() => handleRemoveEntry(entry.id)}
                  className="text-surface-400 hover:text-red-400 text-xs shrink-0 transition-colors"
                  title="Remove entry"
                >
                  &times;
                </button>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Add new entry (hidden when complete) */}
      {!isComplete && (
        <>
          <div
            onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
            onDragLeave={() => setDragOver(false)}
            onDrop={handleDrop}
            className={`rounded-lg transition-colors ${dragOver ? 'ring-2 ring-gold-500 bg-gold-500/5' : ''}`}
          >
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              onPaste={handlePaste}
              placeholder="Describe the RFI — what was requested, when, and any response received. Paste or drag images here..."
              rows={4}
              className="w-full px-3 py-2 rounded-lg bg-white dark:bg-surface-900 border border-surface-300 dark:border-surface-600 text-surface-900 dark:text-surface-100 placeholder-surface-400 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-gold-500/50 focus:border-gold-500 mb-2"
            />
          </div>

          {/* Image upload area */}
          <div className="mb-3">
            <input
              ref={fileInputRef}
              type="file"
              accept="image/jpeg,image/png,image/gif,image/webp"
              multiple
              onChange={handleFilesSelected}
              className="hidden"
            />
            <button
              onClick={() => fileInputRef.current?.click()}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-dashed border-surface-400 dark:border-surface-600 text-surface-500 dark:text-surface-400 hover:border-gold-500 hover:text-gold-500 text-xs transition-colors"
            >
              <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              Attach Documents
            </button>
            <span className="text-[10px] text-surface-500 ml-2">or paste / drag &amp; drop</span>

            {/* Selected file previews */}
            {selectedFiles.length > 0 && (
              <div className="flex flex-wrap gap-2 mt-2">
                {selectedFiles.map((file, idx) => (
                  <div key={idx} className="relative group">
                    <img
                      src={URL.createObjectURL(file)}
                      alt={file.name}
                      className="w-16 h-16 rounded-lg object-cover border border-surface-300 dark:border-surface-600"
                    />
                    <button
                      onClick={() => removeSelectedFile(idx)}
                      className="absolute -top-1.5 -right-1.5 w-4 h-4 rounded-full bg-red-500 text-white text-[10px] flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
                    >
                      &times;
                    </button>
                    <span className="block text-[9px] text-surface-400 mt-0.5 max-w-[64px] truncate">
                      {file.name}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={handleAddEntry}
              disabled={adding || !text.trim()}
              className="px-4 py-1.5 rounded-lg border border-gold-500 text-gold-500 hover:bg-gold-500/10 font-semibold text-sm transition-colors disabled:opacity-50"
            >
              {adding ? 'Adding...' : 'Add Another'}
            </button>
            {(entries.length > 0 || text.trim()) && (
              <button
                onClick={handleProcess}
                disabled={processing || (entries.length === 0 && !text.trim())}
                className="px-4 py-1.5 rounded-lg bg-gold-500 hover:bg-gold-600 text-surface-900 font-semibold text-sm transition-colors disabled:opacity-50"
              >
                {processing ? 'Processing...' : `Done — Process All (${entries.length + (text.trim() ? 1 : 0)})`}
              </button>
            )}
            {entries.length === 0 && !text.trim() && (
              <button
                onClick={handleMarkNone}
                className="px-3 py-1.5 rounded-lg text-xs text-surface-400 hover:text-surface-600 dark:hover:text-surface-300 border border-surface-300 dark:border-surface-600 hover:bg-surface-200 dark:hover:bg-surface-700 transition-colors"
              >
                No Data
              </button>
            )}
            {aiStatus === 'error' && entries.length > 0 && (
              <button
                onClick={handleProcess}
                disabled={processing}
                className="px-4 py-1.5 rounded-lg border border-amber-500/50 text-amber-500 hover:bg-amber-500/10 font-semibold text-sm transition-colors disabled:opacity-50"
              >
                {processing ? 'Retrying...' : 'Retry Processing'}
              </button>
            )}
          </div>
        </>
      )}

      {/* Actions when complete */}
      {isComplete && (
        <div className="flex items-center gap-3">
          <button
            onClick={handlePreview}
            className="px-3 py-1.5 rounded-lg border border-surface-300 dark:border-surface-600 text-surface-700 dark:text-surface-300 hover:bg-surface-200 dark:hover:bg-surface-700 text-sm transition-colors"
          >
            Preview
          </button>
          <button
            onClick={handleReset}
            className="px-3 py-1.5 rounded-lg border border-red-500/30 text-red-500 hover:bg-red-500/10 text-sm transition-colors"
          >
            Reset
          </button>
        </div>
      )}

      {showPreview && previewData && (
        <RFIPreviewModal
          title={SECTION_LABELS[sectionKey]}
          data={previewData}
          caseId={caseData.case_id}
          activeTab={previewTab}
          onTabChange={setPreviewTab}
          onClose={() => setShowPreview(false)}
        />
      )}
    </div>
  );
}


// ── RFI Preview Modal ────────────────────────────────────────────

function RFIPreviewModal({ title, data, caseId, activeTab, onTabChange, onClose }) {
  const content = activeTab === 'ai' ? data.output : data.raw_text;
  const entries = data.entries || [];
  const [copied, setCopied] = useState(false);
  const [expandedEntry, setExpandedEntry] = useState(null);

  function handleCopy() {
    if (content) {
      navigator.clipboard.writeText(content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
      <div className="bg-white dark:bg-surface-800 rounded-xl w-full max-w-4xl max-h-[85vh] flex flex-col border border-surface-200 dark:border-surface-700 shadow-2xl">
        <div className="flex items-center justify-between px-5 py-3 border-b border-surface-200 dark:border-surface-700">
          <h3 className="text-base font-semibold text-surface-900 dark:text-surface-100">{title}</h3>
          <div className="flex items-center gap-3">
            <div className="flex bg-surface-100 dark:bg-surface-900 rounded-lg p-0.5">
              <button
                onClick={() => onTabChange('ai')}
                className={`px-3 py-1 rounded-md text-xs font-medium transition-colors ${
                  activeTab === 'ai'
                    ? 'bg-gold-500 text-surface-900'
                    : 'text-surface-500 hover:text-surface-700 dark:hover:text-surface-300'
                }`}
              >
                AI Summary
              </button>
              <button
                onClick={() => onTabChange('entries')}
                className={`px-3 py-1 rounded-md text-xs font-medium transition-colors ${
                  activeTab === 'entries'
                    ? 'bg-gold-500 text-surface-900'
                    : 'text-surface-500 hover:text-surface-700 dark:hover:text-surface-300'
                }`}
              >
                Per-Entry ({entries.length})
              </button>
              <button
                onClick={() => onTabChange('raw')}
                className={`px-3 py-1 rounded-md text-xs font-medium transition-colors ${
                  activeTab === 'raw'
                    ? 'bg-gold-500 text-surface-900'
                    : 'text-surface-500 hover:text-surface-700 dark:hover:text-surface-300'
                }`}
              >
                Raw
              </button>
            </div>
            <button onClick={handleCopy} className="text-xs text-surface-400 hover:text-surface-200 transition-colors">
              {copied ? 'Copied!' : 'Copy'}
            </button>
            <button onClick={onClose} className="text-surface-400 hover:text-surface-200 text-lg">&times;</button>
          </div>
        </div>
        <div className="flex-1 overflow-y-auto p-5">
          {data.ai_error && activeTab === 'ai' && (
            <div className="mb-3 text-xs text-red-400 bg-red-500/10 rounded-lg px-3 py-2">
              AI Error: {data.ai_error}
            </div>
          )}

          {activeTab === 'entries' ? (
            <div className="space-y-3">
              {entries.map((entry, idx) => (
                <div key={entry.id} className="bg-surface-100 dark:bg-surface-900 rounded-lg border border-surface-200 dark:border-surface-700">
                  <button
                    onClick={() => setExpandedEntry(expandedEntry === idx ? null : idx)}
                    className="w-full flex items-center justify-between px-4 py-2.5 text-left"
                  >
                    <span className="text-sm font-medium text-surface-800 dark:text-surface-200">
                      RFI #{idx + 1}
                      {entry.images && entry.images.length > 0 && (
                        <span className="ml-2 text-xs text-surface-400">
                          ({entry.images.length} doc{entry.images.length !== 1 ? 's' : ''})
                        </span>
                      )}
                    </span>
                    <svg
                      className={`w-4 h-4 text-surface-400 transition-transform ${expandedEntry === idx ? 'rotate-180' : ''}`}
                      fill="none" stroke="currentColor" viewBox="0 0 24 24"
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </button>
                  {expandedEntry === idx && (
                    <div className="px-4 pb-3 space-y-2">
                      <div className="text-xs text-surface-400 mb-1">Original text:</div>
                      <pre className="text-sm text-surface-700 dark:text-surface-300 whitespace-pre-wrap font-mono bg-white dark:bg-surface-800 rounded p-2">
                        {entry.text}
                      </pre>
                      {entry.images && entry.images.length > 0 && (
                        <div className="flex flex-wrap gap-2 mt-2">
                          {entry.images.map((img) => (
                            <a
                              key={img.image_id}
                              href={`/api/ingestion/images/${caseId}/rfis/${entry.id}/${img.image_id}`}
                              target="_blank"
                              rel="noopener noreferrer"
                            >
                              <img
                                src={`/api/ingestion/images/${caseId}/rfis/${entry.id}/${img.image_id}`}
                                alt={img.filename || 'Document'}
                                className="w-24 h-24 rounded-lg object-cover border border-surface-600 hover:border-gold-500 transition-colors"
                              />
                            </a>
                          ))}
                        </div>
                      )}
                      {entry.ai_output && (
                        <>
                          <div className="text-xs text-surface-400 mt-3 mb-1">AI analysis:</div>
                          <pre className="text-sm text-surface-700 dark:text-surface-300 whitespace-pre-wrap font-mono bg-emerald-500/5 border border-emerald-500/20 rounded p-2">
                            {entry.ai_output}
                          </pre>
                        </>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <pre className="text-sm text-surface-800 dark:text-surface-200 whitespace-pre-wrap font-mono leading-relaxed">
              {content || 'No content available.'}
            </pre>
          )}
        </div>
      </div>
    </div>
  );
}


// ── Helpers: Extract Images from HTML Paste ──────────────────────

const MIN_PASTE_IMAGE_BYTES = 15000; // 15KB — skip avatars and UI chrome

function dataUriToFile(dataUri, index) {
  try {
    const [header, base64] = dataUri.split(',');
    if (!base64) return null;
    const mime = header.match(/:(.*?);/)?.[1] || 'image/png';
    const binary = atob(base64);
    const array = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) {
      array[i] = binary.charCodeAt(i);
    }
    const ext = mime.split('/')[1] || 'png';
    return new File([array], `pasted_${Date.now()}_${index}.${ext}`, { type: mime });
  } catch {
    return null;
  }
}

function extractImagesFromHtml(html) {
  try {
    const parser = new DOMParser();
    const doc = parser.parseFromString(html, 'text/html');
    const imgs = doc.querySelectorAll('img');
    const files = [];
    imgs.forEach((img, idx) => {
      const src = img.src;
      if (src && src.startsWith('data:')) {
        const file = dataUriToFile(src, idx);
        if (file && file.size >= MIN_PASTE_IMAGE_BYTES) {
          files.push(file);
        }
      }
    });
    return files;
  } catch {
    return [];
  }
}


// ── Text + Image Section (L1 Victim, L1 Suspect) ────────────────

function TextImageSection({ sectionKey, caseData, placeholder, onSaved, subjectIndex }) {
  const { token } = useAuth();
  const section = caseData.sections?.[sectionKey] || {};
  const [text, setText] = useState(section.raw_text || '');
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [saving, setSaving] = useState(false);
  const [showPreview, setShowPreview] = useState(false);
  const [previewData, setPreviewData] = useState(null);
  const [previewTab, setPreviewTab] = useState('ai');
  const [dragOver, setDragOver] = useState(false);

  const status = section.status || 'empty';
  const aiStatus = section.ai_status;
  const isComplete = status === 'complete';
  const isNone = status === 'none';
  const isProcessing = status === 'processing';

  const fileInputRef = useRef(null);

  function handleFilesSelected(e) {
    const files = Array.from(e.target.files || []);
    setSelectedFiles((prev) => [...prev, ...files]);
    if (fileInputRef.current) fileInputRef.current.value = '';
  }

  function removeSelectedFile(idx) {
    setSelectedFiles((prev) => prev.filter((_, i) => i !== idx));
  }

  function addImageFiles(files) {
    const imageFiles = files.filter((f) => f.type.startsWith('image/'));
    if (imageFiles.length > 0) {
      setSelectedFiles((prev) => [...prev, ...imageFiles]);
    }
  }

  function handlePaste(e) {
    // HTML with tables/formatting → convert to Markdown and insert
    const markdown = getMarkdownFromPaste(e.clipboardData);
    if (markdown) {
      e.preventDefault();
      const ta = e.target;
      const start = ta.selectionStart;
      const end = ta.selectionEnd;
      setText((prev) => prev.substring(0, start) + markdown + prev.substring(end));
      requestAnimationFrame(() => {
        ta.selectionStart = ta.selectionEnd = start + markdown.length;
      });
      return;
    }

    const html = e.clipboardData?.getData('text/html');

    // Extract images embedded in HTML (e.g., chat log pasted via Notes)
    if (html) {
      const extracted = extractImagesFromHtml(html);
      if (extracted.length > 0) {
        setSelectedFiles((prev) => [...prev, ...extracted]);
      }
    }

    // Handle direct image paste (screenshot only, no text content)
    const items = e.clipboardData?.items;
    if (items) {
      const hasText = Array.from(items).some(
        (i) => i.type.startsWith('text/')
      );
      if (!hasText) {
        const imageFiles = [];
        for (const item of items) {
          if (item.type.startsWith('image/')) {
            const file = item.getAsFile();
            if (file) imageFiles.push(file);
          }
        }
        if (imageFiles.length > 0) {
          e.preventDefault();
          setSelectedFiles((prev) => [...prev, ...imageFiles]);
        }
      }
    }
    // Default: text flows into textarea normally
  }

  function handleDrop(e) {
    e.preventDefault();
    setDragOver(false);
    const files = Array.from(e.dataTransfer?.files || []);
    addImageFiles(files);
  }

  async function handleSaveAndProcess() {
    if (!text.trim() && selectedFiles.length === 0) return;
    setSaving(true);
    try {
      await ingestionApi.saveTextImageSection(
        token, caseData.case_id, sectionKey, text, selectedFiles, subjectIndex,
      );
      setSelectedFiles([]);
      if (onSaved) onSaved();
    } catch (err) {
      console.error(`Failed to save ${sectionKey}:`, err);
    } finally {
      setSaving(false);
    }
  }

  async function handleReset() {
    try {
      await ingestionApi.resetTextImageSection(token, caseData.case_id, sectionKey, subjectIndex);
      setText('');
      setSelectedFiles([]);
      if (onSaved) onSaved();
    } catch (err) {
      console.error(`Failed to reset ${sectionKey}:`, err);
    }
  }

  async function handlePreview() {
    try {
      const data = await ingestionApi.getTextImageSection(token, caseData.case_id, sectionKey, subjectIndex);
      setPreviewData(data);
      setPreviewTab('ai');
      setShowPreview(true);
    } catch (err) {
      console.error(`Failed to load preview for ${sectionKey}:`, err);
    }
  }

  async function handleMarkNone() {
    try {
      await ingestionApi.markSectionNone(token, caseData.case_id, sectionKey, subjectIndex);
      if (onSaved) onSaved();
    } catch (err) {
      console.error(`Failed to mark ${sectionKey} N/A:`, err);
    }
  }

  if (isNone) {
    async function handleReopen() {
      try {
        await ingestionApi.reopenSection(token, caseData.case_id, sectionKey, subjectIndex);
        if (onSaved) onSaved();
      } catch (err) {
        console.error(`Failed to reopen ${sectionKey}:`, err);
      }
    }
    return (
      <div className="bg-surface-100/50 dark:bg-surface-800/50 rounded-xl p-5 border border-surface-200/50 dark:border-surface-700/50">
        <div className="flex items-center justify-between">
          <h4 className="text-base font-semibold text-surface-500 dark:text-surface-400">
            {SECTION_LABELS[sectionKey]}
          </h4>
          <div className="flex items-center gap-2">
            <button
              onClick={handleReopen}
              className="text-[10px] text-surface-400 hover:text-surface-600 dark:hover:text-surface-300 transition-colors"
            >
              Reopen
            </button>
            <StatusDot status="none" />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-surface-100 dark:bg-surface-800 rounded-xl p-5 border border-surface-200 dark:border-surface-700">
      <div className="flex items-center justify-between mb-3">
        <h4 className="text-base font-semibold text-surface-900 dark:text-surface-100">
          {SECTION_LABELS[sectionKey]}
        </h4>
        <div className="flex items-center gap-2">
          {aiStatus && (
            <span className={`text-[10px] px-2 py-0.5 rounded-full ${
              aiStatus === 'complete' ? 'bg-emerald-500/20 text-emerald-400' :
              aiStatus === 'processing' ? 'bg-gold-500/20 text-gold-400' :
              aiStatus === 'error' ? 'bg-red-500/20 text-red-400' : ''
            }`}>
              {aiStatus === 'complete' ? 'AI processed' :
               aiStatus === 'processing' ? 'AI processing...' :
               aiStatus === 'error' ? 'AI failed (raw saved)' : ''}
            </span>
          )}
          <StatusDot status={status} />
        </div>
      </div>

      {/* Input area (hidden when complete or processing) */}
      {!isComplete && !isProcessing && (
        <>
          <div
            onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
            onDragLeave={() => setDragOver(false)}
            onDrop={handleDrop}
            className={`rounded-lg transition-colors ${dragOver ? 'ring-2 ring-gold-500 bg-gold-500/5' : ''}`}
          >
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              onPaste={handlePaste}
              placeholder={placeholder}
              rows={6}
              className="w-full px-3 py-2 rounded-lg bg-white dark:bg-surface-900 border border-surface-300 dark:border-surface-600 text-surface-900 dark:text-surface-100 placeholder-surface-400 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-gold-500/50 focus:border-gold-500 mb-2"
            />
          </div>

          {/* Image upload area */}
          <div className="mb-3">
            <input
              ref={fileInputRef}
              type="file"
              accept="image/jpeg,image/png,image/gif,image/webp"
              multiple
              onChange={handleFilesSelected}
              className="hidden"
            />
            <button
              onClick={() => fileInputRef.current?.click()}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-dashed border-surface-400 dark:border-surface-600 text-surface-500 dark:text-surface-400 hover:border-gold-500 hover:text-gold-500 text-xs transition-colors"
            >
              <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              Attach Screenshots
            </button>
            <span className="text-[10px] text-surface-500 ml-2">or paste / drag &amp; drop — embedded images auto-extracted</span>

            {/* Selected file previews */}
            {selectedFiles.length > 0 && (
              <div className="flex flex-wrap gap-2 mt-2">
                {selectedFiles.map((file, idx) => (
                  <div key={idx} className="relative group">
                    <img
                      src={URL.createObjectURL(file)}
                      alt={file.name}
                      className="w-16 h-16 rounded-lg object-cover border border-surface-300 dark:border-surface-600"
                    />
                    <button
                      onClick={() => removeSelectedFile(idx)}
                      className="absolute -top-1.5 -right-1.5 w-4 h-4 rounded-full bg-red-500 text-white text-[10px] flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
                    >
                      &times;
                    </button>
                    <span className="block text-[9px] text-surface-400 mt-0.5 max-w-[64px] truncate">
                      {file.name}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={handleSaveAndProcess}
              disabled={saving || (!text.trim() && selectedFiles.length === 0)}
              className="px-4 py-1.5 rounded-lg bg-gold-500 hover:bg-gold-600 text-surface-900 font-semibold text-sm transition-colors disabled:opacity-50"
            >
              {saving ? 'Processing...' : 'Save & Process'}
            </button>
            {status === 'empty' && !text.trim() && selectedFiles.length === 0 && (
              <button
                onClick={handleMarkNone}
                className="px-3 py-1.5 rounded-lg text-xs text-surface-400 hover:text-surface-600 dark:hover:text-surface-300 border border-surface-300 dark:border-surface-600 hover:bg-surface-200 dark:hover:bg-surface-700 transition-colors"
              >
                No Data
              </button>
            )}
          </div>
        </>
      )}

      {/* Processing indicator */}
      {isProcessing && (
        <div className="flex items-center gap-3 py-4">
          <LoadingSpinner size="sm" />
          <span className="text-sm text-surface-400">Processing communications...</span>
        </div>
      )}

      {/* Actions when complete */}
      {isComplete && (
        <div className="flex items-center gap-3">
          <button
            onClick={handlePreview}
            className="px-3 py-1.5 rounded-lg border border-surface-300 dark:border-surface-600 text-surface-700 dark:text-surface-300 hover:bg-surface-200 dark:hover:bg-surface-700 text-sm transition-colors"
          >
            Preview
          </button>
          <button
            onClick={handleReset}
            className="px-3 py-1.5 rounded-lg border border-red-500/30 text-red-500 hover:bg-red-500/10 text-sm transition-colors"
          >
            Reset
          </button>
        </div>
      )}

      {showPreview && previewData && (
        <TextImagePreviewModal
          title={SECTION_LABELS[sectionKey]}
          sectionKey={sectionKey}
          data={previewData}
          caseId={caseData.case_id}
          activeTab={previewTab}
          onTabChange={setPreviewTab}
          onClose={() => setShowPreview(false)}
        />
      )}
    </div>
  );
}


// ── Text + Image Preview Modal ───────────────────────────────────

function TextImagePreviewModal({ title, sectionKey, data, caseId, activeTab, onTabChange, onClose }) {
  const content = activeTab === 'ai' ? data.output : data.raw_text;
  const images = data.images || [];
  const batchId = data.batch_id;
  const [copied, setCopied] = useState(false);

  function handleCopy() {
    if (content) {
      navigator.clipboard.writeText(content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
      <div className="bg-white dark:bg-surface-800 rounded-xl w-full max-w-4xl max-h-[85vh] flex flex-col border border-surface-200 dark:border-surface-700 shadow-2xl">
        <div className="flex items-center justify-between px-5 py-3 border-b border-surface-200 dark:border-surface-700">
          <h3 className="text-base font-semibold text-surface-900 dark:text-surface-100">{title}</h3>
          <div className="flex items-center gap-3">
            <div className="flex bg-surface-100 dark:bg-surface-900 rounded-lg p-0.5">
              <button
                onClick={() => onTabChange('ai')}
                className={`px-3 py-1 rounded-md text-xs font-medium transition-colors ${
                  activeTab === 'ai'
                    ? 'bg-gold-500 text-surface-900'
                    : 'text-surface-500 hover:text-surface-700 dark:hover:text-surface-300'
                }`}
              >
                AI Summary
              </button>
              <button
                onClick={() => onTabChange('raw')}
                className={`px-3 py-1 rounded-md text-xs font-medium transition-colors ${
                  activeTab === 'raw'
                    ? 'bg-gold-500 text-surface-900'
                    : 'text-surface-500 hover:text-surface-700 dark:hover:text-surface-300'
                }`}
              >
                Raw
              </button>
            </div>
            <button onClick={handleCopy} className="text-xs text-surface-400 hover:text-surface-200 transition-colors">
              {copied ? 'Copied!' : 'Copy'}
            </button>
            <button onClick={onClose} className="text-surface-400 hover:text-surface-200 text-lg">&times;</button>
          </div>
        </div>
        <div className="flex-1 overflow-y-auto p-5">
          {data.ai_error && activeTab === 'ai' && (
            <div className="mb-3 text-xs text-red-400 bg-red-500/10 rounded-lg px-3 py-2">
              AI Error: {data.ai_error}
            </div>
          )}

          {/* Source images */}
          {images.length > 0 && batchId && (
            <div className="mb-4">
              <div className="text-xs text-surface-400 mb-2">Source images ({images.length})</div>
              <div className="flex flex-wrap gap-2">
                {images.map((img) => (
                  <a
                    key={img.image_id}
                    href={`/api/ingestion/images/${caseId}/${sectionKey}/${batchId}/${img.image_id}`}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    <img
                      src={`/api/ingestion/images/${caseId}/${sectionKey}/${batchId}/${img.image_id}`}
                      alt={img.filename || 'Screenshot'}
                      className="w-20 h-20 rounded-lg object-cover border border-surface-300 dark:border-surface-600 hover:border-gold-500 transition-colors"
                    />
                  </a>
                ))}
              </div>
            </div>
          )}

          <pre className="text-sm text-surface-800 dark:text-surface-200 whitespace-pre-wrap font-mono leading-relaxed">
            {content || 'No content available.'}
          </pre>
        </div>
      </div>
    </div>
  );
}


// ── KYC Document Section (Image-Only) ────────────────────────────

function KYCSection({ caseData, onSaved, subjectIndex }) {
  const sectionKey = 'kyc';
  const { token } = useAuth();
  const section = caseData.sections?.[sectionKey] || {};
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [showPreview, setShowPreview] = useState(false);
  const [previewData, setPreviewData] = useState(null);
  const [dragOver, setDragOver] = useState(false);

  const status = section.status || 'empty';
  const aiStatus = section.ai_status;
  const isComplete = status === 'complete';
  const isNone = status === 'none';
  const isProcessing = status === 'processing';

  const fileInputRef = useRef(null);

  function handleFilesSelected(e) {
    const files = Array.from(e.target.files || []);
    setSelectedFiles((prev) => [...prev, ...files]);
    if (fileInputRef.current) fileInputRef.current.value = '';
  }

  function removeSelectedFile(idx) {
    setSelectedFiles((prev) => prev.filter((_, i) => i !== idx));
  }

  function addImageFiles(files) {
    const imageFiles = files.filter((f) => f.type.startsWith('image/'));
    if (imageFiles.length > 0) {
      setSelectedFiles((prev) => [...prev, ...imageFiles]);
    }
  }

  function handlePaste(e) {
    const items = e.clipboardData?.items;
    if (!items) return;
    const imageFiles = [];
    for (const item of items) {
      if (item.type.startsWith('image/')) {
        const file = item.getAsFile();
        if (file) imageFiles.push(file);
      }
    }
    if (imageFiles.length > 0) {
      e.preventDefault();
      addImageFiles(imageFiles);
    }
  }

  function handleDrop(e) {
    e.preventDefault();
    setDragOver(false);
    const files = Array.from(e.dataTransfer?.files || []);
    addImageFiles(files);
  }

  async function handleUploadAndProcess() {
    if (selectedFiles.length === 0) return;
    setUploading(true);
    try {
      await ingestionApi.uploadKYC(token, caseData.case_id, selectedFiles, subjectIndex);
      setSelectedFiles([]);
      if (onSaved) onSaved();
    } catch (err) {
      console.error('Failed to upload KYC:', err);
    } finally {
      setUploading(false);
    }
  }

  async function handleReset() {
    try {
      await ingestionApi.resetKYC(token, caseData.case_id, subjectIndex);
      setSelectedFiles([]);
      if (onSaved) onSaved();
    } catch (err) {
      console.error('Failed to reset KYC:', err);
    }
  }

  async function handlePreview() {
    try {
      const data = await ingestionApi.getKYCOutput(token, caseData.case_id, subjectIndex);
      setPreviewData(data);
      setShowPreview(true);
    } catch (err) {
      console.error('Failed to load KYC preview:', err);
    }
  }

  async function handleMarkNone() {
    try {
      await ingestionApi.markSectionNone(token, caseData.case_id, sectionKey, subjectIndex);
      if (onSaved) onSaved();
    } catch (err) {
      console.error('Failed to mark KYC N/A:', err);
    }
  }

  if (isNone) {
    async function handleReopen() {
      try {
        await ingestionApi.reopenSection(token, caseData.case_id, sectionKey, subjectIndex);
        if (onSaved) onSaved();
      } catch (err) {
        console.error('Failed to reopen KYC:', err);
      }
    }
    return (
      <div className="bg-surface-100/50 dark:bg-surface-800/50 rounded-xl p-5 border border-surface-200/50 dark:border-surface-700/50">
        <div className="flex items-center justify-between">
          <h4 className="text-base font-semibold text-surface-500 dark:text-surface-400">
            {SECTION_LABELS[sectionKey]}
          </h4>
          <div className="flex items-center gap-2">
            <button
              onClick={handleReopen}
              className="text-[10px] text-surface-400 hover:text-surface-600 dark:hover:text-surface-300 transition-colors"
            >
              Reopen
            </button>
            <StatusDot status="none" />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-surface-100 dark:bg-surface-800 rounded-xl p-5 border border-surface-200 dark:border-surface-700">
      <div className="flex items-center justify-between mb-3">
        <h4 className="text-base font-semibold text-surface-900 dark:text-surface-100">
          {SECTION_LABELS[sectionKey]}
        </h4>
        <div className="flex items-center gap-2">
          {aiStatus && (
            <span className={`text-[10px] px-2 py-0.5 rounded-full ${
              aiStatus === 'complete' ? 'bg-emerald-500/20 text-emerald-400' :
              aiStatus === 'processing' ? 'bg-gold-500/20 text-gold-400' :
              aiStatus === 'error' ? 'bg-red-500/20 text-red-400' : ''
            }`}>
              {aiStatus === 'complete' ? 'AI processed' :
               aiStatus === 'processing' ? 'AI processing...' :
               aiStatus === 'error' ? 'AI failed' : ''}
            </span>
          )}
          {isComplete && (
            <PreviewButton
              token={token}
              caseId={caseData.case_id}
              sectionKey={sectionKey}
              label={SECTION_LABELS[sectionKey]}
            />
          )}
          <StatusDot status={status} />
        </div>
      </div>

      {/* Upload area (hidden when complete or processing) */}
      {!isComplete && !isProcessing && (
        <>
          <div
            onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
            onDragLeave={() => setDragOver(false)}
            onDrop={handleDrop}
            onPaste={handlePaste}
            tabIndex={0}
            className={`rounded-lg border-2 border-dashed p-6 text-center transition-colors cursor-pointer focus:outline-none ${
              dragOver
                ? 'border-gold-500 bg-gold-500/5'
                : 'border-surface-300 dark:border-surface-600 hover:border-surface-400 dark:hover:border-surface-500'
            }`}
            onClick={() => fileInputRef.current?.click()}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept="image/jpeg,image/png,image/gif,image/webp"
              multiple
              onChange={handleFilesSelected}
              className="hidden"
            />
            <svg className="w-8 h-8 mx-auto mb-2 text-surface-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            <p className="text-sm text-surface-500 dark:text-surface-400">
              Click to select, paste, or drag &amp; drop KYC screenshots
            </p>
            <p className="text-[10px] text-surface-400 mt-1">
              Binance Admin screenshots, ID documents, proof of address
            </p>
          </div>

          {/* Selected file previews */}
          {selectedFiles.length > 0 && (
            <div className="flex flex-wrap gap-2 mt-3">
              {selectedFiles.map((file, idx) => (
                <div key={idx} className="relative group">
                  <img
                    src={URL.createObjectURL(file)}
                    alt={file.name}
                    className="w-20 h-20 rounded-lg object-cover border border-surface-300 dark:border-surface-600"
                  />
                  <button
                    onClick={(e) => { e.stopPropagation(); removeSelectedFile(idx); }}
                    className="absolute -top-1.5 -right-1.5 w-4 h-4 rounded-full bg-red-500 text-white text-[10px] flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
                  >
                    &times;
                  </button>
                  <span className="block text-[9px] text-surface-400 mt-0.5 max-w-[80px] truncate">
                    {file.name}
                  </span>
                </div>
              ))}
            </div>
          )}

          <div className="flex items-center gap-3 mt-3">
            {selectedFiles.length > 0 && (
              <button
                onClick={handleUploadAndProcess}
                disabled={uploading}
                className="px-4 py-1.5 rounded-lg bg-gold-500 hover:bg-gold-600 text-surface-900 font-semibold text-sm transition-colors disabled:opacity-50"
              >
                {uploading ? 'Processing...' : `Upload & Process (${selectedFiles.length})`}
              </button>
            )}
            {selectedFiles.length === 0 && status === 'empty' && (
              <button
                onClick={handleMarkNone}
                className="px-3 py-1.5 rounded-lg text-xs text-surface-400 hover:text-surface-600 dark:hover:text-surface-300 border border-surface-300 dark:border-surface-600 hover:bg-surface-200 dark:hover:bg-surface-700 transition-colors"
              >
                No Data
              </button>
            )}
            {status === 'error' && (
              <button
                onClick={handleReset}
                className="px-4 py-1.5 rounded-lg border border-amber-500/50 text-amber-500 hover:bg-amber-500/10 font-semibold text-sm transition-colors"
              >
                Reset &amp; Try Again
              </button>
            )}
          </div>
        </>
      )}

      {/* Processing indicator */}
      {isProcessing && (
        <div className="flex items-center gap-3 py-4">
          <LoadingSpinner size="sm" />
          <span className="text-sm text-surface-400">Extracting identity data from images...</span>
        </div>
      )}

      {/* Actions when complete */}
      {isComplete && (
        <div className="flex items-center gap-3">
          <button
            onClick={handlePreview}
            className="px-3 py-1.5 rounded-lg border border-surface-300 dark:border-surface-600 text-surface-700 dark:text-surface-300 hover:bg-surface-200 dark:hover:bg-surface-700 text-sm transition-colors"
          >
            Preview
          </button>
          <button
            onClick={handleReset}
            className="px-3 py-1.5 rounded-lg border border-red-500/30 text-red-500 hover:bg-red-500/10 text-sm transition-colors"
          >
            Reset
          </button>
        </div>
      )}

      {showPreview && previewData && (
        <KYCPreviewModal
          data={previewData}
          caseId={caseData.case_id}
          onClose={() => setShowPreview(false)}
        />
      )}
    </div>
  );
}


// ── KYC Preview Modal ────────────────────────────────────────────

function KYCPreviewModal({ data, caseId, onClose }) {
  const [copied, setCopied] = useState(false);
  const images = data.images || [];
  const batchId = data.batch_id;

  function handleCopy() {
    if (data.output) {
      navigator.clipboard.writeText(data.output);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
      <div className="bg-white dark:bg-surface-800 rounded-xl w-full max-w-4xl max-h-[85vh] flex flex-col border border-surface-200 dark:border-surface-700 shadow-2xl">
        <div className="flex items-center justify-between px-5 py-3 border-b border-surface-200 dark:border-surface-700">
          <h3 className="text-base font-semibold text-surface-900 dark:text-surface-100">
            {SECTION_LABELS.kyc}
          </h3>
          <div className="flex items-center gap-3">
            <button onClick={handleCopy} className="text-xs text-surface-400 hover:text-surface-200 transition-colors">
              {copied ? 'Copied!' : 'Copy'}
            </button>
            <button onClick={onClose} className="text-surface-400 hover:text-surface-200 text-lg">&times;</button>
          </div>
        </div>
        <div className="flex-1 overflow-y-auto p-5">
          {data.ai_error && (
            <div className="mb-3 text-xs text-red-400 bg-red-500/10 rounded-lg px-3 py-2">
              AI Error: {data.ai_error}
            </div>
          )}

          {/* Source images */}
          {images.length > 0 && batchId && (
            <div className="mb-4">
              <div className="text-xs text-surface-400 mb-2">Source documents ({images.length})</div>
              <div className="flex flex-wrap gap-2">
                {images.map((img) => (
                  <a
                    key={img.image_id}
                    href={`/api/ingestion/images/${caseId}/kyc/${batchId}/${img.image_id}`}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    <img
                      src={`/api/ingestion/images/${caseId}/kyc/${batchId}/${img.image_id}`}
                      alt={img.filename || 'KYC document'}
                      className="w-24 h-24 rounded-lg object-cover border border-surface-300 dark:border-surface-600 hover:border-gold-500 transition-colors"
                    />
                  </a>
                ))}
              </div>
            </div>
          )}

          {/* AI output */}
          <pre className="text-sm text-surface-800 dark:text-surface-200 whitespace-pre-wrap font-mono leading-relaxed">
            {data.output || 'No output available.'}
          </pre>
        </div>
      </div>
    </div>
  );
}


// ── Kodex / LE Entry Section (iterative per-case entry) ──────────

const KODEX_ACCEPTED_TYPES = '.pdf,.docx,.doc,image/jpeg,image/png,image/gif,image/webp';

function KodexEntrySection({ caseData, onSaved, subjectIndex }) {
  const sectionKey = 'kodex';
  const { token } = useAuth();
  const section = caseData.sections?.[sectionKey] || {};
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [text, setText] = useState('');
  const [adding, setAdding] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [processingCount, setProcessingCount] = useState(0);
  const [showPreview, setShowPreview] = useState(false);
  const [previewData, setPreviewData] = useState(null);
  const [previewTab, setPreviewTab] = useState('ai');
  const [totalCount, setTotalCount] = useState(section.total_count ?? '');
  const [dragOver, setDragOver] = useState(false);

  useEffect(() => {
    setTotalCount(section.total_count ?? '');
  }, [section.total_count]);

  const entries = section.entries || [];
  const status = section.status || 'empty';
  const aiStatus = section.ai_status;
  const isComplete = status === 'complete';
  const isNone = status === 'none';
  const isProcessing = status === 'processing' || processing;
  const isError = status === 'error';
  const hasSubjectUid = !!caseData.subject_uid;

  // Legacy detection: old pipeline used per_case + extracted status
  const isLegacy = !entries.length && (
    (section.per_case?.length > 0) || status === 'extracted'
  );

  // Effective count includes pending staged files/text (not yet saved to MongoDB)
  const hasPending = selectedFiles.length > 0 || text.trim().length > 0;
  const effectiveEntryCount = entries.length + (hasPending ? 1 : 0);

  const fileInputRef = useRef(null);

  function handleFilesSelected(e) {
    const files = Array.from(e.target.files || []);
    setSelectedFiles((prev) => [...prev, ...files]);
    if (fileInputRef.current) fileInputRef.current.value = '';
  }

  function removeSelectedFile(idx) {
    setSelectedFiles((prev) => prev.filter((_, i) => i !== idx));
  }

  function handleDrop(e) {
    e.preventDefault();
    setDragOver(false);
    const files = Array.from(e.dataTransfer?.files || []);
    if (files.length > 0) {
      setSelectedFiles((prev) => [...prev, ...files]);
    }
  }

  function handlePaste(e) {
    // HTML with tables/formatting → convert to Markdown and insert
    const markdown = getMarkdownFromPaste(e.clipboardData);
    if (markdown) {
      e.preventDefault();
      const ta = e.target;
      const start = ta.selectionStart;
      const end = ta.selectionEnd;
      setText((prev) => prev.substring(0, start) + markdown + prev.substring(end));
      requestAnimationFrame(() => {
        ta.selectionStart = ta.selectionEnd = start + markdown.length;
      });
      return;
    }

    const items = e.clipboardData?.items;
    if (!items) return;
    const imageFiles = [];
    for (const item of items) {
      if (item.type.startsWith('image/')) {
        const file = item.getAsFile();
        if (file) imageFiles.push(file);
      }
    }
    if (imageFiles.length > 0) {
      e.preventDefault();
      setSelectedFiles((prev) => [...prev, ...imageFiles]);
    }
  }

  function fileTypeIcon(file) {
    const name = (file.name || '').toLowerCase();
    if (name.endsWith('.pdf')) return 'PDF';
    if (name.endsWith('.docx') || name.endsWith('.doc')) return 'DOC';
    if (file.type?.startsWith('image/')) return 'IMG';
    return 'FILE';
  }

  async function handleAddEntry() {
    if (!text.trim() && selectedFiles.length === 0) return;
    setAdding(true);
    try {
      const autoLabel = `LE Case ${entries.length + 1}`;
      await ingestionApi.addKodexEntry(
        token, caseData.case_id, autoLabel, selectedFiles, subjectIndex, text,
      );
      setSelectedFiles([]);
      setText('');
      if (onSaved) onSaved();
    } catch (err) {
      console.error('Failed to add Kodex entry:', err);
    } finally {
      setAdding(false);
    }
  }

  async function handleRemoveEntry(entryId) {
    try {
      await ingestionApi.removeKodexEntry(token, caseData.case_id, entryId, subjectIndex);
      if (onSaved) onSaved();
    } catch (err) {
      console.error('Failed to remove Kodex entry:', err);
    }
  }

  async function handleProcess() {
    const count = effectiveEntryCount;
    setProcessingCount(count);
    setProcessing(true);
    try {
      // Auto-add pending files/text as a new entry before processing
      if (text.trim() || selectedFiles.length > 0) {
        const autoLabel = `LE Case ${entries.length + 1}`;
        await ingestionApi.addKodexEntry(
          token, caseData.case_id, autoLabel, selectedFiles, subjectIndex, text,
        );
        setSelectedFiles([]);
        setText('');
      }
      await ingestionApi.processEntries(token, caseData.case_id, sectionKey, subjectIndex);
      if (onSaved) onSaved();
    } catch (err) {
      console.error('Failed to process Kodex entries:', err);
    } finally {
      setProcessing(false);
      setProcessingCount(0);
    }
  }

  async function handleReset() {
    try {
      await ingestionApi.resetKodex(token, caseData.case_id, subjectIndex);
      setSelectedFiles([]);
      setText('');
      if (onSaved) onSaved();
    } catch (err) {
      console.error('Failed to reset Kodex:', err);
    }
  }

  async function handlePreview() {
    try {
      const data = await ingestionApi.getKodexOutput(token, caseData.case_id, subjectIndex);
      setPreviewData(data);
      setPreviewTab('ai');
      setShowPreview(true);
    } catch (err) {
      console.error('Failed to load Kodex preview:', err);
    }
  }

  async function handleMarkNone() {
    try {
      await ingestionApi.markSectionNone(token, caseData.case_id, sectionKey, subjectIndex);
      if (onSaved) onSaved();
    } catch (err) {
      console.error('Failed to mark Kodex N/A:', err);
    }
  }

  if (isNone) {
    async function handleReopen() {
      try {
        await ingestionApi.reopenSection(token, caseData.case_id, sectionKey, subjectIndex);
        if (onSaved) onSaved();
      } catch (err) {
        console.error('Failed to reopen Kodex:', err);
      }
    }
    return (
      <div className="bg-surface-100/50 dark:bg-surface-800/50 rounded-xl p-5 border border-surface-200/50 dark:border-surface-700/50">
        <div className="flex items-center justify-between">
          <h4 className="text-base font-semibold text-surface-500 dark:text-surface-400">
            {SECTION_LABELS[sectionKey]}
          </h4>
          <div className="flex items-center gap-2">
            <button
              onClick={handleReopen}
              className="text-[10px] text-surface-400 hover:text-surface-600 dark:hover:text-surface-300 transition-colors"
            >
              Reopen
            </button>
            <StatusDot status="none" />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-surface-100 dark:bg-surface-800 rounded-xl p-5 border border-surface-200 dark:border-surface-700">
      <div className="flex items-center justify-between mb-3">
        <h4 className="text-base font-semibold text-surface-900 dark:text-surface-100">
          {SECTION_LABELS[sectionKey]}
        </h4>
        <div className="flex items-center gap-2">
          {aiStatus && (
            <span className={`text-[10px] px-2 py-0.5 rounded-full ${
              aiStatus === 'complete' ? 'bg-emerald-500/20 text-emerald-400' :
              aiStatus === 'processing' ? 'bg-gold-500/20 text-gold-400' :
              aiStatus === 'error' ? 'bg-red-500/20 text-red-400' : ''
            }`}>
              {aiStatus === 'complete' ? 'AI processed' :
               aiStatus === 'processing' ? 'AI processing...' :
               aiStatus === 'error' ? 'AI failed (raw saved)' : ''}
            </span>
          )}
          {isLegacy && (
            <span className="text-[10px] px-2 py-0.5 rounded-full bg-blue-500/20 text-blue-400">
              Legacy
            </span>
          )}
          <StatusDot status={status === 'incomplete' ? 'empty' : status} />
        </div>
      </div>

      {/* Gate: need subject UID */}
      {!hasSubjectUid && !isComplete && !isLegacy && !isProcessing && !isError && (
        <div className="text-sm text-surface-400 py-3 flex items-center gap-2">
          <svg className="w-4 h-4 text-surface-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
          </svg>
          C360 must be processed first to identify the subject UID.
        </div>
      )}

      {/* Legacy data view */}
      {isLegacy && (
        <div className="mb-3">
          <p className="text-sm text-blue-400 mb-2">
            {section.case_count || 0} PDF(s) uploaded via legacy pipeline.
            {status === 'extracted' ? ' LE assessment will be generated at assembly.' : ''}
          </p>
          <div className="flex items-center gap-3">
            <button
              onClick={handlePreview}
              className="px-3 py-1.5 rounded-lg border border-surface-300 dark:border-surface-600 text-surface-700 dark:text-surface-300 hover:bg-surface-200 dark:hover:bg-surface-700 text-sm transition-colors"
            >
              Preview
            </button>
            <button
              onClick={handleReset}
              className="px-3 py-1.5 rounded-lg border border-red-500/30 text-red-500 hover:bg-red-500/10 text-sm transition-colors"
            >
              Reset &amp; Re-upload
            </button>
          </div>
        </div>
      )}

      {/* Total count input */}
      {hasSubjectUid && !isNone && !isLegacy && (
        <div className="flex items-center gap-2 mb-3">
          <label className="text-xs text-surface-500 dark:text-surface-400 whitespace-nowrap">
            Total Kodex cases for subject:
          </label>
          <input
            type="number"
            min="0"
            value={totalCount}
            onChange={(e) => setTotalCount(e.target.value)}
            onBlur={async () => {
              const parsed = totalCount === '' ? null : parseInt(totalCount, 10);
              if (parsed !== null && (isNaN(parsed) || parsed < 0)) return;
              try {
                await ingestionApi.setTotalCount(token, caseData.case_id, sectionKey, parsed, subjectIndex);
                if (onSaved) onSaved();
              } catch (err) {
                console.error('Failed to save total count:', err);
              }
            }}
            onKeyDown={(e) => e.key === 'Enter' && e.target.blur()}
            placeholder={String(effectiveEntryCount || 0)}
            className="w-16 px-2 py-1 rounded-md bg-white dark:bg-surface-900 border border-surface-300 dark:border-surface-600 text-surface-900 dark:text-surface-100 text-sm text-center focus:outline-none focus:ring-2 focus:ring-gold-500/50 focus:border-gold-500"
          />
          {effectiveEntryCount > 0 && totalCount && parseInt(totalCount, 10) > effectiveEntryCount && (
            <span className="text-xs text-surface-400">
              ({effectiveEntryCount} included below)
            </span>
          )}
        </div>
      )}

      {/* Existing entries list */}
      {entries.length > 0 && !isLegacy && (
        <div className={`space-y-2 mb-3 ${isComplete ? 'opacity-60' : ''}`}>
          {entries.map((entry, idx) => (
            <div
              key={entry.id}
              className="flex items-start gap-2 bg-white dark:bg-surface-900 rounded-lg p-3 border border-surface-200 dark:border-surface-700"
            >
              <span className="text-xs text-surface-400 font-mono mt-0.5 shrink-0">#{idx + 1}</span>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-surface-700 dark:text-surface-300">
                  {entry.label}
                </p>
                {entry.text && (
                  <p className="text-xs text-surface-500 dark:text-surface-400 line-clamp-2 mt-0.5">
                    {entry.text}
                  </p>
                )}
                <div className="flex items-center gap-2 mt-1">
                  {(entry.files || []).length > 0 && (
                    <span className="text-[10px] text-surface-400">
                      {(entry.files || []).length} file{(entry.files || []).length !== 1 ? 's' : ''}
                    </span>
                  )}
                  {entry.text && !(entry.files || []).length && (
                    <span className="text-[10px] text-surface-400 italic">text only</span>
                  )}
                  <div className="flex gap-1">
                    {(entry.files || []).map((f) => {
                      const ext = (f.filename || '').split('.').pop()?.toUpperCase() || 'FILE';
                      const colors = ext === 'PDF' ? 'bg-red-500/20 text-red-400' :
                                     ext === 'DOCX' ? 'bg-blue-500/20 text-blue-400' :
                                     'bg-emerald-500/20 text-emerald-400';
                      return (
                        <span key={f.file_id} className={`text-[9px] px-1.5 py-0.5 rounded ${colors}`}>
                          {ext}
                        </span>
                      );
                    })}
                  </div>
                  {entry.ai_status === 'complete' && (
                    <span className="text-[10px] text-emerald-400">extracted</span>
                  )}
                  {entry.ai_status === 'error' && (
                    <span className="text-[10px] text-red-400">extraction failed</span>
                  )}
                </div>
              </div>
              {!isComplete && (
                <button
                  onClick={() => handleRemoveEntry(entry.id)}
                  className="text-surface-400 hover:text-red-400 text-xs shrink-0 transition-colors"
                  title="Remove entry"
                >
                  &times;
                </button>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Add new entry form (hidden when complete, legacy, or no UID) */}
      {hasSubjectUid && !isComplete && !isLegacy && !isProcessing && (
        <>
          {isError && section.error_message && (
            <div className="mb-2 text-xs text-red-400 bg-red-500/10 rounded-lg px-3 py-2">
              {section.error_message}
            </div>
          )}

          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            onPaste={handlePaste}
            placeholder="Paste or type LE case details — screenshots can be pasted directly..."
            rows={3}
            className="w-full px-3 py-2 rounded-lg bg-white dark:bg-surface-900 border border-surface-300
              dark:border-surface-600 text-surface-900 dark:text-surface-100 placeholder-surface-400
              text-sm font-mono focus:outline-none focus:ring-2 focus:ring-gold-500/50
              focus:border-gold-500 mb-2"
          />

          <div
            onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
            onDragLeave={() => setDragOver(false)}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            className={`rounded-lg border-2 border-dashed p-4 text-center transition-colors cursor-pointer mb-2 ${
              dragOver
                ? 'border-gold-500 bg-gold-500/5'
                : 'border-surface-300 dark:border-surface-600 hover:border-surface-400 dark:hover:border-surface-500'
            }`}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept={KODEX_ACCEPTED_TYPES}
              multiple
              onChange={handleFilesSelected}
              className="hidden"
            />
            <svg className="w-6 h-6 mx-auto mb-1 text-surface-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
            </svg>
            <p className="text-xs text-surface-500 dark:text-surface-400">
              Drop files here — PDFs, Word docs, images
            </p>
          </div>

          {/* Selected file list */}
          {selectedFiles.length > 0 && (
            <div className="space-y-1 mb-2">
              {selectedFiles.map((file, idx) => (
                <div key={idx} className="flex items-center justify-between px-3 py-1.5 rounded-lg bg-surface-200/50 dark:bg-surface-700/50">
                  <div className="flex items-center gap-2 min-w-0">
                    <span className={`text-[10px] font-mono px-1.5 py-0.5 rounded ${
                      fileTypeIcon(file) === 'PDF' ? 'bg-red-500/20 text-red-400' :
                      fileTypeIcon(file) === 'DOC' ? 'bg-blue-500/20 text-blue-400' :
                      fileTypeIcon(file) === 'IMG' ? 'bg-emerald-500/20 text-emerald-400' :
                      'bg-surface-500/20 text-surface-400'
                    }`}>{fileTypeIcon(file)}</span>
                    <span className="text-xs text-surface-600 dark:text-surface-300 truncate">{file.name}</span>
                    <span className="text-[10px] text-surface-400 shrink-0">{(file.size / 1024).toFixed(0)} KB</span>
                  </div>
                  <button
                    onClick={(e) => { e.stopPropagation(); removeSelectedFile(idx); }}
                    className="text-surface-400 hover:text-red-400 text-sm ml-2 shrink-0"
                  >
                    &times;
                  </button>
                </div>
              ))}
            </div>
          )}

          <div className="flex items-center gap-3">
            <button
              onClick={handleAddEntry}
              disabled={adding || (!text.trim() && selectedFiles.length === 0)}
              className="px-4 py-1.5 rounded-lg border border-gold-500 text-gold-500 hover:bg-gold-500/10 font-semibold text-sm transition-colors disabled:opacity-50"
            >
              {adding ? 'Adding...' : 'Add Entry'}
            </button>
            {effectiveEntryCount > 0 && (
              <button
                onClick={handleProcess}
                disabled={processing}
                className="px-4 py-1.5 rounded-lg bg-gold-500 hover:bg-gold-600 text-surface-900 font-semibold text-sm transition-colors disabled:opacity-50"
              >
                {processing ? 'Processing...' : `Done — Process All (${effectiveEntryCount})`}
              </button>
            )}
            {effectiveEntryCount === 0 && (
              <button
                onClick={handleMarkNone}
                className="px-3 py-1.5 rounded-lg text-xs text-surface-400 hover:text-surface-600 dark:hover:text-surface-300 border border-surface-300 dark:border-surface-600 hover:bg-surface-200 dark:hover:bg-surface-700 transition-colors"
              >
                No Data
              </button>
            )}
            {aiStatus === 'error' && entries.length > 0 && (
              <button
                onClick={handleProcess}
                disabled={processing}
                className="px-4 py-1.5 rounded-lg border border-amber-500/50 text-amber-500 hover:bg-amber-500/10 font-semibold text-sm transition-colors disabled:opacity-50"
              >
                {processing ? 'Retrying...' : 'Retry Processing'}
              </button>
            )}
          </div>
        </>
      )}

      {/* No Data button when no UID and section is empty */}
      {!hasSubjectUid && status === 'empty' && (
        <div className="mt-2">
          <button
            onClick={handleMarkNone}
            className="px-3 py-1.5 rounded-lg text-xs text-surface-400 hover:text-surface-600 dark:hover:text-surface-300 border border-surface-300 dark:border-surface-600 hover:bg-surface-200 dark:hover:bg-surface-700 transition-colors"
          >
            No Data
          </button>
        </div>
      )}

      {/* Processing indicator */}
      {isProcessing && (
        <div className="flex items-center gap-3 py-4">
          <LoadingSpinner size="sm" />
          <span className="text-sm text-surface-400">
            Processing {processingCount || entries.length || '?'} LE case {(processingCount || entries.length) === 1 ? 'entry' : 'entries'} — extracting &amp; synthesizing...
          </span>
        </div>
      )}

      {/* Actions when complete */}
      {isComplete && !isLegacy && (
        <div className="flex items-center gap-3">
          <button
            onClick={handlePreview}
            className="px-3 py-1.5 rounded-lg border border-surface-300 dark:border-surface-600 text-surface-700 dark:text-surface-300 hover:bg-surface-200 dark:hover:bg-surface-700 text-sm transition-colors"
          >
            Preview
          </button>
          <button
            onClick={handleReset}
            className="px-3 py-1.5 rounded-lg border border-red-500/30 text-red-500 hover:bg-red-500/10 text-sm transition-colors"
          >
            Reset
          </button>
        </div>
      )}

      {showPreview && previewData && (
        <KodexPreviewModal
          data={previewData}
          activeTab={previewTab}
          onTabChange={setPreviewTab}
          onClose={() => setShowPreview(false)}
        />
      )}
    </div>
  );
}


// ── Kodex Preview Modal ──────────────────────────────────────────

function KodexPreviewModal({ data, activeTab, onTabChange, onClose }) {
  const [copied, setCopied] = useState(false);
  const [expandedEntry, setExpandedEntry] = useState(null);
  const entries = data.entries || [];
  const perCase = data.per_case || [];
  const isLegacy = !entries.length && perCase.length > 0;

  function handleCopy() {
    const textToCopy = activeTab === 'ai' ? data.output : (
      entries.length > 0
        ? entries.map((e, i) => `--- Entry ${i + 1}: ${e.label} ---\n${e.ai_output || '(not extracted)'}`).join('\n\n')
        : perCase.map((pc) => pc.extracted_text || '').join('\n\n---\n\n')
    );
    if (textToCopy) {
      navigator.clipboard.writeText(textToCopy);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
      <div className="bg-white dark:bg-surface-800 rounded-xl w-full max-w-5xl max-h-[85vh] flex flex-col border border-surface-200 dark:border-surface-700 shadow-2xl">
        <div className="flex items-center justify-between px-5 py-3 border-b border-surface-200 dark:border-surface-700">
          <h3 className="text-base font-semibold text-surface-900 dark:text-surface-100">
            {SECTION_LABELS.kodex} — {entries.length || data.case_count || 0} case(s)
          </h3>
          <div className="flex items-center gap-3">
            {!isLegacy && (
              <div className="flex bg-surface-100 dark:bg-surface-900 rounded-lg p-0.5">
                <button
                  onClick={() => onTabChange('ai')}
                  className={`px-3 py-1 rounded-md text-xs font-medium transition-colors ${
                    activeTab === 'ai'
                      ? 'bg-gold-500 text-surface-900'
                      : 'text-surface-400 hover:text-surface-200'
                  }`}
                >
                  AI Summary
                </button>
                <button
                  onClick={() => onTabChange('entries')}
                  className={`px-3 py-1 rounded-md text-xs font-medium transition-colors ${
                    activeTab === 'entries'
                      ? 'bg-gold-500 text-surface-900'
                      : 'text-surface-400 hover:text-surface-200'
                  }`}
                >
                  Per-Entry
                </button>
              </div>
            )}
            <button onClick={handleCopy} className="text-xs text-surface-400 hover:text-surface-200 transition-colors">
              {copied ? 'Copied!' : 'Copy'}
            </button>
            <button onClick={onClose} className="text-surface-400 hover:text-surface-200 text-lg">&times;</button>
          </div>
        </div>
        <div className="flex-1 overflow-y-auto p-5 space-y-5">
          {data.error && (
            <div className="text-xs text-red-400 bg-red-500/10 rounded-lg px-3 py-2">
              Error: {data.error}
            </div>
          )}

          {/* AI Summary tab — cross-case synthesis output */}
          {(activeTab === 'ai' || isLegacy) && data.output && (
            <div>
              <h4 className="text-sm font-semibold text-surface-700 dark:text-surface-300 mb-2">
                LE Assessment
              </h4>
              <pre className="text-sm text-surface-800 dark:text-surface-200 whitespace-pre-wrap font-mono leading-relaxed bg-surface-50 dark:bg-surface-900/50 rounded-lg p-4">
                {data.output}
              </pre>
            </div>
          )}

          {/* Per-Entry tab — accordion per entry with Stage 1 extraction output */}
          {activeTab === 'entries' && entries.length > 0 && (
            <div>
              <h4 className="text-sm font-semibold text-surface-700 dark:text-surface-300 mb-2">
                Per-Entry Extractions
              </h4>
              <div className="space-y-2">
                {entries.map((entry, idx) => (
                  <div key={entry.id} className="border border-surface-200 dark:border-surface-700 rounded-lg overflow-hidden">
                    <button
                      onClick={() => setExpandedEntry(expandedEntry === idx ? null : idx)}
                      className="w-full flex items-center justify-between px-4 py-2.5 bg-surface-50 dark:bg-surface-900/50 hover:bg-surface-100 dark:hover:bg-surface-900/80 transition-colors text-left"
                    >
                      <div className="flex items-center gap-3 min-w-0">
                        <span className="text-xs font-mono text-gold-500">#{idx + 1}</span>
                        <span className="text-sm text-surface-700 dark:text-surface-300 truncate">{entry.label}</span>
                        <span className="text-[10px] text-surface-400 shrink-0">
                          {(entry.files || []).length} file{(entry.files || []).length !== 1 ? 's' : ''}
                        </span>
                        {entry.ai_status === 'complete' && (
                          <span className="text-[10px] text-emerald-400 shrink-0">extracted</span>
                        )}
                        {entry.ai_status === 'error' && (
                          <span className="text-[10px] text-red-400 shrink-0">failed</span>
                        )}
                      </div>
                      <svg className={`w-4 h-4 text-surface-400 transition-transform ${expandedEntry === idx ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                      </svg>
                    </button>
                    {expandedEntry === idx && (
                      <div className="px-4 py-3 border-t border-surface-200 dark:border-surface-700">
                        {/* File list */}
                        <div className="flex flex-wrap gap-1 mb-2">
                          {(entry.files || []).map((f) => {
                            const ext = (f.filename || '').split('.').pop()?.toUpperCase() || 'FILE';
                            return (
                              <span key={f.file_id} className="text-[10px] px-1.5 py-0.5 rounded bg-surface-200 dark:bg-surface-700 text-surface-500 dark:text-surface-400">
                                {f.filename} ({(f.file_size / 1024).toFixed(0)} KB)
                              </span>
                            );
                          })}
                        </div>
                        <pre className="text-xs text-surface-800 dark:text-surface-200 whitespace-pre-wrap font-mono leading-relaxed max-h-96 overflow-y-auto">
                          {entry.ai_output || '(Not yet extracted)'}
                        </pre>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Legacy per-PDF extracted text (accordion) */}
          {isLegacy && perCase.length > 0 && (
            <div>
              <h4 className="text-sm font-semibold text-surface-700 dark:text-surface-300 mb-2">
                Extracted PDF Text (Legacy)
              </h4>
              <div className="space-y-2">
                {perCase.map((pc, idx) => (
                  <div key={idx} className="border border-surface-200 dark:border-surface-700 rounded-lg overflow-hidden">
                    <button
                      onClick={() => setExpandedEntry(expandedEntry === idx ? null : idx)}
                      className="w-full flex items-center justify-between px-4 py-2.5 bg-surface-50 dark:bg-surface-900/50 hover:bg-surface-100 dark:hover:bg-surface-900/80 transition-colors text-left"
                    >
                      <div className="flex items-center gap-3 min-w-0">
                        <span className="text-xs font-mono text-gold-500">PDF {idx + 1}</span>
                        <span className="text-sm text-surface-700 dark:text-surface-300 truncate">{pc.filename}</span>
                        <span className="text-[10px] text-surface-400 shrink-0">{pc.page_count}p</span>
                        <span className="text-[10px] text-surface-400 shrink-0">{((pc.text_length || 0) / 1024).toFixed(1)}KB</span>
                      </div>
                      <svg className={`w-4 h-4 text-surface-400 transition-transform ${expandedEntry === idx ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                      </svg>
                    </button>
                    {expandedEntry === idx && (
                      <div className="px-4 py-3 border-t border-surface-200 dark:border-surface-700">
                        <pre className="text-xs text-surface-800 dark:text-surface-200 whitespace-pre-wrap font-mono leading-relaxed max-h-96 overflow-y-auto">
                          {pc.extracted_text || 'No text extracted.'}
                        </pre>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}


// ── Future Section Placeholder ───────────────────────────────────

function FutureSectionCard({ sectionKey, caseData, subjectIndex }) {
  const { token } = useAuth();
  const section = caseData.sections?.[sectionKey] || {};
  const status = section.status || 'empty';

  async function handleMarkNone() {
    try {
      await ingestionApi.markSectionNone(token, caseData.case_id, sectionKey, subjectIndex);
    } catch (err) {
      console.error('Failed to mark none:', err);
    }
  }

  async function handleReopen() {
    try {
      await ingestionApi.reopenSection(token, caseData.case_id, sectionKey, subjectIndex);
    } catch (err) {
      console.error('Failed to reopen:', err);
    }
  }

  return (
    <div className="bg-surface-100/50 dark:bg-surface-800/50 rounded-xl p-4 border border-surface-200/50 dark:border-surface-700/50">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <h4 className="text-sm font-medium text-surface-500 dark:text-surface-400">
            {SECTION_LABELS[sectionKey]}
          </h4>
          {status === 'empty' && (
            <span className="text-[10px] px-2 py-0.5 rounded-full bg-surface-200 dark:bg-surface-700 text-surface-400">
              Future phase
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          <StatusDot status={status} />
          {status === 'empty' && (
            <button
              onClick={handleMarkNone}
              className="text-[10px] text-surface-400 hover:text-surface-600 dark:hover:text-surface-300 transition-colors"
            >
              No Data
            </button>
          )}
          {status === 'none' && (
            <button
              onClick={handleReopen}
              className="text-[10px] text-surface-400 hover:text-surface-600 dark:hover:text-surface-300 transition-colors"
            >
              Reopen
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

// ── Subject Progress Header (Multi-User) ─────────────────────────

function SubjectProgressHeader({ subjects, currentSubjectIndex, viewingSubjectIndex, onSelectSubject }) {
  if (!subjects || subjects.length === 0) return null;

  return (
    <div className="bg-surface-100 dark:bg-surface-800 rounded-xl p-4 border border-surface-200 dark:border-surface-700">
      <div className="flex items-center gap-2 mb-2">
        <h4 className="text-sm font-semibold text-surface-600 dark:text-surface-300">Subject Progress</h4>
        <span className="text-xs text-surface-400">
          ({subjects.filter((s) => s.status === 'complete').length} of {subjects.length} complete)
        </span>
      </div>
      <div className="flex flex-wrap gap-2">
        {subjects.map((subj, idx) => {
          const isCurrent = idx === currentSubjectIndex;
          const isViewing = idx === (viewingSubjectIndex ?? currentSubjectIndex);
          const statusColors = {
            complete: 'bg-emerald-500/20 border-emerald-500/40 text-emerald-400',
            in_progress: 'bg-gold-500/20 border-gold-500/40 text-gold-400',
            pending: 'bg-surface-200 dark:bg-surface-700 border-surface-300 dark:border-surface-600 text-surface-400',
          };
          const colorClass = statusColors[subj.status] || statusColors.pending;
          const canClick = subj.status === 'complete' || isCurrent;

          return (
            <button
              key={idx}
              type="button"
              onClick={() => canClick && onSelectSubject(isCurrent ? null : idx)}
              disabled={!canClick}
              className={`
                inline-flex items-center gap-2 px-3 py-1.5 rounded-lg border text-xs font-medium transition-colors
                ${colorClass}
                ${isViewing ? 'ring-2 ring-gold-500/50' : ''}
                ${canClick ? 'cursor-pointer hover:brightness-110' : 'cursor-default opacity-60'}
              `}
            >
              <span className="font-semibold">
                {subj.label || `Subject ${idx + 1}`}
              </span>
              {subj.user_id && (
                <span className="font-mono text-[10px] opacity-80">{subj.user_id}</span>
              )}
              {subj.status === 'complete' && (
                <span className="text-[10px]">
                  {subj.sections_complete}/{subj.sections_total}
                </span>
              )}
              {subj.status === 'in_progress' && (
                <span className="text-[10px]">
                  {subj.sections_complete}/{subj.sections_total}
                </span>
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
}

// ── Subject UID Entry Form (Multi-User) ──────────────────────────

function SubjectUidEntryForm({ subjectIndex, caseId, onComplete }) {
  const { token } = useAuth();
  const [uid, setUid] = useState('');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  async function handleSubmit(e) {
    e.preventDefault();
    if (!uid.trim()) return;
    setSaving(true);
    setError('');
    try {
      await ingestionApi.setSubjectUid(token, caseId, subjectIndex, uid.trim());
      onComplete();
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="bg-surface-100 dark:bg-surface-800 rounded-xl p-5 border border-gold-500/30">
      <h4 className="text-base font-semibold text-surface-900 dark:text-surface-100 mb-2">
        Enter UID for Subject {subjectIndex + 1}
      </h4>
      <p className="text-sm text-surface-400 mb-3">
        The previous subject has been submitted. Enter the UID for the next subject to begin ingestion.
      </p>
      <form onSubmit={handleSubmit} className="flex items-center gap-3">
        <input
          type="text"
          value={uid}
          onChange={(e) => setUid(e.target.value)}
          placeholder="e.g. BIN-12345678"
          className="flex-1 max-w-sm px-3 py-2 rounded-lg bg-white dark:bg-surface-900 border border-surface-300 dark:border-surface-600 text-surface-900 dark:text-surface-100 placeholder-surface-400 font-mono text-sm focus:outline-none focus:ring-2 focus:ring-gold-500/50 focus:border-gold-500"
        />
        <button
          type="submit"
          disabled={saving || !uid.trim()}
          className="px-4 py-2 rounded-lg bg-gold-500 hover:bg-gold-600 text-surface-900 font-semibold text-sm transition-colors disabled:opacity-50"
        >
          {saving ? 'Setting...' : 'Set UID & Begin Ingestion'}
        </button>
      </form>
      {error && <p className="text-sm text-red-500 dark:text-red-400 mt-2">{error}</p>}
    </div>
  );
}

// ── Assembly Confirmation Modal ──────────────────────────────────

function AssemblyConfirmModal({ onConfirm, onCancel, assembling }) {
  useEffect(() => {
    function handleKey(e) {
      if (e.key === 'Escape' && !assembling) onCancel();
    }
    window.addEventListener('keydown', handleKey);
    return () => window.removeEventListener('keydown', handleKey);
  }, [onCancel, assembling]);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60" onClick={assembling ? undefined : onCancel}>
      <div
        className="bg-white dark:bg-surface-800 rounded-2xl w-[90%] max-w-md flex flex-col border border-surface-200 dark:border-surface-700 shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="p-6">
          <h3 className="text-lg font-semibold text-surface-900 dark:text-surface-100 mb-3">
            Finalize Case
          </h3>
          <p className="text-sm text-surface-600 dark:text-surface-300 leading-relaxed">
            This will assemble all ingested data into an investigation case. The ingestion data will be
            finalized and you will not be able to edit it after this point.
          </p>
          <p className="text-sm text-surface-600 dark:text-surface-300 mt-2">
            The case will appear in your Investigations list, ready to open and investigate.
          </p>
        </div>
        <div className="flex items-center justify-end gap-3 px-6 pb-6">
          <button
            onClick={onCancel}
            disabled={assembling}
            className="px-4 py-2 rounded-xl text-sm font-medium border border-surface-300 dark:border-surface-600 text-surface-600 dark:text-surface-300 hover:bg-surface-100 dark:hover:bg-surface-700 transition-colors disabled:opacity-50"
          >
            Cancel
          </button>
          <button
            onClick={onConfirm}
            disabled={assembling}
            className="px-5 py-2 rounded-xl text-sm font-bold bg-gold-500 hover:bg-gold-600 text-surface-900 transition-colors disabled:opacity-70"
          >
            {assembling ? 'Assembling...' : 'Confirm & Finalize'}
          </button>
        </div>
      </div>
    </div>
  );
}

// ── Main Page ────────────────────────────────────────────────────

export default function IngestionPage() {
  const { token } = useAuth();
  const navigate = useNavigate();
  const [caseData, setCaseData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showAssemblyConfirm, setShowAssemblyConfirm] = useState(false);
  const [assembling, setAssembling] = useState(false);
  const [assemblyPreview, setAssemblyPreview] = useState(null);
  const [loadingPreview, setLoadingPreview] = useState(false);
  const [resetting, setResetting] = useState(false);
  const [confirmReset, setConfirmReset] = useState(false);

  // Multi-user state
  const [viewingSubjectIndex, setViewingSubjectIndex] = useState(null);
  const [submittingSubject, setSubmittingSubject] = useState(false);
  // showUidEntry removed — UID comes from C360 upload automatically

  // Multi-user derived state
  const isMulti = caseData?.case_mode === 'multi';
  const currentSubjectIndex = isMulti ? (caseData.current_subject_index ?? 0) : null;
  const activeSubjectIndex = isMulti ? (viewingSubjectIndex ?? currentSubjectIndex) : null;
  const isViewingCompleted = isMulti && viewingSubjectIndex != null && viewingSubjectIndex !== currentSubjectIndex;

  // Build effective sections — for multi-user, pull from subjects array
  const effectiveSections = isMulti
    ? caseData?.subjects?.[activeSubjectIndex]?.sections ?? {}
    : caseData?.sections ?? {};

  // Build effective caseData to pass to section components
  const effectiveCaseData = caseData
    ? { ...caseData, sections: effectiveSections }
    : null;

  // Fetch active case on mount
  useEffect(() => {
    async function fetchActive() {
      try {
        const result = await ingestionApi.getActiveCase(token);
        if (result.case_id) {
          setCaseData(result);
        }
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    fetchActive();
  }, [token]);

  // Polling callback — refresh case data during processing
  const handleStatusUpdate = useCallback(
    async (status) => {
      const sections = status.sections || {};
      const anyProcessing = Object.values(sections).some((s) => s.status === 'processing');

      // Update multi-user metadata from status polling
      if (status.case_mode === 'multi') {
        setCaseData((prev) => {
          if (!prev) return prev;
          return {
            ...prev,
            current_subject_index: status.current_subject_index,
            subjects: status.subjects?.map((summary, i) => ({
              ...prev.subjects?.[i],
              ...summary,
            })) ?? prev.subjects,
          };
        });
      }

      // Update AI progress in real-time from status polling
      if (caseData?.case_id && sections.c360) {
        const c360Status = sections.c360;
        if (c360Status.ai_status && c360Status.ai_status !== 'pending') {
          setCaseData((prev) => {
            if (!prev) return prev;
            // For multi-user, update the current subject's c360 in the subjects array
            if (prev.case_mode === 'multi') {
              const si = prev.current_subject_index ?? 0;
              const updatedSubjects = [...(prev.subjects || [])];
              if (updatedSubjects[si]?.sections?.c360) {
                updatedSubjects[si] = {
                  ...updatedSubjects[si],
                  sections: {
                    ...updatedSubjects[si].sections,
                    c360: {
                      ...updatedSubjects[si].sections.c360,
                      ai_status: c360Status.ai_status,
                      ai_progress: c360Status.ai_progress || {},
                    },
                  },
                };
              }
              return { ...prev, subjects: updatedSubjects };
            }
            // Single-user: existing behavior
            return {
              ...prev,
              sections: {
                ...prev.sections,
                c360: {
                  ...prev.sections?.c360,
                  ai_status: c360Status.ai_status,
                  ai_progress: c360Status.ai_progress || {},
                },
              },
            };
          });
        }
      }

      if (!anyProcessing && caseData?.case_id) {
        try {
          const full = await ingestionApi.getCase(token, caseData.case_id);
          setCaseData(full);
        } catch (err) {
          console.error('Failed to refresh case:', err);
        }
      }
    },
    [token, caseData?.case_id]
  );

  const { startPolling } = useIngestionStatus(
    token,
    caseData?.case_id || null,
    handleStatusUpdate,
  );

  function handleCaseCreated(newCase) {
    setCaseData(newCase);
  }

  function handleProcessingStarted() {
    startPolling();
    if (caseData?.case_id) {
      ingestionApi.getCase(token, caseData.case_id).then(setCaseData).catch(() => {});
    }
  }

  async function handleAssemble() {
    setAssembling(true);
    try {
      await ingestionApi.assembleCase(token, caseData.case_id);
      navigate('/cases');
    } catch (err) {
      setError(err.message);
      setShowAssemblyConfirm(false);
    } finally {
      setAssembling(false);
    }
  }

  async function handlePreviewAssembly() {
    setLoadingPreview(true);
    try {
      const result = await ingestionApi.previewAssembly(token, caseData.case_id);
      setAssemblyPreview(result.assembled_case_data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoadingPreview(false);
    }
  }

  async function handleReset() {
    setResetting(true);
    try {
      await ingestionApi.deleteCase(token, caseData.case_id);
      setCaseData(null);
      setConfirmReset(false);
      setViewingSubjectIndex(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setResetting(false);
    }
  }

  // Submit current subject and advance to next
  async function handleSubmitSubject() {
    setSubmittingSubject(true);
    setError('');
    try {
      await ingestionApi.submitSubject(token, caseData.case_id);
      // Re-fetch full case — next subject's sections will be populated by backend
      setViewingSubjectIndex(null);
      const full = await ingestionApi.getCase(token, caseData.case_id);
      setCaseData(full);
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmittingSubject(false);
    }
  }

  // Check if assembly is possible
  const canAssemble = (() => {
    if (!caseData) return false;
    if (isMulti) {
      // For multi-user, backend sets status to "ready" when all subjects are complete
      return caseData.status === 'ready';
    }
    // Single-user: check sections
    if (!caseData.sections) return false;
    const required = [
      'c360', 'elliptic', 'hexa_dump', 'raw_hex_dump', 'previous_icrs',
      'rfis', 'kyc', 'l1_victim', 'l1_suspect', 'kodex',
    ];
    return required.every((key) => {
      const s = caseData.sections[key]?.status;
      return s === 'complete' || s === 'none' || s === 'extracted';
    });
  })();

  // For multi-user: check if current subject's sections are all terminal
  const canSubmitSubject = isMulti && !isViewingCompleted && (() => {
    const required = [
      'c360', 'elliptic', 'hexa_dump', 'raw_hex_dump', 'previous_icrs',
      'rfis', 'kyc', 'l1_victim', 'l1_suspect', 'kodex',
    ];
    return required.every((key) => {
      const s = effectiveSections[key]?.status;
      return s === 'complete' || s === 'none' || s === 'extracted';
    });
  })();

  if (loading) {
    return (
      <AppLayout>
        <div className="flex justify-center py-20">
          <LoadingSpinner size="lg" />
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout>
      <div className="max-w-7xl mx-auto px-6 py-6 animate-fade-in">
        {/* Page header */}
        <div className="flex items-start justify-between mb-6">
          <div>
            <h2 className="text-2xl font-bold text-surface-900 dark:text-surface-100">
              Data Ingestion
            </h2>
            {caseData && (
              <div className="flex items-center gap-3 mt-1">
                <span className="text-sm font-mono text-surface-500">{caseData.case_id}</span>
                <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-surface-200 dark:bg-surface-700 text-surface-600 dark:text-surface-300">
                  {caseData.status}
                </span>
                {isMulti && (
                  <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-blue-500/20 text-blue-400 border border-blue-500/30">
                    Multi-User ({caseData.total_subjects || caseData.subjects?.length || 0} subjects)
                  </span>
                )}
              </div>
            )}
          </div>
          {caseData && (
            <div className="flex items-center gap-2">
              {!confirmReset ? (
                <button
                  onClick={() => setConfirmReset(true)}
                  className="px-3 py-1.5 rounded-lg text-xs font-medium border border-red-500/30 text-red-500 hover:bg-red-500/10 transition-colors"
                >
                  Reset Case
                </button>
              ) : (
                <div className="flex items-center gap-2">
                  <span className="text-xs text-red-400">Clear all data?</span>
                  <button
                    onClick={handleReset}
                    disabled={resetting}
                    className="px-3 py-1.5 rounded-lg text-xs font-medium bg-red-500 hover:bg-red-600 text-white transition-colors disabled:opacity-50"
                  >
                    {resetting ? 'Resetting...' : 'Confirm'}
                  </button>
                  <button
                    onClick={() => setConfirmReset(false)}
                    className="px-3 py-1.5 rounded-lg text-xs font-medium border border-surface-300 dark:border-surface-600 text-surface-500 hover:text-surface-700 dark:hover:text-surface-300 transition-colors"
                  >
                    Cancel
                  </button>
                </div>
              )}
            </div>
          )}
        </div>

        {error && (
          <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-4 text-sm text-red-500 dark:text-red-400 mb-6">
            {error}
            <button onClick={() => setError('')} className="ml-2 underline">Dismiss</button>
          </div>
        )}

        {/* No active case — show creation form */}
        {!caseData && <CaseCreationForm onCreated={handleCaseCreated} />}

        {/* Multi-user: Subject progress header */}
        {caseData && isMulti && (
          <SubjectProgressHeader
            subjects={caseData.subjects}
            currentSubjectIndex={currentSubjectIndex}
            viewingSubjectIndex={viewingSubjectIndex}
            onSelectSubject={(idx) => setViewingSubjectIndex(idx === currentSubjectIndex ? null : idx)}
          />
        )}

        {/* Multi-user: read-only banner when viewing completed subject */}
        {isViewingCompleted && (
          <div className="bg-blue-500/10 border border-blue-500/20 rounded-xl p-3 text-sm text-blue-400 flex items-center justify-between">
            <span>Viewing completed Subject {viewingSubjectIndex + 1} (read-only)</span>
            <button
              onClick={() => setViewingSubjectIndex(null)}
              className="text-xs underline hover:text-blue-300"
            >
              Return to current subject
            </button>
          </div>
        )}

        {/* Active case — show ingestion sections */}
        {caseData && (
          <div key={activeSubjectIndex ?? 'single'} className="space-y-4">
            {/* C360 */}
            <C360Section
              caseData={effectiveCaseData}
              onProcessingStarted={handleProcessingStarted}
              subjectIndex={activeSubjectIndex}
            />

            {/* Additional UIDs + Wallets (appears after C360 completes) */}
            <AdditionalInputsSection
              caseData={effectiveCaseData}
              onSaved={handleProcessingStarted}
              subjectIndex={activeSubjectIndex}
            />

            {/* Elliptic */}
            <EllipticSection
              caseData={effectiveCaseData}
              onProcessingStarted={handleProcessingStarted}
              subjectIndex={activeSubjectIndex}
            />

            {/* L1 Referral Narrative */}
            <TextAISection
              sectionKey="hexa_dump"
              caseData={effectiveCaseData}
              placeholder="Paste the L1 referral narrative here..."
              onSaved={handleProcessingStarted}
              subjectIndex={activeSubjectIndex}
            />

            {/* HaoDesk Case Data */}
            <TextAISection
              sectionKey="raw_hex_dump"
              caseData={effectiveCaseData}
              placeholder="Paste the HaoDesk case data here..."
              onSaved={handleProcessingStarted}
              subjectIndex={activeSubjectIndex}
            />

            {/* KYC Document Summary (image-only) */}
            <KYCSection
              caseData={effectiveCaseData}
              onSaved={handleProcessingStarted}
              subjectIndex={activeSubjectIndex}
            />

            {/* Prior ICR Summary (iterative entries) */}
            <IterativeEntrySection
              sectionKey="previous_icrs"
              caseData={effectiveCaseData}
              placeholder="Paste a prior ICR here (one at a time)..."
              onSaved={handleProcessingStarted}
              showTotalCount
              subjectIndex={activeSubjectIndex}
            />

            {/* RFI Summary (iterative entries with images) */}
            <RFIEntrySection
              caseData={effectiveCaseData}
              onSaved={handleProcessingStarted}
              showTotalCount
              subjectIndex={activeSubjectIndex}
            />

            {/* Kodex / LE Cases */}
            <KodexEntrySection
              caseData={effectiveCaseData}
              onSaved={handleProcessingStarted}
              subjectIndex={activeSubjectIndex}
            />

            {/* L1 Victim Communications */}
            <TextImageSection
              sectionKey="l1_victim"
              caseData={effectiveCaseData}
              placeholder="Paste victim communications here — chat transcripts, case notes, screenshots. Embedded images will be auto-extracted..."
              onSaved={handleProcessingStarted}
              subjectIndex={activeSubjectIndex}
            />

            {/* L1 Suspect Communications */}
            <TextImageSection
              sectionKey="l1_suspect"
              caseData={effectiveCaseData}
              placeholder="Paste suspect communications here — chat transcripts, case notes, screenshots. Embedded images will be auto-extracted..."
              onSaved={handleProcessingStarted}
              subjectIndex={activeSubjectIndex}
            />

            {/* Notes */}
            <NotesSection
              caseData={effectiveCaseData}
              onSaved={handleProcessingStarted}
              subjectIndex={activeSubjectIndex}
            />

            {/* Multi-user: Submit Subject & Continue */}
            {isMulti && !isViewingCompleted && (
              <div className="pt-4 border-t border-surface-200 dark:border-surface-700">
                <button
                  onClick={handleSubmitSubject}
                  disabled={!canSubmitSubject || submittingSubject}
                  className="w-full px-5 py-3 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-base transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
                >
                  {submittingSubject
                    ? 'Submitting...'
                    : `Submit Subject ${currentSubjectIndex + 1} & Continue`}
                </button>
                {!canSubmitSubject && (
                  <p className="text-xs text-surface-400 mt-2 text-center">
                    All sections must be complete or marked N/A before submitting this subject.
                  </p>
                )}
              </div>
            )}

            {/* Assembly */}
            {(!isMulti || canAssemble) && !isViewingCompleted && (
              <div className="pt-4 border-t border-surface-200 dark:border-surface-700">
                <div className="flex gap-3">
                  <button
                    onClick={handlePreviewAssembly}
                    disabled={!canAssemble || loadingPreview}
                    className="flex-1 px-5 py-3 rounded-xl border border-surface-300 dark:border-surface-600 text-surface-700 dark:text-surface-300 hover:bg-surface-200 dark:hover:bg-surface-700 font-semibold text-base transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
                  >
                    {loadingPreview ? 'Loading...' : 'Preview Case Document'}
                  </button>
                  <button
                    onClick={() => setShowAssemblyConfirm(true)}
                    disabled={!canAssemble || assembling}
                    className="flex-1 px-5 py-3 rounded-xl bg-gold-500 hover:bg-gold-600 text-surface-900 font-bold text-base transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
                  >
                    Assemble Case Data
                  </button>
                </div>
                {!canAssemble && (
                  <p className="text-xs text-surface-400 mt-2 text-center">
                    {isMulti
                      ? 'All subjects must be submitted before assembly.'
                      : 'All sections must be complete or marked N/A before assembly.'}
                  </p>
                )}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Assembly confirmation modal */}
      {showAssemblyConfirm && (
        <AssemblyConfirmModal
          onConfirm={handleAssemble}
          onCancel={() => setShowAssemblyConfirm(false)}
          assembling={assembling}
        />
      )}

      {/* Assembly preview modal */}
      {assemblyPreview !== null && (
        <PreviewModal
          title="Case Document Preview"
          content={assemblyPreview}
          onClose={() => setAssemblyPreview(null)}
        />
      )}
    </AppLayout>
  );
}
