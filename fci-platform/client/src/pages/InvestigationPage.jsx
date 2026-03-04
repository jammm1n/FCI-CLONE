import { useEffect, useState, useCallback, useRef } from 'react';
import { useParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import * as api from '../services/api';
import AppLayout from '../components/AppLayout';
import CaseHeader from '../components/investigation/CaseHeader';
import CaseDataTabs from '../components/investigation/CaseDataTabs';
import CaseDataPanel from '../components/investigation/CaseDataPanel';
import ChatMessageList from '../components/investigation/ChatMessageList';
import ChatInput from '../components/investigation/ChatInput';
import StreamingIndicator from '../components/investigation/StreamingIndicator';
import Skeleton from '../components/shared/Skeleton';

export default function InvestigationPage() {
  const { caseId } = useParams();
  const { token } = useAuth();

  const [caseData, setCaseData] = useState(null);
  const [messages, setMessages] = useState([]);
  const [conversationId, setConversationId] = useState(null);
  const [activeTab, setActiveTab] = useState(null);
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState('');
  const [leftWidth, setLeftWidth] = useState(35);
  const dragging = useRef(false);

  // Load case data and conversation
  useEffect(() => {
    async function init() {
      try {
        const caseDetail = await api.getCase(token, caseId);
        setCaseData(caseDetail);

        const ppd = caseDetail.preprocessed_data || {};
        const firstKey = Object.keys(ppd).find((k) => ppd[k]);
        if (firstKey) setActiveTab(firstKey);

        if (caseDetail.conversation_id) {
          setConversationId(caseDetail.conversation_id);
          const history = await api.getConversationHistory(
            token,
            caseDetail.conversation_id
          );
          setMessages(history.messages || []);
        } else {
          const result = await api.createConversation(token, caseId);
          setConversationId(result.conversation_id);
          setCaseData((prev) => ({
            ...prev,
            conversation_id: result.conversation_id,
            status: 'in_progress',
          }));
          setMessages([
            {
              message_id: result.initial_response.message_id,
              role: 'assistant',
              content: result.initial_response.content,
              tools_used: result.initial_response.tools_used || [],
              timestamp: result.initial_response.timestamp,
            },
          ]);
        }
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    init();
  }, [token, caseId]);

  // Send a message with streaming
  const handleSendMessage = useCallback(
    async (content, images) => {
      if (!conversationId || (!content.trim() && images.length === 0)) return;

      const userMsg = {
        message_id: `temp_${Date.now()}`,
        role: 'user',
        content,
        images: images.length > 0 ? images.map((img) => ({ media_type: img.media_type, preview: img.preview })) : [],
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, userMsg]);
      setSending(true);

      const streamMsgId = `stream_${Date.now()}`;
      setMessages((prev) => [
        ...prev,
        {
          message_id: streamMsgId,
          role: 'assistant',
          content: '',
          tools_used: [],
          timestamp: new Date().toISOString(),
          isStreaming: true,
        },
      ]);

      try {
        const response = await api.sendMessage(
          token,
          conversationId,
          content,
          images.map((img) => ({ base64: img.base64, media_type: img.media_type })),
          true
        );

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        let toolsUsed = [];

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
            try {
              event = JSON.parse(jsonStr);
            } catch {
              continue;
            }

            if (event.type === 'content_delta') {
              setMessages((prev) =>
                prev.map((msg) =>
                  msg.message_id === streamMsgId
                    ? { ...msg, content: msg.content + event.text }
                    : msg
                )
              );
            } else if (event.type === 'tool_use') {
              toolsUsed.push({
                tool: event.tool,
                document_id: event.document_id,
                document_title: event.document_title,
              });
            } else if (event.type === 'stored') {
              setMessages((prev) =>
                prev.map((msg) =>
                  msg.message_id === streamMsgId
                    ? { ...msg, message_id: event.message_id, tools_used: toolsUsed, isStreaming: false }
                    : msg
                )
              );
            } else if (event.type === 'error') {
              setMessages((prev) =>
                prev.map((msg) =>
                  msg.message_id === streamMsgId
                    ? { ...msg, content: `**Error:** ${event.message}`, isStreaming: false }
                    : msg
                )
              );
            }
          }
        }
      } catch (err) {
        setMessages((prev) =>
          prev.map((msg) =>
            msg.message_id === streamMsgId
              ? { ...msg, content: `**Error:** ${err.message}`, isStreaming: false }
              : msg
          )
        );
      } finally {
        setSending(false);
      }
    },
    [token, conversationId]
  );

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

  if (loading) {
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
            activeTab={activeTab}
            onTabChange={setActiveTab}
          />
          <CaseDataPanel
            content={activeTab ? preprocessedData[activeTab] : null}
            activeTab={activeTab}
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
          <ChatMessageList messages={messages} />
          {sending && <StreamingIndicator />}
          <ChatInput onSend={handleSendMessage} disabled={sending} />
        </div>
      </div>
    </AppLayout>
  );
}
