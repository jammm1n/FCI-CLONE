import { useState, useCallback, useRef } from 'react';
import * as api from '../services/api';

/**
 * Reusable hook for SSE-streaming chat.
 *
 * Handles:
 *  - Loading conversation history
 *  - Sending messages with optimistic UI + SSE stream reading
 *  - Triggering initial assessment (case mode, no user message)
 */
export default function useStreamingChat(token) {
  const [messages, setMessages] = useState([]);
  const [conversationId, setConversationId] = useState(null);
  const [sending, setSending] = useState(false);
  const [aiLoading, setAiLoading] = useState(false);
  const [tokenUsage, setTokenUsage] = useState(null);
  const [stepComplete, setStepComplete] = useState(false);

  // Ref to avoid stale closure in streaming callbacks
  const conversationIdRef = useRef(null);
  const setConvId = useCallback((id) => {
    conversationIdRef.current = id;
    setConversationId(id);
  }, []);

  // -----------------------------------------------------------------------
  // SSE stream reader (shared by sendMessage and triggerInitialAssessment)
  // -----------------------------------------------------------------------
  const readStream = useCallback(async (response, streamMsgId) => {
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
          if (event.tool === 'signal_step_complete') {
            setStepComplete(true);
          }
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
  }, []);

  // -----------------------------------------------------------------------
  // Load existing conversation history
  // -----------------------------------------------------------------------
  const loadHistory = useCallback(async (convId) => {
    const history = await api.getConversationHistory(token, convId);
    setMessages(history.messages || []);
    setConvId(convId);
    return history;
  }, [token, setConvId]);

  // -----------------------------------------------------------------------
  // Trigger initial assessment (case mode — no user message)
  // -----------------------------------------------------------------------
  const triggerInitialAssessment = useCallback(async (convId) => {
    setAiLoading(true);
    const streamMsgId = `stream_${Date.now()}`;

    setMessages([{
      message_id: streamMsgId,
      role: 'assistant',
      content: '',
      tools_used: [],
      timestamp: new Date().toISOString(),
      isStreaming: true,
    }]);

    try {
      const response = await api.sendMessage(token, convId, '', [], true, true);
      // Once first bytes arrive, switch from spinner to streaming content
      setAiLoading(false);
      await readStream(response, streamMsgId);
    } catch (err) {
      setAiLoading(false);
      setMessages((prev) =>
        prev.map((msg) =>
          msg.message_id === streamMsgId
            ? { ...msg, content: `**Error:** ${err.message}`, isStreaming: false }
            : msg
        )
      );
    }
  }, [token, readStream]);

  // -----------------------------------------------------------------------
  // Send a user message with streaming response
  // -----------------------------------------------------------------------
  const sendMessage = useCallback(async (content, images = []) => {
    const convId = conversationIdRef.current;
    if (!convId || (!content.trim() && images.length === 0)) return;

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
        convId,
        content,
        images.map((img) => ({ base64: img.base64, media_type: img.media_type })),
        true
      );
      await readStream(response, streamMsgId);
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
  }, [token, readStream]);

  return {
    messages,
    setMessages,
    conversationId,
    setConversationId: setConvId,
    sending,
    aiLoading,
    tokenUsage,
    setTokenUsage,
    stepComplete,
    setStepComplete,
    loadHistory,
    sendMessage,
    triggerInitialAssessment,
  };
}
