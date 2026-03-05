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
  previous_icrs: 'Prior ICR Summary',
  rfis: 'RFI Summary',
  kyc: 'KYC Document Summary',
  l1_victim: 'L1 Victim Communications',
  l1_suspect: 'L1 Suspect Communications',
  kodex: 'Law Enforcement / Kodex',
  investigator_notes: 'Investigator Notes',
};

const FUTURE_SECTIONS = [
  'hexa_dump', 'previous_icrs', 'rfis', 'kyc',
  'l1_victim', 'l1_suspect', 'kodex',
];

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

// ── Case Creation Form ───────────────────────────────────────────

function CaseCreationForm({ onCreated }) {
  const { token } = useAuth();
  const [caseId, setCaseId] = useState('');
  const [subjectUid, setSubjectUid] = useState('');
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState('');

  async function handleSubmit(e) {
    e.preventDefault();
    if (!caseId.trim() || !subjectUid.trim()) return;
    setCreating(true);
    setError('');
    try {
      const result = await ingestionApi.createCase(token, caseId.trim(), subjectUid.trim());
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
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-4">
        <div>
          <label className="block text-sm font-medium text-surface-600 dark:text-surface-400 mb-1">
            HowDesk Case Number
          </label>
          <input
            type="text"
            value={caseId}
            onChange={(e) => setCaseId(e.target.value)}
            placeholder="CASE-2026-0451"
            className="w-full px-3 py-2 rounded-lg bg-white dark:bg-surface-900 border border-surface-300 dark:border-surface-600 text-surface-900 dark:text-surface-100 placeholder-surface-400 focus:outline-none focus:ring-2 focus:ring-gold-500/50 focus:border-gold-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-surface-600 dark:text-surface-400 mb-1">
            Subject UID
          </label>
          <input
            type="text"
            value={subjectUid}
            onChange={(e) => setSubjectUid(e.target.value)}
            placeholder="BIN-84729103"
            className="w-full px-3 py-2 rounded-lg bg-white dark:bg-surface-900 border border-surface-300 dark:border-surface-600 text-surface-900 dark:text-surface-100 placeholder-surface-400 focus:outline-none focus:ring-2 focus:ring-gold-500/50 focus:border-gold-500"
          />
        </div>
      </div>
      {error && (
        <p className="text-sm text-red-500 dark:text-red-400 mb-3">{error}</p>
      )}
      <button
        type="submit"
        disabled={creating || !caseId.trim() || !subjectUid.trim()}
        className="px-5 py-2 rounded-lg bg-gold-500 hover:bg-gold-600 text-surface-900 font-semibold text-sm transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {creating ? 'Creating...' : 'Create Case'}
      </button>
    </form>
  );
}

// ── C360 Upload Section ──────────────────────────────────────────

function C360Section({ caseData, onProcessingStarted }) {
  const { token } = useAuth();
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const fileInputRef = useRef(null);

  const c360 = caseData.sections?.c360 || {};
  const status = c360.status || 'empty';
  const isLocked = status === 'processing' || status === 'complete';

  async function handleUpload() {
    if (!files.length) return;
    setUploading(true);
    setError('');
    try {
      await ingestionApi.uploadC360(token, caseData.case_id, files);
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
    const selected = Array.from(e.target.files || []);
    const valid = selected.filter((f) => {
      const name = f.name.toLowerCase();
      return name.endsWith('.xlsx') || name.endsWith('.xls') || name.endsWith('.csv');
    });
    setFiles(valid);
  }

  return (
    <div className="bg-surface-100 dark:bg-surface-800 rounded-xl p-5 border border-surface-200 dark:border-surface-700">
      <div className="flex items-center justify-between mb-3">
        <h4 className="text-sm font-semibold text-surface-900 dark:text-surface-100">
          {SECTION_LABELS.c360}
        </h4>
        <StatusDot status={status} />
      </div>

      {status === 'empty' && (
        <>
          <div className="flex items-center gap-3 mb-3">
            <input
              ref={fileInputRef}
              type="file"
              multiple
              accept=".xlsx,.xls,.csv"
              onChange={handleFileChange}
              className="text-sm text-surface-500 file:mr-3 file:px-3 file:py-1.5 file:rounded-lg file:border-0 file:bg-surface-200 dark:file:bg-surface-700 file:text-surface-700 dark:file:text-surface-300 file:font-medium file:text-sm file:cursor-pointer hover:file:bg-surface-300 dark:hover:file:bg-surface-600"
            />
          </div>
          {files.length > 0 && (
            <p className="text-xs text-surface-400 mb-3">
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
        <div className="flex items-center gap-2 text-sm text-gold-500">
          <LoadingSpinner size="sm" />
          Processing C360 data...
        </div>
      )}

      {status === 'complete' && (
        <div className="space-y-2">
          <p className="text-sm text-emerald-500 dark:text-emerald-400">
            Processing complete. {(c360.detected_file_types || []).length} file types detected.
          </p>
          {(c360.warnings || []).length > 0 && (
            <div className="text-xs text-amber-500 space-y-1">
              {c360.warnings.map((w, i) => (
                <p key={i}>{w.message}</p>
              ))}
            </div>
          )}
          {c360.csv_content && (
            <CsvDownloadButton caseId={caseData.case_id} filename={c360.csv_filename} />
          )}
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

// ── Elliptic Section ─────────────────────────────────────────────

function EllipticSection({ caseData, onProcessingStarted }) {
  const { token } = useAuth();
  const [manualAddresses, setManualAddresses] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  const c360 = caseData.sections?.c360 || {};
  const elliptic = caseData.sections?.elliptic || {};
  const ellStatus = elliptic.status || 'empty';
  const c360Complete = c360.status === 'complete';

  async function handleSubmit() {
    setSubmitting(true);
    setError('');
    try {
      // Save manual addresses first if any
      const extras = manualAddresses
        .split('\n')
        .map((a) => a.trim())
        .filter(Boolean);
      if (extras.length > 0) {
        await ingestionApi.addManualAddresses(token, caseData.case_id, extras);
      }
      // Submit to Elliptic
      await ingestionApi.submitElliptic(token, caseData.case_id);
      setManualAddresses('');
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
      onProcessingStarted(); // trigger a refresh
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="bg-surface-100 dark:bg-surface-800 rounded-xl p-5 border border-surface-200 dark:border-surface-700">
      <div className="flex items-center justify-between mb-3">
        <h4 className="text-sm font-semibold text-surface-900 dark:text-surface-100">
          {SECTION_LABELS.elliptic}
        </h4>
        <StatusDot status={ellStatus} />
      </div>

      {!c360Complete && ellStatus === 'empty' && (
        <p className="text-xs text-surface-400">
          Upload C360 data first to extract wallet addresses.
        </p>
      )}

      {c360Complete && ellStatus === 'empty' && (
        <>
          <p className="text-xs text-surface-400 mb-3">
            {(c360.wallet_addresses || []).length} addresses extracted from C360 data.
            Add any additional wallet addresses below (one per line), or submit directly.
          </p>
          <textarea
            value={manualAddresses}
            onChange={(e) => setManualAddresses(e.target.value)}
            placeholder="Additional wallet addresses (one per line)..."
            rows={3}
            className="w-full px-3 py-2 rounded-lg bg-white dark:bg-surface-900 border border-surface-300 dark:border-surface-600 text-surface-900 dark:text-surface-100 placeholder-surface-400 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-gold-500/50 focus:border-gold-500 mb-3"
          />
          {error && <p className="text-sm text-red-500 dark:text-red-400 mb-3">{error}</p>}
          <div className="flex gap-2">
            <button
              onClick={handleSubmit}
              disabled={submitting}
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
        <h4 className="text-sm font-semibold text-surface-900 dark:text-surface-100">
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
              Mark N/A
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

// ── Assembled Output Modal ───────────────────────────────────────

function AssembledOutputModal({ markdown, onClose }) {
  const [copied, setCopied] = useState(false);

  function handleCopy() {
    navigator.clipboard.writeText(markdown);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

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

  // Polling callback — refresh full case data when status changes
  const handleStatusUpdate = useCallback(
    async (status) => {
      // If any section just completed, fetch full case data
      const sections = status.sections || {};
      const anyProcessing = Object.values(sections).some((s) => s.status === 'processing');
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
    // Also refresh immediately
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

  // Check if assembly is possible
  const canAssemble = caseData?.sections && (() => {
    const required = [
      'c360', 'elliptic', 'hexa_dump', 'previous_icrs', 'rfis',
      'kyc', 'l1_victim', 'l1_suspect', 'kodex',
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
      <div className="max-w-3xl mx-auto px-6 py-6 animate-fade-in">
        {/* Page header */}
        <div className="mb-6">
          <h2 className="text-2xl font-bold text-surface-900 dark:text-surface-100">
            Data Ingestion
          </h2>
          {caseData && (
            <div className="flex items-center gap-3 mt-1">
              <span className="text-sm font-mono text-surface-500">{caseData.case_id}</span>
              <span className="text-sm text-surface-400">UID: {caseData.subject_uid}</span>
              <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-surface-200 dark:bg-surface-700 text-surface-600 dark:text-surface-300">
                {caseData.status}
              </span>
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

            {/* Elliptic */}
            <EllipticSection
              caseData={caseData}
              onProcessingStarted={handleProcessingStarted}
            />

            {/* Future phase sections */}
            {FUTURE_SECTIONS.map((key) => (
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
          markdown={assembledMarkdown}
          onClose={() => setAssembledMarkdown(null)}
        />
      )}
    </AppLayout>
  );
}
