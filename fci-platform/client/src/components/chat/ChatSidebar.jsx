import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

export default function ChatSidebar({
  conversations = [],
  activeId = null,
  onNewChat,
  onDelete,
}) {
  const navigate = useNavigate();
  const [pendingDeleteId, setPendingDeleteId] = useState(null);

  // Clear pending delete after 3 seconds
  useEffect(() => {
    if (!pendingDeleteId) return;
    const timer = setTimeout(() => setPendingDeleteId(null), 3000);
    return () => clearTimeout(timer);
  }, [pendingDeleteId]);

  return (
    <div className="w-72 shrink-0 flex flex-col border-r border-surface-200 dark:border-surface-700 bg-surface-50 dark:bg-surface-900 h-full">
      {/* New chat button */}
      <div className="p-3">
        <button
          onClick={onNewChat}
          className="w-full flex items-center gap-2 px-3 py-2.5 rounded-lg text-sm font-medium border border-gold-500/30 text-gold-600 dark:text-gold-400 hover:bg-gold-500/10 transition-colors"
        >
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-4 h-4">
            <path d="M10.75 4.75a.75.75 0 00-1.5 0v4.5h-4.5a.75.75 0 000 1.5h4.5v4.5a.75.75 0 001.5 0v-4.5h4.5a.75.75 0 000-1.5h-4.5v-4.5z" />
          </svg>
          New Chat
        </button>
      </div>

      {/* Conversation list */}
      <div className="flex-1 overflow-y-auto custom-scrollbar px-2 pb-3">
        {conversations.length === 0 && (
          <p className="text-xs text-surface-400 dark:text-surface-500 text-center mt-8">
            No conversations yet
          </p>
        )}
        {conversations.map((conv) => (
          <div
            key={conv.conversation_id}
            className={`group relative flex items-center rounded-lg px-3 py-2.5 mb-0.5 text-sm cursor-pointer transition-colors ${
              conv.conversation_id === activeId
                ? 'bg-surface-100 dark:bg-surface-800 text-gold-600 dark:text-gold-400'
                : 'text-surface-600 dark:text-surface-400 hover:bg-surface-100 dark:hover:bg-surface-800'
            }`}
            onClick={() => navigate(`/chat/${conv.conversation_id}`)}
          >
            <span className="truncate flex-1">
              {conv.title || 'New conversation'}
            </span>
            {onDelete && pendingDeleteId === conv.conversation_id ? (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  setPendingDeleteId(null);
                  onDelete(conv.conversation_id);
                }}
                className="shrink-0 ml-1 px-2 py-0.5 rounded text-xs font-medium bg-red-500/15 text-red-500 hover:bg-red-500/25 transition-colors"
              >
                Delete?
              </button>
            ) : onDelete && (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  setPendingDeleteId(conv.conversation_id);
                }}
                className="opacity-0 group-hover:opacity-100 shrink-0 ml-1 p-1 rounded hover:bg-surface-200 dark:hover:bg-surface-700 text-surface-400 hover:text-red-500 transition-all"
                title="Delete conversation"
              >
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" className="w-3.5 h-3.5">
                  <path fillRule="evenodd" d="M5 3.25V4H2.75a.75.75 0 0 0 0 1.5h.3l.815 8.15A1.5 1.5 0 0 0 5.357 15h5.285a1.5 1.5 0 0 0 1.493-1.35l.815-8.15h.3a.75.75 0 0 0 0-1.5H11v-.75A2.25 2.25 0 0 0 8.75 1h-1.5A2.25 2.25 0 0 0 5 3.25Zm2.25-.75a.75.75 0 0 0-.75.75V4h3v-.75a.75.75 0 0 0-.75-.75h-1.5ZM6.05 6a.75.75 0 0 1 .787.713l.275 5.5a.75.75 0 0 1-1.498.075l-.275-5.5A.75.75 0 0 1 6.05 6Zm3.9 0a.75.75 0 0 1 .712.787l-.275 5.5a.75.75 0 0 1-1.498-.075l.275-5.5a.75.75 0 0 1 .786-.711Z" clipRule="evenodd" />
                </svg>
              </button>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
