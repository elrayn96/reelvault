import React, { useState } from 'react';
import { MediaData, MediaItem } from '../types';
import { Download, Archive, Link, FileVideo, FileImage, ShieldCheck, PlayCircle, Eye, EyeOff, Check } from 'lucide-react';

interface PreviewCardProps {
  data: MediaData;
  onDownload: (compression: 'original' | 'compressed') => void;
  isDownloading: boolean;
  onBack: () => void;
}

export const PreviewCard: React.FC<PreviewCardProps> = ({ data, onDownload, isDownloading, onBack }) => {
  const [selectedQuality, setSelectedQuality] = useState<'original' | 'compressed'>('original');
  const [activeCarouselIndex, setActiveCarouselIndex] = useState(0);
  const [showFullCaption, setShowFullCaption] = useState(false);

  // Carousel handlers
  const hasMultipleItems = data.type === 'carousel';
  const currentMediaItem: MediaItem = hasMultipleItems 
    ? data.items[activeCarouselIndex] 
    : data.items[0];

  const handleDownloadClick = () => {
    onDownload(selectedQuality);
  };

  return (
    <div className="w-full max-w-6xl mx-auto px-4 py-8">
      {/* Back to search */}
      <div className="mb-6">
        <button 
          onClick={onBack}
          type="button"
          className="flex items-center gap-2 text-sm font-semibold text-gray-500 hover:text-indigo-600 transition-colors"
        >
          &larr; Back to Search
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Span: Responsive Media Preview Window */}
        <div className="lg:col-span-7 space-y-4">
          <div className="bg-white rounded-[24px] overflow-hidden border border-gray-100 shadow-[0px_4px_24px_rgba(15,23,42,0.04)] aspect-square md:aspect-[4/5] relative group">
            
            {/* Visual Media Rendering */}
            {currentMediaItem?.is_video ? (
              <div className="w-full h-full relative bg-black flex items-center justify-center">
                <video 
                  src={currentMediaItem.url} 
                  poster={currentMediaItem.thumbnail}
                  controls
                  className="w-full h-full object-contain"
                />
                
                {/* Visual hover guides */}
                <div className="absolute top-4 left-4 bg-gray-950/60 backdrop-blur-md px-3 py-1.5 rounded-full text-white text-xs font-semibold flex items-center gap-1">
                  <FileVideo className="w-3.5 h-3.5" />
                  <span>Interactive Clip</span>
                </div>
              </div>
            ) : (
              <img 
                src={currentMediaItem?.url} 
                alt="Parsed media segment"
                referrerPolicy="no-referrer"
                className="w-full h-full object-cover"
              />
            )}

            {/* Type Indicator overlay */}
            <div className="absolute top-4 right-4 bg-gray-950/60 backdrop-blur-md text-white text-xs font-bold font-mono px-3.5 py-1.5 rounded-full flex items-center gap-1.5">
              <span>{data.original_type.toUpperCase()}</span>
            </div>

            {/* Carousel Item Counter Slider Indicators */}
            {hasMultipleItems && (
              <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex items-center gap-1.5 bg-gray-950/50 backdrop-blur-md px-4 py-1.5 rounded-full">
                {data.items.map((item, idx) => (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => setActiveCarouselIndex(idx)}
                    className={`w-2 h-2 rounded-full transition-all ${
                      activeCarouselIndex === idx ? 'bg-white scale-125' : 'bg-white/40'
                    }`}
                  />
                ))}
              </div>
            )}
          </div>

          {/* Carousel thumbnails navigator */}
          {hasMultipleItems && (
            <div className="flex gap-2.5 overflow-x-auto pb-2 custom-scroll">
              {data.items.map((item, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => setActiveCarouselIndex(idx)}
                  className={`w-16 h-16 rounded-xl overflow-hidden shrink-0 border-2 transition-all relative ${
                    activeCarouselIndex === idx ? 'border-indigo-600 scale-95' : 'border-transparent'
                  }`}
                >
                  <img src={item.thumbnail} alt="" className="w-full h-full object-cover" />
                  {item.is_video && (
                    <div className="absolute inset-0 flex items-center justify-center bg-black/25">
                      <PlayCircle className="w-5 h-5 text-white" />
                    </div>
                  )}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Right Span: Details and Option selectors */}
        <div className="lg:col-span-5 space-y-6">
          
          {/* Metadata information element */}
          <section className="bg-white rounded-3xl p-6 border border-gray-100 shadow-sm space-y-4">
            <div className="flex items-center justify-between border-b border-gray-50 pb-4">
              <h2 className="text-xl font-display font-bold text-gray-900">Media Details</h2>
              <span className="bg-indigo-50 text-indigo-700 text-xs font-mono font-bold px-3 py-1 rounded-full uppercase tracking-wider">
                {data.items.length} {data.items.length === 1 ? 'Item' : 'Items'}
              </span>
            </div>

            <div className="space-y-3.5 text-sm">
              <div>
                <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider block mb-1">Owner</span>
                <span className="font-semibold text-gray-800">@{data.owner}</span>
              </div>

              <div>
                <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider block mb-1">Caption</span>
                <p className={`text-gray-700 leading-relaxed font-sans ${showFullCaption ? '' : 'line-clamp-2'}`}>
                  {data.caption || 'No caption provided.'}
                </p>
                {data.caption && data.caption.length > 100 && (
                  <button
                    onClick={() => setShowFullCaption(!showFullCaption)}
                    className="text-xs font-semibold text-indigo-600 hover:text-indigo-700 mt-1 flex items-center gap-1"
                  >
                    {showFullCaption ? (
                      <>
                        <EyeOff className="w-3 h-3" />
                        <span>Show Less</span>
                      </>
                    ) : (
                      <>
                        <Eye className="w-3 h-3" />
                        <span>Read More</span>
                      </>
                    )}
                  </button>
                )}
              </div>
            </div>
          </section>

          {/* Secure quality selector option */}
          <section className="bg-white rounded-3xl p-6 border border-gray-100 shadow-sm space-y-4">
            <h3 className="text-xs font-bold text-gray-400 uppercase tracking-widest">Select Download Profile</h3>
            
            <div className="grid grid-cols-2 gap-3.5">
              {/* Profile Option 1: Original */}
              <label className="relative cursor-pointer group">
                <input 
                  type="radio" 
                  name="quality_selector" 
                  value="original"
                  checked={selectedQuality === 'original'}
                  onChange={() => setSelectedQuality('original')}
                  className="peer sr-only"
                />
                <div className="p-4 rounded-xl border border-gray-100 bg-gray-50/50 flex flex-col items-center justify-center text-center gap-1.5 transition-all peer-checked:border-indigo-600 peer-checked:bg-indigo-50/30 group-hover:border-indigo-500/50">
                  <FileImage className={`w-5 h-5 ${selectedQuality === 'original' ? 'text-indigo-600' : 'text-gray-400'}`} />
                  <span className="text-sm font-semibold text-gray-800">Original (HD)</span>
                  <span className="text-xs text-gray-400 font-mono">Max Quality</span>
                </div>
              </label>

              {/* Profile Option 2: Compressed (Pillow size reducers) */}
              <label className="relative cursor-pointer group">
                <input 
                  type="radio" 
                  name="quality_selector" 
                  value="compressed"
                  checked={selectedQuality === 'compressed'}
                  onChange={() => setSelectedQuality('compressed')}
                  className="peer sr-only"
                />
                <div className="p-4 rounded-xl border border-gray-100 bg-gray-50/50 flex flex-col items-center justify-center text-center gap-1.5 transition-all peer-checked:border-indigo-600 peer-checked:bg-indigo-50/30 group-hover:border-indigo-500/50">
                  <ShieldCheck className={`w-5 h-5 ${selectedQuality === 'compressed' ? 'text-indigo-600' : 'text-gray-400'}`} />
                  <span className="text-sm font-semibold text-gray-800">Data Saver</span>
                  <span className="text-xs text-gray-400 font-mono">Compressed</span>
                </div>
              </label>
            </div>
          </section>

          {/* Download Action Actions */}
          <div className="space-y-3">
            <button
              onClick={handleDownloadClick}
              disabled={isDownloading}
              className={`w-full h-14 rounded-2xl font-display font-bold text-base flex items-center justify-center gap-3 transition-all active:scale-[0.98] shadow-md ${
                isDownloading
                  ? 'bg-neutral-300 text-white pointer-events-none'
                  : 'bg-indigo-600 text-white hover:bg-indigo-700 hover:shadow-indigo-200'
              }`}
            >
              <Download className="w-5 h-5" />
              <span>{hasMultipleItems ? 'Download Carousel as ZIP' : 'Download Now'}</span>
            </button>

            {/* Sub informational privacy badge */}
            <div className="flex items-center justify-center gap-1.5 text-xs font-semibold text-gray-400 py-2">
              <ShieldCheck className="w-4 h-4 text-emerald-500" />
              <span>Vault Transit complete. Direct user download.</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
