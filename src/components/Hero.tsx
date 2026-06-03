import React, { useState } from 'react';
import { Clipboard, ShieldAlert, Film, History, Image as ImageIcon } from 'lucide-react';

interface HeroProps {
  onAnalyze: (url: string) => void;
  isLoading: boolean;
  error: string | null;
}

export const Hero: React.FC<HeroProps> = ({ onAnalyze, isLoading, error }) => {
  const [url, setUrl] = useState('');
  const [localError, setLocalError] = useState<string | null>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setLocalError(null);

    const trimmed = url.trim();
    if (!trimmed) {
      setLocalError('Please paste an Instagram link first.');
      return;
    }

    if (!trimmed.includes('instagram.com')) {
      setLocalError('Invalid link. Please enter a valid instagram.com URL.');
      return;
    }

    onAnalyze(trimmed);
  };

  const handlePaste = async () => {
    try {
      const text = await navigator.clipboard.readText();
      if (text) {
        setUrl(text);
        setLocalError(null);
      }
    } catch (err) {
      // Clipboard API blocks without document focus/permissions in some embeds
      console.warn('Could not read from clipboard:', err);
    }
  };

  return (
    <section className="w-full flex flex-col items-center py-12 md:py-20">
      <div className="w-full max-w-3xl text-center space-y-6 px-4">
        <h1 className="text-4xl md:text-5xl font-display font-extrabold text-gray-900 tracking-tight leading-tight">
          Download Instagram Media <span className="text-indigo-600">Instantly</span>
        </h1>
        <p className="text-lg md:text-xl text-gray-500 font-sans max-w-2xl mx-auto">
          Paste a link to save Reels, Posts, Stories, and Carousels in original high quality. Zero storage transit for your privacy.
        </p>

        {/* Big Search Input Field */}
        <form onSubmit={handleSubmit} className="mt-8 relative max-w-2xl mx-auto">
          <div className="flex flex-col sm:flex-row items-center gap-3 bg-white rounded-2xl p-2 w-full border border-gray-100 shadow-[0px_4px_24px_rgba(15,23,42,0.06)] focus-within:border-indigo-500 focus-within:ring-2 focus-within:ring-indigo-100 transition-all duration-200">
            <div className="flex items-center flex-grow w-full px-3 h-14">
              <Film className="w-5 h-5 text-gray-400 mr-3 shrink-0" />
              <input 
                type="text"
                placeholder="Paste Instagram link here... (e.g., https://www.instagram.com/reel/...)"
                value={url}
                onChange={(e) => {
                  setUrl(e.target.value);
                  setLocalError(null);
                }}
                disabled={isLoading}
                className="w-full bg-transparent border-none text-gray-800 placeholder:text-gray-400 text-base md:text-lg focus:outline-none focus:ring-0"
              />
              <button
                type="button"
                onClick={handlePaste}
                title="Paste from clipboard"
                className="p-2 hover:bg-gray-50 active:scale-95 text-gray-400 hover:text-indigo-600 rounded-lg transition-all shrink-0 ml-1"
              >
                <Clipboard className="w-5 h-5" />
              </button>
            </div>
            
            <button
              type="submit"
              disabled={isLoading}
              className={`w-full sm:w-auto px-8 h-12 rounded-xl text-white font-display font-bold text-base transition-all active:scale-95 shadow-md flex items-center justify-center ${
                isLoading 
                  ? 'bg-neutral-300 pointer-events-none' 
                  : 'bg-indigo-600 hover:bg-indigo-700 hover:shadow-indigo-200 active:bg-indigo-800'
              }`}
            >
              {isLoading ? 'Processing' : 'Download Now'}
            </button>
          </div>

          {/* Inline Errors feedback */}
          {(localError || error) && (
            <div className="absolute left-2 -bottom-9 flex items-center gap-1.5 text-xs font-semibold text-rose-600 bg-rose-50/80 backdrop-blur-sm px-3.5 py-1.5 rounded-lg border border-rose-100/30">
              <ShieldAlert className="w-4 h-4 shrink-0" />
              <span>{localError || error}</span>
            </div>
          )}
        </form>

        {/* Easy tags indicators */}
        <div className="pt-10 flex flex-wrap justify-center gap-6 text-sm font-semibold text-gray-500">
          <div className="flex items-center gap-2 px-4 py-2 bg-white rounded-xl border border-gray-100/50 shadow-sm hover:translate-y-[-1px] transition-all">
            <div className="w-6 h-6 rounded-lg bg-indigo-50 flex items-center justify-center text-indigo-600">
              <Film className="w-3.5 h-3.5" />
            </div>
            <span>Reels</span>
          </div>

          <div className="flex items-center gap-2 px-4 py-2 bg-white rounded-xl border border-gray-100/50 shadow-sm hover:translate-y-[-1px] transition-all">
            <div className="w-6 h-6 rounded-lg bg-indigo-50 flex items-center justify-center text-indigo-600">
              <History className="w-3.5 h-3.5" />
            </div>
            <span>Stories</span>
          </div>

          <div className="flex items-center gap-2 px-4 py-2 bg-white rounded-xl border border-gray-100/50 shadow-sm hover:translate-y-[-1px] transition-all">
            <div className="w-6 h-6 rounded-lg bg-indigo-50 flex items-center justify-center text-indigo-600">
              <ImageIcon className="w-3.5 h-3.5" />
            </div>
            <span>Photos & Carousels</span>
          </div>
        </div>
      </div>
    </section>
  );
};
