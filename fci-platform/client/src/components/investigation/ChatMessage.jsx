import { useState, useEffect } from 'react';
import { createPortal } from 'react-dom';
import MarkdownRenderer from '../shared/MarkdownRenderer';
import { formatTimestamp } from '../../utils/formatters';
import { imageUrl } from '../../services/api';

async function downloadImage(src) {
  try {
    const res = await fetch(src);
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = src.split('/').pop() || 'image';
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  } catch {
    // Fallback: open in new tab
    window.open(src, '_blank');
  }
}

function Lightbox({ src, onClose }) {
  // Close on Escape key
  useEffect(() => {
    const handler = (e) => { if (e.key === 'Escape') onClose(); };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [onClose]);

  return (
    <div
      onClick={onClose}
      style={{
        position: 'fixed',
        inset: 0,
        zIndex: 9999,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: 'rgba(0,0,0,0.85)',
        backdropFilter: 'blur(4px)',
        cursor: 'pointer',
      }}
    >
      <img
        src={src}
        alt="Full size"
        onClick={(e) => e.stopPropagation()}
        style={{
          maxWidth: '90vw',
          maxHeight: '90vh',
          objectFit: 'contain',
          borderRadius: '8px',
          boxShadow: '0 25px 50px rgba(0,0,0,0.5)',
          cursor: 'default',
        }}
      />
      {/* Top-right buttons */}
      <div style={{ position: 'absolute', top: 24, right: 24, display: 'flex', gap: 8 }}>
        <button
          onClick={(e) => { e.stopPropagation(); downloadImage(src); }}
          title="Download image"
          style={{
            width: 40, height: 40, borderRadius: '50%', border: 'none',
            backgroundColor: 'rgba(50,50,50,0.7)', color: '#fff',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            cursor: 'pointer',
          }}
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4" />
            <polyline points="7 10 12 15 17 10" />
            <line x1="12" y1="15" x2="12" y2="3" />
          </svg>
        </button>
        <button
          onClick={onClose}
          title="Close"
          style={{
            width: 40, height: 40, borderRadius: '50%', border: 'none',
            backgroundColor: 'rgba(50,50,50,0.7)', color: '#fff',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            cursor: 'pointer',
          }}
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        </button>
      </div>
    </div>
  );
}

export default function ChatMessage({ message, conversationId }) {
  const isUser = message.role === 'user';
  const toolsUsed = message.tools_used || [];
  const isStreaming = message.isStreaming;
  const thinkingContent = message.thinking_content || '';
  const [lightboxSrc, setLightboxSrc] = useState(null);
  const [showThinking, setShowThinking] = useState(false);

  return (
    <div className={`${isUser ? 'flex justify-end' : ''} animate-fade-in-up`}>
      <div
        className={`px-5 py-4 ${
          isUser
            ? 'max-w-[75%] bg-gold-500/10 border border-gold-500/20 rounded-2xl rounded-br-md'
            : 'bg-surface-50 dark:bg-surface-800 border border-surface-200 dark:border-surface-700 rounded-2xl rounded-bl-md shadow-soft-sm'
        }`}
      >
        {/* Role label + timestamp */}
        <div className="flex items-center gap-2 mb-2">
          <span className={`text-sm font-semibold ${
            isUser ? 'text-gold-600 dark:text-gold-500' : 'text-surface-600 dark:text-surface-400'
          }`}>
            {isUser ? 'You' : 'AI Assistant'}
          </span>
          <span className="text-xs text-surface-400">
            {formatTimestamp(message.timestamp)}
          </span>
        </div>

        {/* Image thumbnails (user messages) */}
        {isUser && message.images && message.images.length > 0 && (
          <div className="flex flex-wrap gap-2 mb-3">
            {message.images.map((img, i) => {
              const src = img.preview || (img.image_id && conversationId ? imageUrl(conversationId, img.image_id) : null);
              return (
                <div
                  key={img.image_id || i}
                  className="w-24 h-24 rounded-xl border-2 border-gold-200 dark:border-gold-800 overflow-hidden bg-surface-100 dark:bg-surface-900 hover:scale-105 transition-transform cursor-pointer"
                  onClick={() => src && setLightboxSrc(src)}
                >
                  {src ? (
                    <img src={src} alt={`Attachment ${i + 1}`} className="w-full h-full object-cover" />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center text-xs text-surface-500">Image</div>
                  )}
                </div>
              );
            })}
          </div>
        )}

        {/* AI Thinking (collapsible) */}
        {!isUser && thinkingContent && (
          <div className="mb-3">
            <button
              onClick={() => setShowThinking((prev) => !prev)}
              className="flex items-center gap-1.5 text-xs text-surface-400 hover:text-purple-400 transition-colors"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 16 16"
                fill="currentColor"
                className={`w-3 h-3 transition-transform ${showThinking ? 'rotate-90' : ''}`}
              >
                <path d="M6.22 4.22a.75.75 0 0 1 1.06 0l3.25 3.25a.75.75 0 0 1 0 1.06l-3.25 3.25a.75.75 0 0 1-1.06-1.06L8.94 8 6.22 5.28a.75.75 0 0 1 0-1.06Z" />
              </svg>
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" className="w-3 h-3 opacity-60">
                <path d="M8 1a5.5 5.5 0 0 0-4.764 8.246l-.703 2.108a.75.75 0 0 0 .949.949l2.108-.703A5.5 5.5 0 1 0 8 1ZM4 6.5a.5.5 0 0 1 .5-.5h7a.5.5 0 0 1 0 1h-7a.5.5 0 0 1-.5-.5Zm.5 2.5a.5.5 0 0 0 0 1h4a.5.5 0 0 0 0-1h-4Z" />
              </svg>
              {showThinking ? 'Hide' : 'Show'} AI thinking
              <span className="text-surface-500">({Math.round(thinkingContent.length / 4).toLocaleString()} tokens est.)</span>
            </button>
            {showThinking && (
              <div className="mt-2 px-3 py-2 rounded-lg bg-purple-500/5 border border-purple-500/10 max-h-96 overflow-y-auto">
                <pre className="text-xs text-surface-400 dark:text-surface-500 whitespace-pre-wrap font-mono leading-relaxed">{thinkingContent}</pre>
              </div>
            )}
          </div>
        )}

        {/* Content */}
        {isUser ? (
          <p className="text-base text-surface-800 dark:text-surface-200 leading-relaxed whitespace-pre-wrap">{message.content}</p>
        ) : (
          <div className="text-base leading-relaxed">
            <MarkdownRenderer content={message.content} />
            {isStreaming && (
              <span className="animate-blink text-gold-500 ml-0.5">&#9612;</span>
            )}
          </div>
        )}

        {/* Tools used footer */}
        {toolsUsed.length > 0 && (() => {
          const injected = toolsUsed.filter((t) => t.tool === 'system_injected');
          const fetched = toolsUsed.filter((t) => t.tool !== 'system_injected');
          return (
            <div className="mt-3 pt-3 border-t border-surface-100 dark:border-surface-700 space-y-1">
              {injected.length > 0 && (
                <div>
                  <span className="text-xs text-surface-400">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" className="w-3 h-3 inline mr-1 opacity-50">
                      <path d="M2 4a2 2 0 012-2h8a2 2 0 012 2v8a2 2 0 01-2 2H4a2 2 0 01-2-2V4zm2-.5a.5.5 0 00-.5.5v8a.5.5 0 00.5.5h8a.5.5 0 00.5-.5V4a.5.5 0 00-.5-.5H4z" />
                    </svg>
                    Context:{' '}
                  </span>
                  {injected.map((t, i) => (
                    <span key={i} className="text-xs text-surface-500 dark:text-surface-400">
                      {t.document_title}{i < injected.length - 1 ? ', ' : ''}
                    </span>
                  ))}
                </div>
              )}
              {fetched.length > 0 && (
                <div>
                  <span className="text-sm text-surface-500">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" className="w-3.5 h-3.5 inline mr-1 opacity-60">
                      <path d="M2 4a2 2 0 012-2h8a2 2 0 012 2v8a2 2 0 01-2 2H4a2 2 0 01-2-2V4zm2-.5a.5.5 0 00-.5.5v8a.5.5 0 00.5.5h8a.5.5 0 00.5-.5V4a.5.5 0 00-.5-.5H4z" />
                    </svg>
                    Referenced:{' '}
                  </span>
                  {fetched.map((t, i) => (
                    <span key={i} className="text-sm text-gold-600 dark:text-gold-400 font-medium">
                      {t.document_title}{i < fetched.length - 1 ? ', ' : ''}
                    </span>
                  ))}
                </div>
              )}
            </div>
          );
        })()}
      </div>

      {/* Lightbox — portalled to body, all inline styles */}
      {lightboxSrc && createPortal(
        <Lightbox src={lightboxSrc} onClose={() => setLightboxSrc(null)} />,
        document.body
      )}
    </div>
  );
}
