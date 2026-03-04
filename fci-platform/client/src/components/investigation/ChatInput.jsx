import { useState, useCallback, useEffect, useRef } from 'react';
import ImageUpload from '../shared/ImageUpload';

export default function ChatInput({ onSend, disabled }) {
  const [text, setText] = useState('');
  const [images, setImages] = useState([]);
  const [dragOver, setDragOver] = useState(false);
  const textareaRef = useRef(null);
  const dropRef = useRef(null);

  const handleSend = useCallback(() => {
    if (!text.trim() && images.length === 0) return;
    onSend(text.trim(), images);
    setText('');
    setImages([]);
  }, [text, images, onSend]);

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
        Promise.all(imageFiles.map(fileToBase64)).then((newImages) => {
          setImages((prev) => [...prev, ...newImages]);
        });
      }
    }

    textarea.addEventListener('paste', handlePaste);
    return () => textarea.removeEventListener('paste', handlePaste);
  }, []);

  // Handle drag and drop
  const handleDragOver = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragOver(false);
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragOver(false);

    const files = Array.from(e.dataTransfer.files).filter((f) =>
      f.type.startsWith('image/')
    );
    if (files.length > 0) {
      Promise.all(files.map(fileToBase64)).then((newImages) => {
        setImages((prev) => [...prev, ...newImages]);
      });
    }
  }, []);

  return (
    <div
      ref={dropRef}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      className={`border-t bg-surface-50 dark:bg-surface-800 px-5 py-4 shrink-0 ${
        dragOver
          ? 'border-2 border-dashed border-gold-400 bg-gold-500/5'
          : 'border-surface-200 dark:border-surface-700'
      }`}
    >
      {/* Drag overlay text */}
      {dragOver && (
        <div className="text-center text-sm text-gold-500 mb-2 animate-fade-in">
          Drop image here
        </div>
      )}

      <div className="flex items-end gap-2">
        <ImageUpload images={images} onImagesChange={setImages} />

        <textarea
          ref={textareaRef}
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={disabled}
          placeholder="Type a message... (Shift+Enter for new line)"
          rows={3}
          className="flex-1 px-4 py-3 text-base rounded-xl bg-surface-100 dark:bg-surface-900 border border-surface-200 dark:border-surface-600 text-surface-900 dark:text-surface-100 placeholder-surface-400 focus:outline-none focus:ring-2 focus:ring-gold-500/30 focus:border-gold-500 resize-none disabled:opacity-50"
        />

        <button
          onClick={handleSend}
          disabled={disabled || (!text.trim() && images.length === 0)}
          className="px-5 py-2.5 text-base font-medium rounded-xl bg-gradient-to-r from-gold-500 to-gold-400 text-surface-950 shadow-md shadow-gold-500/20 active:scale-[0.97] disabled:from-surface-300 disabled:to-surface-400 dark:disabled:from-surface-700 dark:disabled:to-surface-600 disabled:text-surface-500 disabled:shadow-none shrink-0"
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
