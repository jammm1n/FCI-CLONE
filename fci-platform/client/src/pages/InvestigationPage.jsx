import { useEffect, useState, useCallback } from 'react';
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
import LoadingSpinner from '../components/shared/LoadingSpinner';

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

  // Load case data and conversation
  useEffect(() => {
    async function init() {
      try {
        // Fetch case details
        const caseDetail = await api.getCase(token, caseId);
        setCaseData(caseDetail);

        // Set the first available tab
        const ppd = caseDetail.preprocessed_data || {};
        const firstKey = Object.keys(ppd).find((k) => ppd[k]);
        if (firstKey) setActiveTab(firstKey);

        if (caseDetail.conversation_id) {
          // Existing conversation — load history
          setConversationId(caseDetail.conversation_id);
          const history = await api.getConversationHistory(
            token,
            caseDetail.conversation_id
          );
          setMessages(history.messages || []);
        } else {
          // New conversation — create and get initial assessment
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
      if (!conversationId || !content.trim()) return;

      // Optimistically add user message
      const userMsg = {
        message_id: `temp_${Date.now()}`,
        role: 'user',
        content,
        images: images.length > 0 ? images.map((img) => ({ media_type: img.media_type })) : [],
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, userMsg]);
      setSending(true);

      // Add a placeholder assistant message that we'll stream into
      const streamMsgId = `stream_${Date.now()}`;
      setMessages((prev) => [
        ...prev,
        {
          message_id: streamMsgId,
          role: 'assistant',
          content: '',
          tools_used: [],
          timestamp: new Date().toISOString(),
        },
      ]);

      try {
        const response = await api.sendMessage(
          token,
          conversationId,
          content,
          images.map((img) => ({ base64: img.base64, media_type: img.media_type })),
          true // streaming
        );

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        let toolsUsed = [];

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });

          // Parse SSE lines from buffer
          const lines = buffer.split('\n');
          buffer = lines.pop(); // keep incomplete line in buffer

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
              // Update the placeholder message with the real message_id
              setMessages((prev) =>
                prev.map((msg) =>
                  msg.message_id === streamMsgId
                    ? { ...msg, message_id: event.message_id, tools_used: toolsUsed }
                    : msg
                )
              );
            } else if (event.type === 'error') {
              setMessages((prev) =>
                prev.map((msg) =>
                  msg.message_id === streamMsgId
                    ? { ...msg, content: `**Error:** ${event.message}` }
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
              ? { ...msg, content: `**Error:** ${err.message}` }
              : msg
          )
        );
      } finally {
        setSending(false);
      }
    },
    [token, conversationId]
  );

  if (loading) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center h-full">
          <div className="text-center">
            <LoadingSpinner size="lg" className="mx-auto mb-3" />
            <p className="text-sm text-surface-400">Loading investigation...</p>
          </div>
        </div>
      </AppLayout>
    );
  }

  if (error) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center h-full">
          <div className="bg-red-900/20 border border-red-800 rounded p-6 max-w-md text-sm text-red-400">
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
      <div className="flex h-full">
        {/* Left panel — Case Data (35%) */}
        <div className="w-[35%] border-r border-surface-700 flex flex-col min-h-0">
          <CaseHeader caseData={caseData} />
          <CaseDataTabs
            preprocessedData={preprocessedData}
            activeTab={activeTab}
            onTabChange={setActiveTab}
          />
          <CaseDataPanel
            content={activeTab ? preprocessedData[activeTab] : null}
          />
        </div>

        {/* Right panel — Chat (65%) */}
        <div className="flex-1 flex flex-col min-h-0">
          <ChatMessageList messages={messages} />
          {sending && <StreamingIndicator />}
          <ChatInput onSend={handleSendMessage} disabled={sending} />
        </div>
      </div>
    </AppLayout>
  );
}
