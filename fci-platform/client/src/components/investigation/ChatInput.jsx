import { useState, useCallback, useEffect, useRef } from 'react';
import ImageUpload from '../shared/ImageUpload';

export default function ChatInput({ onSend, disabled, maxWidth = '', currentStep, stepComplete, onAdvanceStep, onQCCheck, onContinueDiscussion, onManualStepComplete, stepLoading }) {
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

  const hasContent = text.trim() || images.length > 0;

  return (
    <div
      ref={dropRef}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      className={`bg-surface-100 dark:bg-surface-850 pb-5 pt-2 shrink-0 ${
        dragOver ? 'ring-2 ring-inset ring-gold-400 bg-gold-500/5' : ''
      }`}
      style={{ paddingLeft: '5%', paddingRight: '5%' }}
    >
      <div className={maxWidth ? `${maxWidth} mx-auto` : ''}>
        {/* Step complete — approval mode: replaces the text input */}
        {stepComplete && currentStep >= 1 && currentStep <= 4 && (
          <div className="flex flex-col items-center gap-3 py-3 animate-fade-in">
            <p className="text-sm text-surface-500 dark:text-surface-400">
              This step is complete. Review the output above, then approve or continue the discussion.
            </p>
            <div className="flex items-center gap-3">
              {currentStep <= 3 ? (
                <button
                  onClick={onAdvanceStep}
                  disabled={stepLoading}
                  className="px-5 py-2.5 text-sm font-semibold rounded-lg bg-gradient-to-r from-gold-500 to-gold-400 text-surface-950 active:scale-[0.98] disabled:from-surface-300 disabled:to-surface-400 dark:disabled:from-surface-700 dark:disabled:to-surface-600 disabled:text-surface-500 flex items-center gap-2"
                >
                  {stepLoading ? (
                    <>
                      <div className="w-4 h-4 border-2 border-surface-950/30 border-t-surface-950 rounded-full animate-spin" />
                      Generating summary...
                    </>
                  ) : (
                    <>
                      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-4 h-4">
                        <path fillRule="evenodd" d="M16.704 4.153a.75.75 0 01.143 1.052l-8 10.5a.75.75 0 01-1.127.075l-4.5-4.5a.75.75 0 011.06-1.06l3.894 3.893 7.48-9.817a.75.75 0 011.05-.143z" clipRule="evenodd" />
                      </svg>
                      Approve and Continue
                    </>
                  )}
                </button>
              ) : (
                <button
                  onClick={onQCCheck}
                  disabled={stepLoading}
                  className="px-5 py-2.5 text-sm font-semibold rounded-lg bg-gradient-to-r from-gold-500 to-gold-400 text-surface-950 active:scale-[0.98] disabled:from-surface-300 disabled:to-surface-400 dark:disabled:from-surface-700 dark:disabled:to-surface-600 disabled:text-surface-500 flex items-center gap-2"
                >
                  {stepLoading ? (
                    <>
                      <div className="w-4 h-4 border-2 border-surface-950/30 border-t-surface-950 rounded-full animate-spin" />
                      Generating summary...
                    </>
                  ) : (
                    'QC Check'
                  )}
                </button>
              )}
              <button
                onClick={onContinueDiscussion}
                disabled={stepLoading}
                className="px-5 py-2.5 text-sm font-medium rounded-lg border border-surface-300 dark:border-surface-600 text-surface-600 dark:text-surface-400 hover:bg-surface-200 dark:hover:bg-surface-700 active:scale-[0.98] disabled:opacity-50"
              >
                Continue Discussion
              </button>
            </div>
          </div>
        )}

        {/* Manual override — only when step is NOT yet signalled complete */}
        {!stepComplete && currentStep >= 1 && currentStep <= 4 && !disabled && (
          <div className="flex justify-center mb-1">
            <button
              onClick={onManualStepComplete}
              className="text-xs text-surface-400 hover:text-gold-500 transition-colors"
            >
              Mark step complete
            </button>
          </div>
        )}

        {/* Normal chat input — hidden when in approval mode */}
        {(!stepComplete || !currentStep || currentStep > 4) && <>
        {dragOver && (
          <div className="text-center text-sm text-gold-500 mb-2 animate-fade-in">
            Drop image here
          </div>
        )}

        {/* Image thumbnails above the input */}
        {images.length > 0 && (
          <div className="flex flex-wrap gap-2 mb-2 px-1">
            <ImageUpload images={images} onImagesChange={setImages} showButton={false} />
          </div>
        )}

        {/* Unified input container */}
        <div className="relative rounded-2xl bg-surface-50 dark:bg-surface-800 border border-surface-200 dark:border-surface-700 focus-within:ring-2 focus-within:ring-gold-500/30 focus-within:border-gold-500">
          <textarea
            ref={textareaRef}
            value={text}
            onChange={(e) => setText(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={disabled}
            placeholder="Type a message... (Shift+Enter for new line)"
            rows={2}
            className="w-full px-4 pt-3 pb-12 text-base bg-transparent text-surface-900 dark:text-surface-100 placeholder-surface-400 focus:outline-none resize-none disabled:opacity-50"
          />

          {/* Bottom toolbar inside the input */}
          <div className="absolute bottom-2 left-2 right-2 flex items-center justify-between">
            <ImageUpload images={images} onImagesChange={setImages} showButton={true} showThumbnails={false} />

            <button
              onClick={handleSend}
              disabled={disabled || !hasContent}
              className="w-8 h-8 rounded-lg bg-gradient-to-r from-gold-500 to-gold-400 text-surface-950 flex items-center justify-center active:scale-[0.95] disabled:from-surface-300 disabled:to-surface-400 dark:disabled:from-surface-700 dark:disabled:to-surface-600 disabled:text-surface-500 shrink-0"
              title="Send message"
            >
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-4 h-4">
                <path d="M3.105 2.288a.75.75 0 0 0-.826.95l1.414 4.926A1.5 1.5 0 0 0 5.135 9.25h6.115a.75.75 0 0 1 0 1.5H5.135a1.5 1.5 0 0 0-1.442 1.086l-1.414 4.926a.75.75 0 0 0 .826.95 28.897 28.897 0 0 0 15.293-7.155.75.75 0 0 0 0-1.114A28.897 28.897 0 0 0 3.105 2.288Z" />
              </svg>
            </button>
          </div>
        </div>
        </>}
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
