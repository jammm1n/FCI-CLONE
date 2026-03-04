import { useEffect, useRef } from 'react';
import ChatMessage from './ChatMessage';

export default function ChatMessageList({ messages }) {
  const bottomRef = useRef(null);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  if (messages.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <p className="text-sm text-surface-500">Starting investigation...</p>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto custom-scrollbar p-4 space-y-4">
      {messages.map((msg) => (
        <ChatMessage key={msg.message_id} message={msg} />
      ))}
      <div ref={bottomRef} />
    </div>
  );
}
