import { useState, useCallback, type DragEvent } from "react";
import { ImagePlus, Send, X } from "lucide-react";

interface Props {
  onSubmit: (postText: string, imageUrl?: string) => void;
  isLoading: boolean;
}

export function PostInput({ onSubmit, isLoading }: Props) {
  const [text, setText] = useState("");
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);

  const handleImageFile = useCallback((file: File) => {
    if (!file.type.startsWith("image/")) return;
    const reader = new FileReader();
    reader.onload = (e) => {
      setImagePreview(e.target?.result as string);
    };
    reader.readAsDataURL(file);
  }, []);

  const handleDrop = useCallback(
    (e: DragEvent) => {
      e.preventDefault();
      setIsDragging(false);
      const file = e.dataTransfer.files[0];
      if (file) handleImageFile(file);
    },
    [handleImageFile]
  );

  const handleSubmit = () => {
    if (!text.trim()) return;
    onSubmit(text.trim(), imagePreview || undefined);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
      handleSubmit();
    }
  };

  return (
    <div className="space-y-4">
      <div
        className={`relative rounded-lg border-2 transition-colors ${
          isDragging
            ? "border-blue-400 bg-blue-50"
            : "border-gray-200 focus-within:border-blue-400"
        }`}
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
      >
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Paste a social media post here..."
          rows={5}
          className="w-full resize-none rounded-lg p-4 text-gray-900 placeholder-gray-400 focus:outline-none bg-transparent"
          disabled={isLoading}
        />
        {isDragging && (
          <div className="absolute inset-0 flex items-center justify-center rounded-lg bg-blue-50/80">
            <p className="text-blue-600 font-medium">Drop image here</p>
          </div>
        )}
      </div>

      {imagePreview && (
        <div className="relative inline-block">
          <img
            src={imagePreview}
            alt="Attached"
            className="h-24 rounded-lg border border-gray-200 object-cover"
          />
          <button
            onClick={() => setImagePreview(null)}
            className="absolute -top-2 -right-2 rounded-full bg-gray-800 p-0.5 text-white hover:bg-gray-700"
          >
            <X size={14} />
          </button>
        </div>
      )}

      <div className="flex items-center justify-between">
        <label className="flex cursor-pointer items-center gap-2 text-sm text-gray-500 hover:text-gray-700">
          <ImagePlus size={18} />
          <span>Attach image</span>
          <input
            type="file"
            accept="image/*"
            className="hidden"
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (file) handleImageFile(file);
            }}
          />
        </label>

        <button
          onClick={handleSubmit}
          disabled={!text.trim() || isLoading}
          className="flex items-center gap-2 rounded-lg bg-blue-600 px-5 py-2.5 text-sm font-medium text-white transition-colors hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading ? (
            <>
              <svg className="h-4 w-4 animate-spin" viewBox="0 0 24 24">
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                  fill="none"
                />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                />
              </svg>
              Analyzing...
            </>
          ) : (
            <>
              <Send size={16} />
              Explain Post
            </>
          )}
        </button>
      </div>
    </div>
  );
}
