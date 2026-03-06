import { useEffect, useState, useCallback, useRef } from 'react';
import { useAuth } from '../context/AuthContext';
import AppLayout from '../components/AppLayout';
import LoadingSpinner from '../components/shared/LoadingSpinner';
import useIngestionStatus from '../hooks/useIngestionStatus';
import * as ingestionApi from '../services/ingestion_api';

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
  investigator_notes: 'Investigator Notes',
};


// ── Status Indicator ─────────────────────────────────────────────

function StatusDot({ status }) {
  const config = {
    empty: { color: 'bg-surface-500', label: 'Empty' },
    processing: { color: 'bg-gold-400 animate-pulse', label: 'Processing' },
    complete: { color: 'bg-emerald-500', label: 'Complete' },
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
            PROCESSOR_ORDER.map((pid) => (
              <ProcessorSection
                key={pid}
                processorId={pid}
                processorOutputs={processorOutputs}
                aiOutputs={aiOutputs}
              />
            ))
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

function PreviewButton({ token, caseId, sectionKey, label }) {
  const [loading, setLoading] = useState(false);
  const [preview, setPreview] = useState(null);

  async function handleClick() {
    setLoading(true);
    try {
      const data = await ingestionApi.getSectionOutput(token, caseId, sectionKey);
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

function C360PreviewButton({ token, caseId, label }) {
  const [loading, setLoading] = useState(false);
  const [previewData, setPreviewData] = useState(null);

  async function handleClick() {
    setLoading(true);
    try {
      const data = await ingestionApi.getC360Output(token, caseId);
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
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState('');

  async function handleSubmit(e) {
    e.preventDefault();
    if (!caseId.trim()) return;
    setCreating(true);
    setError('');
    try {
      const result = await ingestionApi.createCase(token, caseId.trim());
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

function C360Section({ caseData, onProcessingStarted }) {
  const { token } = useAuth();
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const [dragging, setDragging] = useState(false);
  const fileInputRef = useRef(null);

  // Quick info returned synchronously from upload
  const [quickInfo, setQuickInfo] = useState(null);

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
      const result = await ingestionApi.uploadC360(token, caseData.case_id, files);
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
            />
          )}
          <StatusDot status={status} />
        </div>
      </div>

      {status === 'empty' && (
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
          {error && <p className="text-sm text-red-500 dark:text-red-400 mb-3">{error}</p>}
          <button
            onClick={handleUpload}
            disabled={uploading || !files.length}
            className="px-4 py-1.5 rounded-lg bg-gold-500 hover:bg-gold-600 text-surface-900 font-semibold text-sm transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {uploading ? 'Uploading...' : 'Upload & Process'}
          </button>
        </>
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
          <CsvDownloadButton caseId={caseData.case_id} filename={c360.csv_filename} />
        </div>
      )}

      {status === 'error' && (
        <p className="text-sm text-red-500 dark:text-red-400">
          {c360.error_message || 'Processing failed.'}
        </p>
      )}
    </div>
  );
}

// ── CSV Download Button ──────────────────────────────────────────

function CsvDownloadButton({ caseId, filename }) {
  const { token } = useAuth();
  const [downloading, setDownloading] = useState(false);

  async function handleDownload() {
    setDownloading(true);
    try {
      const res = await fetch(ingestionApi.c360CsvUrl(caseId), {
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

function AdditionalInputsSection({ caseData, onSaved }) {
  const { token } = useAuth();

  const existingUids = caseData.coconspirator_uids || [];
  const existingWallets = caseData.sections?.elliptic?.manual_addresses || [];
  const hasSavedData = existingUids.length > 0 || existingWallets.length > 0;

  const [editing, setEditing] = useState(!hasSavedData);
  const [extraUids, setExtraUids] = useState(existingUids.join('\n'));
  const [extraWallets, setExtraWallets] = useState(existingWallets.join('\n'));
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  const c360Complete = caseData.sections?.c360?.status === 'complete';
  if (!c360Complete) return null;

  async function handleSave() {
    setSaving(true);
    setError('');
    try {
      // Save extra UIDs
      const uids = extraUids.split('\n').map((u) => u.trim()).filter(Boolean);
      await fetch(`/api/ingestion/cases/${caseData.case_id}/uids`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ coconspirator_uids: uids }),
      });

      // Save extra wallets
      const wallets = extraWallets.split('\n').map((w) => w.trim()).filter(Boolean);
      await ingestionApi.addManualAddresses(token, caseData.case_id, wallets);

      // Run address cross-reference (includes manual wallets vs UOL)
      await ingestionApi.runAddressXref(token, caseData.case_id);

      // Run UID search if UIDs were provided
      if (uids.length > 0) {
        await ingestionApi.runUidSearch(token, caseData.case_id);
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
        </div>
      )}

      {editing && (
        <>
          <p className="text-sm text-surface-400 mb-4">
            Optional. Add any additional UIDs of interest (victims, co-suspects) and extra wallet addresses not in the C360 data.
          </p>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-4">
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
    </div>
  );
}

// ── Elliptic Section ─────────────────────────────────────────────

function EllipticSection({ caseData, onProcessingStarted }) {
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
      await ingestionApi.submitElliptic(token, caseData.case_id);
      onProcessingStarted();
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  async function handleMarkNone() {
    try {
      await ingestionApi.markSectionNone(token, caseData.case_id, 'elliptic');
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
        <p className="text-xs text-surface-400">Marked as not applicable.</p>
      )}

      {ellStatus === 'error' && (
        <p className="text-sm text-red-500 dark:text-red-400">
          {elliptic.error_message || 'Screening failed.'}
        </p>
      )}
    </div>
  );
}

// ── Notes Section ────────────────────────────────────────────────

function NotesSection({ caseData }) {
  const { token } = useAuth();
  const [notes, setNotes] = useState(caseData.sections?.investigator_notes?.output || '');
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  const notesStatus = caseData.sections?.investigator_notes?.status || 'empty';

  async function handleSave() {
    setSaving(true);
    setSaved(false);
    try {
      await ingestionApi.saveNotes(token, caseData.case_id, notes);
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } catch (err) {
      console.error('Failed to save notes:', err);
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="bg-surface-100 dark:bg-surface-800 rounded-xl p-5 border border-surface-200 dark:border-surface-700">
      <div className="flex items-center justify-between mb-3">
        <h4 className="text-base font-semibold text-surface-900 dark:text-surface-100">
          {SECTION_LABELS.investigator_notes}
        </h4>
        <StatusDot status={notesStatus} />
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
          disabled={saving}
          className="px-4 py-1.5 rounded-lg bg-gold-500 hover:bg-gold-600 text-surface-900 font-semibold text-sm transition-colors disabled:opacity-50"
        >
          {saving ? 'Saving...' : 'Save Notes'}
        </button>
        {saved && <span className="text-xs text-emerald-500">Saved</span>}
      </div>
    </div>
  );
}

// ── Text Section with AI Processing ──────────────────────────────

function TextAISection({ sectionKey, caseData, placeholder, onSaved }) {
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
      await ingestionApi.saveTextSection(token, caseData.case_id, sectionKey, text);
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
      await ingestionApi.saveTextSection(token, caseData.case_id, sectionKey, '');
      setText('');
      if (onSaved) onSaved();
    } catch (err) {
      console.error(`Failed to reset ${sectionKey}:`, err);
    }
  }

  async function handlePreview() {
    try {
      const data = await ingestionApi.getTextSection(token, caseData.case_id, sectionKey);
      setPreviewData(data);
      setPreviewTab('ai');
      setShowPreview(true);
    } catch (err) {
      console.error(`Failed to load preview for ${sectionKey}:`, err);
    }
  }

  async function handleMarkNone() {
    try {
      await ingestionApi.markSectionNone(token, caseData.case_id, sectionKey);
      if (onSaved) onSaved();
    } catch (err) {
      console.error(`Failed to mark ${sectionKey} N/A:`, err);
    }
  }

  if (isNone) {
    async function handleReopen() {
      try {
        await ingestionApi.reopenSection(token, caseData.case_id, sectionKey);
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

function IterativeEntrySection({ sectionKey, caseData, placeholder, onSaved }) {
  const { token } = useAuth();
  const section = caseData.sections?.[sectionKey] || {};
  const [text, setText] = useState('');
  const [adding, setAdding] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [showPreview, setShowPreview] = useState(false);
  const [previewData, setPreviewData] = useState(null);
  const [previewTab, setPreviewTab] = useState('ai');

  const entries = section.entries || [];
  const status = section.status || 'empty';
  const aiStatus = section.ai_status;
  const isComplete = status === 'complete';
  const isNone = status === 'none';

  async function handleMarkNone() {
    try {
      await ingestionApi.markSectionNone(token, caseData.case_id, sectionKey);
      if (onSaved) onSaved();
    } catch (err) {
      console.error(`Failed to mark ${sectionKey} N/A:`, err);
    }
  }

  async function handleAddEntry() {
    if (!text.trim()) return;
    setAdding(true);
    try {
      await ingestionApi.addEntry(token, caseData.case_id, sectionKey, text);
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
      await ingestionApi.removeEntry(token, caseData.case_id, sectionKey, entryId);
      if (onSaved) onSaved();
    } catch (err) {
      console.error(`Failed to remove entry:`, err);
    }
  }

  async function handleProcess() {
    setProcessing(true);
    try {
      if (text.trim()) {
        await ingestionApi.addEntry(token, caseData.case_id, sectionKey, text);
      }
      await ingestionApi.processEntries(token, caseData.case_id, sectionKey);
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
        await ingestionApi.removeEntry(token, caseData.case_id, sectionKey, entry.id);
      }
      setText('');
      if (onSaved) onSaved();
    } catch (err) {
      console.error(`Failed to reset ${sectionKey}:`, err);
    }
  }

  async function handlePreview() {
    try {
      const data = await ingestionApi.getEntries(token, caseData.case_id, sectionKey);
      setPreviewData(data);
      setPreviewTab('ai');
      setShowPreview(true);
    } catch (err) {
      console.error(`Failed to load preview for ${sectionKey}:`, err);
    }
  }

  if (isNone) {
    async function handleReopen() {
      try {
        await ingestionApi.reopenSection(token, caseData.case_id, sectionKey);
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

function RFIEntrySection({ caseData, onSaved }) {
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

  const entries = section.entries || [];
  const status = section.status || 'empty';
  const aiStatus = section.ai_status;
  const isComplete = status === 'complete';
  const isNone = status === 'none';

  const fileInputRef = useRef(null);

  async function handleMarkNone() {
    try {
      await ingestionApi.markSectionNone(token, caseData.case_id, sectionKey);
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
        token, caseData.case_id, sectionKey, text, selectedFiles,
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
      await ingestionApi.removeEntry(token, caseData.case_id, sectionKey, entryId);
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
          token, caseData.case_id, sectionKey, text, selectedFiles,
        );
        setText('');
        setSelectedFiles([]);
      }
      await ingestionApi.processEntries(token, caseData.case_id, sectionKey);
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
        await ingestionApi.removeEntry(token, caseData.case_id, sectionKey, entry.id);
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
      const data = await ingestionApi.getEntries(token, caseData.case_id, sectionKey);
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
        await ingestionApi.reopenSection(token, caseData.case_id, sectionKey);
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


// ── Future Section Placeholder ───────────────────────────────────

function FutureSectionCard({ sectionKey, caseData }) {
  const { token } = useAuth();
  const section = caseData.sections?.[sectionKey] || {};
  const status = section.status || 'empty';

  async function handleMarkNone() {
    try {
      await ingestionApi.markSectionNone(token, caseData.case_id, sectionKey);
    } catch (err) {
      console.error('Failed to mark none:', err);
    }
  }

  async function handleReopen() {
    try {
      await ingestionApi.reopenSection(token, caseData.case_id, sectionKey);
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

// ── Assembled Output Modal ───────────────────────────────────────

function AssembledOutputModal({ caseId, markdown, onClose }) {
  const [copied, setCopied] = useState(false);

  function handleCopy() {
    navigator.clipboard.writeText(markdown);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  function handleDownload() {
    const blob = new Blob([markdown], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${caseId}_case_document.md`;
    a.click();
    URL.revokeObjectURL(url);
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
            Assembled Case Data
          </h3>
          <div className="flex items-center gap-2">
            <button
              onClick={handleDownload}
              className="px-3 py-1.5 rounded-lg text-xs font-medium bg-gold-500 hover:bg-gold-600 text-surface-900 transition-colors"
            >
              Download .md
            </button>
            <button
              onClick={handleCopy}
              className="px-3 py-1.5 rounded-lg text-xs font-medium border border-surface-300 dark:border-surface-600 text-surface-600 dark:text-surface-300 hover:bg-surface-100 dark:hover:bg-surface-700 transition-colors"
            >
              {copied ? 'Copied!' : 'Copy Markdown'}
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
            {markdown}
          </pre>
        </div>
      </div>
    </div>
  );
}

// ── Main Page ────────────────────────────────────────────────────

export default function IngestionPage() {
  const { token } = useAuth();
  const [caseData, setCaseData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [assembledMarkdown, setAssembledMarkdown] = useState(null);
  const [assembling, setAssembling] = useState(false);
  const [resetting, setResetting] = useState(false);
  const [confirmReset, setConfirmReset] = useState(false);

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

      // Update AI progress in real-time from status polling
      if (caseData?.case_id && sections.c360) {
        const c360Status = sections.c360;
        if (c360Status.ai_status && c360Status.ai_status !== 'pending') {
          setCaseData((prev) => {
            if (!prev) return prev;
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
      const result = await ingestionApi.assembleCase(token, caseData.case_id);
      setAssembledMarkdown(result.assembled_case_data);
    } catch (err) {
      setError(err.message);
    } finally {
      setAssembling(false);
    }
  }

  async function handleReset() {
    setResetting(true);
    try {
      await ingestionApi.deleteCase(token, caseData.case_id);
      setCaseData(null);
      setConfirmReset(false);
    } catch (err) {
      setError(err.message);
    } finally {
      setResetting(false);
    }
  }

  // Check if assembly is possible
  const canAssemble = caseData?.sections && (() => {
    const required = [
      'c360', 'elliptic', 'hexa_dump', 'raw_hex_dump', 'previous_icrs',
      'rfis', 'kyc', 'l1_victim', 'l1_suspect', 'kodex',
    ];
    return required.every((key) => {
      const s = caseData.sections[key]?.status;
      return s === 'complete' || s === 'none';
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

        {/* Active case — show ingestion sections */}
        {caseData && (
          <div className="space-y-4">
            {/* C360 */}
            <C360Section
              caseData={caseData}
              onProcessingStarted={handleProcessingStarted}
            />

            {/* Additional UIDs + Wallets (appears after C360 completes) */}
            <AdditionalInputsSection
              caseData={caseData}
              onSaved={handleProcessingStarted}
            />

            {/* Elliptic */}
            <EllipticSection
              caseData={caseData}
              onProcessingStarted={handleProcessingStarted}
            />

            {/* L1 Referral Narrative */}
            <TextAISection
              sectionKey="hexa_dump"
              caseData={caseData}
              placeholder="Paste the L1 referral narrative here..."
              onSaved={handleProcessingStarted}
            />

            {/* HaoDesk Case Data */}
            <TextAISection
              sectionKey="raw_hex_dump"
              caseData={caseData}
              placeholder="Paste the HaoDesk case data here..."
              onSaved={handleProcessingStarted}
            />

            {/* KYC Document Summary (future — image-only input) */}
            <FutureSectionCard
              sectionKey="kyc"
              caseData={caseData}
            />

            {/* Prior ICR Summary (iterative entries) */}
            <IterativeEntrySection
              sectionKey="previous_icrs"
              caseData={caseData}
              placeholder="Paste a prior ICR here (one at a time)..."
              onSaved={handleProcessingStarted}
            />

            {/* RFI Summary (iterative entries with images) */}
            <RFIEntrySection
              caseData={caseData}
              onSaved={handleProcessingStarted}
            />

            {/* Remaining future phase sections */}
            {['kodex', 'l1_victim', 'l1_suspect'].map((key) => (
              <FutureSectionCard
                key={key}
                sectionKey={key}
                caseData={caseData}
              />
            ))}

            {/* Notes */}
            <NotesSection caseData={caseData} />

            {/* Assembly */}
            <div className="pt-4 border-t border-surface-200 dark:border-surface-700">
              <button
                onClick={handleAssemble}
                disabled={!canAssemble || assembling}
                className="w-full px-5 py-3 rounded-xl bg-gold-500 hover:bg-gold-600 text-surface-900 font-bold text-base transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
              >
                {assembling ? 'Assembling...' : 'Assemble Case Data'}
              </button>
              {!canAssemble && caseData.sections && (
                <p className="text-xs text-surface-400 mt-2 text-center">
                  All sections must be complete or marked N/A before assembly.
                </p>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Assembled output modal */}
      {assembledMarkdown && (
        <AssembledOutputModal
          caseId={caseData?.case_id || 'case'}
          markdown={assembledMarkdown}
          onClose={() => setAssembledMarkdown(null)}
        />
      )}
    </AppLayout>
  );
}
