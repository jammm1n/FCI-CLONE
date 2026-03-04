import MarkdownRenderer from '../shared/MarkdownRenderer';
import { formatTimestamp } from '../../utils/formatters';

export default function ChatMessage({ message }) {
  const isUser = message.role === 'user';
  const toolsUsed = message.tools_used || [];

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-[85%] rounded-lg px-4 py-3 ${
          isUser
            ? 'bg-primary-900/40 border border-primary-800/50'
            : 'bg-surface-800 border border-surface-700'
        }`}
      >
        {/* Role label */}
        <div className="flex items-center gap-2 mb-1.5">
          <span className={`text-xs font-medium ${isUser ? 'text-primary-400' : 'text-surface-400'}`}>
            {isUser ? 'You' : 'AI Assistant'}
          </span>
          <span className="text-xs text-surface-600">
            {formatTimestamp(message.timestamp)}
          </span>
        </div>

        {/* Image thumbnails */}
        {isUser && message.images && message.images.length > 0 && (
          <div className="flex flex-wrap gap-2 mb-2">
            {message.images.map((img, i) => (
              <div key={i} className="w-20 h-20 rounded border border-surface-600 overflow-hidden bg-surface-900">
                {img.preview ? (
                  <img src={img.preview} alt={`Attachment ${i + 1}`} className="w-full h-full object-cover" />
                ) : (
                  <div className="w-full h-full flex items-center justify-center text-xs text-surface-500">Image</div>
                )}
              </div>
            ))}
          </div>
        )}

        {/* Content */}
        {isUser ? (
          <p className="text-sm text-surface-200 whitespace-pre-wrap">{message.content}</p>
        ) : (
          <MarkdownRenderer content={message.content} />
        )}

        {/* Tools used footer */}
        {toolsUsed.length > 0 && (
          <div className="mt-2 pt-2 border-t border-surface-700">
            <span className="text-xs text-surface-500">Referenced: </span>
            {toolsUsed.map((t, i) => (
              <span key={i} className="text-xs text-primary-400">
                {t.document_title}
                {i < toolsUsed.length - 1 ? ', ' : ''}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
