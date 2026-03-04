import { useState, useCallback, useEffect, useRef } from 'react';
import ImageUpload from '../shared/ImageUpload';

export default function ChatInput({ onSend, disabled }) {
  const [text, setText] = useState('');
  const [images, setImages] = useState([]);
  const textareaRef = useRef(null);

  const handleSend = useCallback(() => {
    if (!text.trim() && images.length === 0) return;
    onSend(text.trim(), images);
    setText('');
    setImages([]);
  }, [text, images, onSend]);

  // Enter to send, Shift+Enter for newline
  const handleKeyDown = useCallback(
    (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSend();
      }
    },
    [handleSend]
  );

  // Handle paste for images
  useEffect(() => {
    const textarea = textareaRef.current;
    if (!textarea) return;

    function handlePaste(e) {
      const items = e.clipboardData?.items;
      if (!items) return;

      const imageFiles = [];
      for (const item of items) {
        if (item.type.startsWith('image/')) {
          const file = item.getAsFile();
          if (file) imageFiles.push(file);
        }
      }

      if (imageFiles.length > 0) {
        e.preventDefault();
        // Convert pasted images to base64
        Promise.all(imageFiles.map(fileToBase64)).then((newImages) => {
          setImages((prev) => [...prev, ...newImages]);
        });
      }
    }

    textarea.addEventListener('paste', handlePaste);
    return () => textarea.removeEventListener('paste', handlePaste);
  }, []);

  return (
    <div className="border-t border-surface-700 bg-surface-800 px-4 py-3 shrink-0">
      <div className="flex items-end gap-2">
        <ImageUpload images={images} onImagesChange={setImages} />

        <textarea
          ref={textareaRef}
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={disabled}
          placeholder="Type a message... (Shift+Enter for new line)"
          rows={2}
          className="flex-1 px-3 py-2 bg-surface-900 border border-surface-600 rounded text-sm text-surface-100 placeholder-surface-500 focus:outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500 resize-none disabled:opacity-50"
        />

        <button
          onClick={handleSend}
          disabled={disabled || (!text.trim() && images.length === 0)}
          className="px-4 py-2 bg-primary-700 hover:bg-primary-600 disabled:bg-surface-700 disabled:text-surface-500 text-sm font-medium text-white rounded transition-colors shrink-0"
        >
          Send
        </button>
      </div>
    </div>
  );
}

function fileToBase64(file) {
  return new Promise((resolve) => {
    const reader = new FileReader();
    reader.onload = () => {
      const base64 = reader.result.split(',')[1];
      resolve({
        base64,
        media_type: file.type,
        preview: URL.createObjectURL(file),
      });
    };
    reader.readAsDataURL(file);
  });
}
