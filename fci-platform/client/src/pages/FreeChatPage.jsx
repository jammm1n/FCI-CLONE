import { useEffect, useState, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import * as api from '../services/api';
import useStreamingChat from '../hooks/useStreamingChat';
import AppLayout from '../components/AppLayout';
import ChatSidebar from '../components/chat/ChatSidebar';
import ChatMessageList from '../components/investigation/ChatMessageList';
import ChatInput from '../components/investigation/ChatInput';
import StreamingIndicator from '../components/investigation/StreamingIndicator';
import DownloadPdfButton from '../components/shared/DownloadPdfButton';
import TokenUsageDisplay from '../components/shared/TokenUsageDisplay';

export default function FreeChatPage() {
  const { conversationId: paramConvId } = useParams();
  const navigate = useNavigate();
  const { token } = useAuth();

  const [sidebarConversations, setSidebarConversations] = useState([]);

  const {
    messages,
    setMessages,
    conversationId,
    setConversationId,
    sending,
    aiLoading,
    tokenUsage,
    setTokenUsage,
    loadHistory,
    sendMessage: hookSendMessage,
  } = useStreamingChat(token);

  // Load sidebar conversations
  const refreshSidebar = useCallback(async () => {
    try {
      const data = await api.getConversations(token, 'free_chat');
      setSidebarConversations(data.conversations || []);
    } catch {
      // Sidebar load failure is non-critical
    }
  }, [token]);

  // Initial load: sidebar + conversation if URL has an ID
  useEffect(() => {
    refreshSidebar();
  }, [refreshSidebar]);

  // When URL param changes, load that conversation
  useEffect(() => {
    if (paramConvId && paramConvId !== conversationId) {
      loadHistory(paramConvId);
    } else if (!paramConvId) {
      // /chat with no ID — fresh state
      setMessages([]);
      setConversationId(null);
    }
  }, [paramConvId]);

  // Handle first message in a new conversation
  const handleSend = useCallback(async (content, images = []) => {
    if (!content.trim() && images.length === 0) return;

    if (!conversationId) {
      // Create new free_chat conversation, then send first message
      try {
        const result = await api.createConversation(token, null, 'free_chat');
        const newConvId = result.conversation_id;
        setConversationId(newConvId);
        navigate(`/chat/${newConvId}`, { replace: true });

        // Now send the message through the hook
        // We need to wait for conversationId to be set, so send manually
        // Add user message optimistically
        const userMsg = {
          message_id: `temp_${Date.now()}`,
          role: 'user',
          content,
          images: images.length > 0 ? images.map((img) => ({ media_type: img.media_type, preview: img.preview })) : [],
          timestamp: new Date().toISOString(),
        };
        setMessages([userMsg]);

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

        const response = await api.sendMessage(
          token,
          newConvId,
          content,
          images.map((img) => ({ base64: img.base64, media_type: img.media_type })),
          true
        );

        // Read SSE stream
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
            } else if (event.type === 'done') {
              if (event.token_usage) setTokenUsage(event.token_usage);
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

        // Refresh sidebar to show new conversation with auto-generated title
        refreshSidebar();
      } catch (err) {
        setMessages((prev) => {
          const last = prev[prev.length - 1];
          if (last && last.isStreaming) {
            return prev.map((msg) =>
              msg.message_id === last.message_id
                ? { ...msg, content: `**Error:** ${err.message}`, isStreaming: false }
                : msg
            );
          }
          return prev;
        });
      }
    } else {
      // Existing conversation — use hook
      await hookSendMessage(content, images);
    }
  }, [token, conversationId, hookSendMessage, setConversationId, setMessages, setTokenUsage, navigate, refreshSidebar]);

  const handleNewChat = useCallback(() => {
    setMessages([]);
    setConversationId(null);
    navigate('/chat');
  }, [navigate, setMessages, setConversationId]);

  const handleDelete = useCallback(async (convId) => {
    try {
      await api.deleteConversation(token, convId);
      setSidebarConversations((prev) => prev.filter((c) => c.conversation_id !== convId));
      // If we deleted the active conversation, go to fresh chat
      if (convId === conversationId) {
        handleNewChat();
      }
    } catch {
      // Ignore delete errors
    }
  }, [token, conversationId, handleNewChat]);

  return (
    <AppLayout>
      <div className="flex h-full">
        <ChatSidebar
          conversations={sidebarConversations}
          activeId={conversationId}
          onNewChat={handleNewChat}
          onDelete={handleDelete}
        />
        <div className="flex-1 flex flex-col min-h-0">
          <div className="flex items-center justify-between px-4 py-2 border-b border-surface-200 dark:border-surface-700 bg-surface-50 dark:bg-surface-800 shrink-0">
            <TokenUsageDisplay tokenUsage={tokenUsage} />
            <DownloadPdfButton
              conversationId={conversationId}
              disabled={sending || aiLoading}
            />
          </div>
          <ChatMessageList
            messages={messages}
            aiLoading={aiLoading}
            emptyStateText="Ask anything about financial crime investigation..."
            maxWidth="w-[85%]"
            conversationId={conversationId}
          />
          {sending && <StreamingIndicator />}
          <ChatInput onSend={handleSend} disabled={sending} maxWidth="w-[85%]" />
        </div>
      </div>
    </AppLayout>
  );
}
