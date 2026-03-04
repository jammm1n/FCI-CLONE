import { useRef, useCallback } from 'react';

/**
 * Handles image selection (file picker + paste) and base64 conversion.
 *
 * Props:
 *   images: array of { base64, media_type, preview } objects
 *   onImagesChange: callback to update images in parent state
 */
export default function ImageUpload({ images, onImagesChange }) {
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
      <button
        type="button"
        onClick={() => fileInputRef.current?.click()}
        className="p-1.5 text-surface-400 hover:text-surface-200 transition-colors"
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

      {/* Thumbnails */}
      {images.map((img, i) => (
        <div key={i} className="relative group">
          <img
            src={img.preview}
            alt=""
            className="h-8 w-8 rounded object-cover border border-surface-600"
          />
          <button
            type="button"
            onClick={() => removeImage(i)}
            className="absolute -top-1.5 -right-1.5 w-4 h-4 rounded-full bg-red-600 text-white text-xs leading-none flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
          >
            x
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
      // Strip the data:...;base64, prefix
      const result = reader.result;
      const base64 = result.split(',')[1];
      resolve(base64);
    };
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}
