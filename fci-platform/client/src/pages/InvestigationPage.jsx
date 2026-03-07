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

export default function InvestigationPage() {
  const { caseId } = useParams();
  const { token } = useAuth();

  const [caseData, setCaseData] = useState(null);
  const [activeGroup, setActiveGroup] = useState(null);
  const [activeSubTab, setActiveSubTab] = useState(null);
  const [caseLoading, setCaseLoading] = useState(true);
  const [error, setError] = useState('');
  const [leftWidth, setLeftWidth] = useState(35);
  const dragging = useRef(false);

  const {
    messages,
    setMessages,
    conversationId,
    setConversationId,
    sending,
    aiLoading,
    tokenUsage,
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
          await loadHistory(caseDetail.conversation_id);
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
            <TokenUsageDisplay tokenUsage={tokenUsage} />
            <DownloadPdfButton
              conversationId={conversationId}
              disabled={sending || aiLoading}
            />
          </div>
          <ChatMessageList messages={messages} aiLoading={aiLoading} conversationId={conversationId} />
          {sending && <StreamingIndicator />}
          <ChatInput onSend={sendMessage} disabled={sending} />
        </div>
      </div>
    </AppLayout>
  );
}
