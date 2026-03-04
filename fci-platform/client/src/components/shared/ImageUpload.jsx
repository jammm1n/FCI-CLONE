import { useRef, useCallback } from 'react';

export default function ImageUpload({ images, onImagesChange, showButton = true, showThumbnails = true }) {
  const fileInputRef = useRef(null);

  const addFiles = useCallback(
    async (files) => {
      const newImages = [];
      for (const file of files) {
        if (!file.type.startsWith('image/')) continue;
        const base64 = await fileToBase64(file);
        newImages.push({
          base64,
          media_type: file.type,
          preview: URL.createObjectURL(file),
        });
      }
      if (newImages.length > 0) {
        onImagesChange([...images, ...newImages]);
      }
    },
    [images, onImagesChange]
  );

  const handleFileSelect = useCallback(
    (e) => {
      if (e.target.files) {
        addFiles(Array.from(e.target.files));
        e.target.value = '';
      }
    },
    [addFiles]
  );

  const removeImage = useCallback(
    (index) => {
      const updated = images.filter((_, i) => i !== index);
      onImagesChange(updated);
    },
    [images, onImagesChange]
  );

  return (
    <div className="flex items-center gap-2">
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        multiple
        className="hidden"
        onChange={handleFileSelect}
      />

      {showButton && (
        <button
          type="button"
          onClick={() => fileInputRef.current?.click()}
          className="w-8 h-8 rounded-lg hover:bg-surface-100 dark:hover:bg-surface-700 flex items-center justify-center text-surface-400 hover:text-gold-500"
          title="Attach image"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M18.375 12.739l-7.693 7.693a4.5 4.5 0 01-6.364-6.364l10.94-10.94A3 3 0 1119.5 7.372L8.552 18.32m.009-.01l-.01.01m5.699-9.941l-7.81 7.81a1.5 1.5 0 002.112 2.13"
            />
          </svg>
        </button>
      )}

      {showThumbnails && images.map((img, i) => (
        <div key={i} className="relative group">
          <img
            src={img.preview}
            alt=""
            className="w-14 h-14 rounded-lg object-cover border border-surface-200 dark:border-surface-700"
          />
          <button
            type="button"
            onClick={() => removeImage(i)}
            className="absolute -top-1.5 -right-1.5 w-5 h-5 bg-surface-600 hover:bg-red-500 text-white rounded-full flex items-center justify-center text-xs opacity-0 group-hover:opacity-100 transition-opacity"
          >
            &times;
          </button>
        </div>
      ))}
    </div>
  );
}

function fileToBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      const result = reader.result;
      const base64 = result.split(',')[1];
      resolve(base64);
    };
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}
