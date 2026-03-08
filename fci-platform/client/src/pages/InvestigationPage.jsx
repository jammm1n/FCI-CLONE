import { useEffect, useState, useCallback, useRef } from 'react';
import { useParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import * as api from '../services/api';
import useStreamingChat from '../hooks/useStreamingChat';
import AppLayout from '../components/AppLayout';
import CaseHeader from '../components/investigation/CaseHeader';
import CaseDataTabs, { TAB_GROUPS } from '../components/investigation/CaseDataTabs';
import CaseDataPanel from '../components/investigation/CaseDataPanel';
import ChatMessageList from '../components/investigation/ChatMessageList';
import ChatInput from '../components/investigation/ChatInput';
import StreamingIndicator from '../components/investigation/StreamingIndicator';
import Skeleton from '../components/shared/Skeleton';
import DownloadPdfButton from '../components/shared/DownloadPdfButton';
import TokenUsageDisplay from '../components/shared/TokenUsageDisplay';
import StepIndicator from '../components/shared/StepIndicator';
import QCPasteModal from '../components/shared/QCPasteModal';

export default function InvestigationPage() {
  const { caseId } = useParams();
  const { token } = useAuth();

  const [caseData, setCaseData] = useState(null);
  const [activeGroup, setActiveGroup] = useState(null);
  const [activeSubTab, setActiveSubTab] = useState(null);
  const [caseLoading, setCaseLoading] = useState(true);
  const [error, setError] = useState('');
  const [stepError, setStepError] = useState('');
  const [leftWidth, setLeftWidth] = useState(35);
  const [currentStep, setCurrentStep] = useState(null);
  const [stepPhase, setStepPhase] = useState(null);
  const [stepLoading, setStepLoading] = useState(false);
  const [showQCModal, setShowQCModal] = useState(false);
  const [stepSignalled, setStepSignalled] = useState(false);
  const [autoExecuting, setAutoExecuting] = useState(false);
  const dragging = useRef(false);

  const {
    messages,
    setMessages,
    conversationId,
    setConversationId,
    sending,
    aiLoading,
    tokenUsage,
    setTokenUsage,
    stepComplete,
    setStepComplete,
    loadHistory,
    sendMessage,
    triggerInitialAssessment,
  } = useStreamingChat(token);

  // Load case data and conversation
  useEffect(() => {
    let cancelled = false; // guard against StrictMode double-fire

    async function init() {
      try {
        const caseDetail = await api.getCase(token, caseId);
        if (cancelled) return;
        setCaseData(caseDetail);

        const ppd = caseDetail.preprocessed_data || {};
        // Find the first group that has data and set it as active
        for (const group of TAB_GROUPS) {
          const firstTab = group.tabs.find((t) => ppd[t.key]);
          if (firstTab) {
            setActiveGroup(group.id);
            setActiveSubTab(firstTab.key);
            break;
          }
        }

        // Case data is ready — render left panel immediately
        setCaseLoading(false);

        if (caseDetail.conversation_id) {
          // Existing conversation — load history
          setConversationId(caseDetail.conversation_id);
          const history = await loadHistory(caseDetail.conversation_id);
          if (history?.investigation_state) {
            setCurrentStep(history.investigation_state.current_step);
            setStepPhase(history.investigation_state.phase);
            if (history.investigation_state.step_complete_signalled) {
              setStepComplete(true);
              setStepSignalled(true);
            }
          }
        } else {
          // New conversation — two-step: create (instant) then stream assessment
          const result = await api.createConversation(token, caseId, 'case');
          if (cancelled) return;
          setConversationId(result.conversation_id);
          setCaseData((prev) => ({
            ...prev,
            conversation_id: result.conversation_id,
            status: 'in_progress',
          }));
          setCurrentStep(1);
          setStepPhase('setup');

          // Check if this conversation already has messages (e.g. race condition)
          const history = await api.getConversationHistory(token, result.conversation_id);
          if (cancelled) return;
          if (history.messages && history.messages.length > 0) {
            setMessages(history.messages);
          } else {
            await triggerInitialAssessment(result.conversation_id);
          }
        }
      } catch (err) {
        if (!cancelled) {
          setError(err.message);
          setCaseLoading(false);
        }
      }
    }
    init();

    return () => { cancelled = true; };
  }, [token, caseId]);

  // Warn on tab close / refresh while AI is responding
  useEffect(() => {
    if (!sending && !aiLoading && !autoExecuting) return;
    const handler = (e) => { e.preventDefault(); e.returnValue = ''; };
    window.addEventListener('beforeunload', handler);
    return () => window.removeEventListener('beforeunload', handler);
  }, [sending, aiLoading, autoExecuting]);

  // Track when the AI first signals step complete
  useEffect(() => {
    if (stepComplete) setStepSignalled(true);
  }, [stepComplete]);

  // After AI finishes responding, re-show approval buttons if step was signalled
  const wasSending = useRef(false);
  useEffect(() => {
    if (sending) {
      wasSending.current = true;
    } else if (wasSending.current && stepSignalled && !stepComplete) {
      wasSending.current = false;
      setStepComplete(true);
    }
  }, [sending, stepSignalled, stepComplete, setStepComplete]);

  const handleMouseDown = useCallback((e) => {
    e.preventDefault();
    dragging.current = true;
    document.body.style.cursor = 'col-resize';
    document.body.style.userSelect = 'none';

    function onMouseMove(e) {
      if (!dragging.current) return;
      const container = document.getElementById('investigation-panels');
      if (!container) return;
      const rect = container.getBoundingClientRect();
      const pct = ((e.clientX - rect.left) / rect.width) * 100;
      setLeftWidth(Math.min(60, Math.max(20, pct)));
    }

    function onMouseUp() {
      dragging.current = false;
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
      window.removeEventListener('mousemove', onMouseMove);
      window.removeEventListener('mouseup', onMouseUp);
    }

    window.addEventListener('mousemove', onMouseMove);
    window.addEventListener('mouseup', onMouseUp);
  }, []);

  const handleAdvanceStep = useCallback(async () => {
    if (!conversationId || stepLoading) return;
    setStepLoading(true);
    setStepError('');
    try {
      const result = await api.advanceStep(token, conversationId);
      setCurrentStep(result.step);
      setStepPhase(result.phase);
      const prevStep = result.step - 1;
      const PHASE_LABELS = { setup: 'Setup', analysis: 'Analysis', decision: 'Decision', post: 'Post-Decision', qc_check: 'QC Check' };
      const STEP_PHASES = { 1: 'setup', 2: 'analysis', 3: 'decision', 4: 'post', 5: 'qc_check' };
      const prevPhaseLabel = PHASE_LABELS[STEP_PHASES[prevStep]] || prevStep;
      const nextPhaseLabel = PHASE_LABELS[result.phase] || result.phase;
      setMessages((prev) => [
        ...prev,
        {
          message_id: `divider_${Date.now()}`,
          role: 'step_divider',
          content: `Step ${prevStep} (${prevPhaseLabel}) complete. Moving to Step ${result.step}: ${nextPhaseLabel}.`,
          timestamp: new Date().toISOString(),
        },
      ]);
      setStepComplete(false);
      setStepSignalled(false);
      setStepLoading(false);
      // Auto-trigger the AI to begin the new step
      const PHASE_LABELS_FULL = { setup: 'Setup', analysis: 'Analysis', decision: 'Decision', post: 'Post-Decision', qc_check: 'QC Check' };
      await sendMessage(`Begin Step ${result.step}: ${PHASE_LABELS_FULL[result.phase] || result.phase}. Your step document is loaded. Proceed in express mode.`);
    } catch (err) {
      setStepError(err.message);
      setStepLoading(false);
    }
  }, [conversationId, token, stepLoading, setMessages, setStepComplete, sendMessage]);

  const handleQCSubmit = useCallback(async (pastedText) => {
    if (!conversationId) return;
    setStepLoading(true);
    setStepError('');
    try {
      const result = await api.qcCheck(token, conversationId);
      setCurrentStep(result.step);
      setStepPhase(result.phase);
      setMessages((prev) => [
        ...prev,
        {
          message_id: `divider_${Date.now()}`,
          role: 'step_divider',
          content: 'Step 4 (Post-Decision) complete. Moving to Step 5: QC Check.',
          timestamp: new Date().toISOString(),
        },
      ]);
      setShowQCModal(false);
      setStepComplete(false);
      setStepSignalled(false);
      await sendMessage(pastedText);
    } catch (err) {
      setStepError(err.message);
    } finally {
      setStepLoading(false);
    }
  }, [conversationId, token, setMessages, sendMessage, setStepComplete]);

  // --- Auto-execute: run remaining steps without human approval ---
  const handleAutoExecute = useCallback(async (skipSummaries = false) => {
    if (!conversationId || autoExecuting) return;
    setAutoExecuting(true);
    setStepComplete(false);
    setStepSignalled(false);
    setStepError('');

    let currentStreamMsgId = null;
    let currentToolsUsed = [];

    try {
      const response = await api.autoExecute(token, conversationId, skipSummaries);
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop();

        for (const line of lines) {
          if (!line.startsWith('data:')) continue;
          const jsonStr = line.slice(5).trim();
          if (!jsonStr) continue;

          let event;
          try { event = JSON.parse(jsonStr); } catch { continue; }

          if (event.type === 'auto_step_start') {
            setCurrentStep(event.step);
            setStepPhase(event.phase);
            currentToolsUsed = [];
            currentStreamMsgId = `stream_auto_${Date.now()}_${event.step}`;

            const newMessages = [];
            if (event.user_content) {
              newMessages.push({
                message_id: `auto_user_${event.step}_${Date.now()}`,
                role: 'user',
                content: event.user_content,
                timestamp: new Date().toISOString(),
              });
            }
            newMessages.push({
              message_id: currentStreamMsgId,
              role: 'assistant',
              content: '',
              tools_used: [],
              timestamp: new Date().toISOString(),
              isStreaming: true,
            });
            setMessages((prev) => [...prev, ...newMessages]);

          } else if (event.type === 'content_delta') {
            if (currentStreamMsgId) {
              setMessages((prev) =>
                prev.map((msg) =>
                  msg.message_id === currentStreamMsgId
                    ? { ...msg, content: msg.content + event.text }
                    : msg
                )
              );
            }

          } else if (event.type === 'tool_use') {
            currentToolsUsed.push({
              tool: event.tool,
              document_id: event.document_id,
              document_title: event.document_title,
            });

          } else if (event.type === 'auto_step_done') {
            if (currentStreamMsgId) {
              const finalTools = [...currentToolsUsed];
              setMessages((prev) =>
                prev.map((msg) =>
                  msg.message_id === currentStreamMsgId
                    ? { ...msg, message_id: event.message_id || msg.message_id, tools_used: finalTools, isStreaming: false }
                    : msg
                )
              );
            }
            if (event.token_usage) setTokenUsage(event.token_usage);
            currentStreamMsgId = null;

          } else if (event.type === 'auto_step_divider') {
            setMessages((prev) => [
              ...prev,
              {
                message_id: `divider_auto_${Date.now()}`,
                role: 'step_divider',
                content: event.content,
                timestamp: new Date().toISOString(),
              },
            ]);

          } else if (event.type === 'auto_complete') {
            // All steps finished

          } else if (event.type === 'error') {
            if (currentStreamMsgId) {
              setMessages((prev) =>
                prev.map((msg) =>
                  msg.message_id === currentStreamMsgId
                    ? { ...msg, content: `**Error:** ${event.message}`, isStreaming: false }
                    : msg
                )
              );
            }
            setStepError(event.message);
          }
        }
      }
    } catch (err) {
      setStepError(err.message);
    } finally {
      setAutoExecuting(false);
    }
  }, [conversationId, token, autoExecuting, setMessages, setStepComplete, setTokenUsage]);

  if (caseLoading) {
    return (
      <AppLayout>
        <div id="investigation-panels" className="flex h-full">
          {/* Skeleton left panel */}
          <div style={{ width: `${leftWidth}%` }} className="border-r border-surface-200 dark:border-surface-700 flex flex-col p-6 gap-4 shrink-0 animate-fade-in">
            <Skeleton className="h-6 w-3/4" />
            <Skeleton className="h-4 w-1/2" />
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-32 w-full mt-4" />
          </div>
          {/* Skeleton right panel */}
          <div className="flex-1 flex flex-col p-5 gap-4 animate-fade-in" style={{ animationDelay: '100ms' }}>
            <Skeleton className="h-16 w-3/4" />
            <Skeleton className="h-12 w-1/2 ml-auto" />
            <Skeleton className="h-16 w-2/3" />
          </div>
        </div>
      </AppLayout>
    );
  }

  if (error) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center h-full">
          <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-6 max-w-md text-sm text-red-500 dark:text-red-400">
            {error}
          </div>
        </div>
      </AppLayout>
    );
  }

  const preprocessedData = caseData?.preprocessed_data || {};

  function handleGroupChange(groupId) {
    setActiveGroup(groupId);
    // Auto-select first available sub-tab in the new group
    const group = TAB_GROUPS.find((g) => g.id === groupId);
    if (group) {
      const firstAvailable = group.tabs.find((t) => preprocessedData[t.key]);
      setActiveSubTab(firstAvailable ? firstAvailable.key : null);
    }
  }

  return (
    <AppLayout
      caseInfo={caseData ? { case_id: caseData.case_id, case_type: caseData.case_type } : null}
    >
      <div id="investigation-panels" className="flex h-full">
        {/* Left panel — Case Data */}
        <div
          style={{ width: `${leftWidth}%` }}
          className="border-r border-surface-200 dark:border-surface-700 flex flex-col min-h-0 shrink-0 animate-slide-in-left"
        >
          <CaseHeader caseData={caseData} />
          <CaseDataTabs
            preprocessedData={preprocessedData}
            activeGroup={activeGroup}
            activeSubTab={activeSubTab}
            onGroupChange={handleGroupChange}
            onSubTabChange={setActiveSubTab}
          />
          <CaseDataPanel
            content={activeSubTab ? preprocessedData[activeSubTab] : null}
            activeTab={activeSubTab}
          />
        </div>

        {/* Gold drag handle */}
        <div
          onMouseDown={handleMouseDown}
          className="w-4 flex items-center justify-center cursor-col-resize group shrink-0 animate-fade-in"
          style={{ animationDelay: '300ms' }}
        >
          <div className="w-1 h-8 rounded-full bg-surface-300 dark:bg-surface-600 group-hover:bg-gold-500 group-hover:h-12 group-active:bg-gold-400 group-hover:shadow-[0_0_8px_rgba(240,185,11,0.3)] transition-all duration-200 flex flex-col items-center justify-center gap-0.5">
            <div className="w-0.5 h-0.5 rounded-full bg-surface-400 dark:bg-surface-500 group-hover:bg-gold-300 transition-colors" />
            <div className="w-0.5 h-0.5 rounded-full bg-surface-400 dark:bg-surface-500 group-hover:bg-gold-300 transition-colors" />
            <div className="w-0.5 h-0.5 rounded-full bg-surface-400 dark:bg-surface-500 group-hover:bg-gold-300 transition-colors" />
          </div>
        </div>

        {/* Right panel — Chat */}
        <div
          className="flex-1 flex flex-col min-h-0 animate-slide-in-right"
          style={{ animationDelay: '100ms' }}
        >
          <div className="flex items-center justify-between px-4 py-2 border-b border-surface-200 dark:border-surface-700 bg-surface-50 dark:bg-surface-800 shrink-0">
            <div className="flex items-center gap-4">
              <TokenUsageDisplay tokenUsage={tokenUsage} />
              <StepIndicator currentStep={currentStep} phase={stepPhase} />
            </div>
            <DownloadPdfButton
              conversationId={conversationId}
              disabled={sending || aiLoading || autoExecuting}
            />
          </div>
          <ChatMessageList messages={messages} aiLoading={aiLoading} conversationId={conversationId} />
          {(sending || autoExecuting) && <StreamingIndicator />}
          {stepError && (
            <div className="mx-4 mb-2 px-4 py-2 text-sm text-red-500 bg-red-500/10 border border-red-500/20 rounded-lg flex items-center justify-between">
              <span>{stepError}</span>
              <button onClick={() => setStepError('')} className="text-red-400 hover:text-red-300 ml-3 shrink-0">&times;</button>
            </div>
          )}
          <ChatInput
            onSend={sendMessage}
            disabled={sending || autoExecuting}
            currentStep={currentStep}
            stepComplete={stepComplete && !autoExecuting}
            onAdvanceStep={handleAdvanceStep}
            onQCCheck={() => setShowQCModal(true)}
            onContinueDiscussion={() => setStepComplete(false)}
            onManualStepComplete={() => setStepComplete(true)}
            stepLoading={stepLoading}
            onAutoExecute={handleAutoExecute}
            autoExecuting={autoExecuting}
          />
        </div>
      </div>
      {showQCModal && (
        <QCPasteModal
          onSubmit={handleQCSubmit}
          onCancel={() => setShowQCModal(false)}
          loading={stepLoading}
        />
      )}
    </AppLayout>
  );
}
