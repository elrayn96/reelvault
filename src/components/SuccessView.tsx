import React, { useState } from 'react';
import { DownloadResponse } from '../services/api';
import { CheckCircle, Download, FileText, Share2, Sparkles, Smile, Frown, Meh, Heart, Copy, Check } from 'lucide-react';

interface SuccessViewProps {
  downloadResult: DownloadResponse;
  compression: 'original' | 'compressed';
  onReset: () => void;
  thumbnail: string;
}

export const SuccessView: React.FC<SuccessViewProps> = ({ downloadResult, compression, onReset, thumbnail }) => {
  const [copiedShare, setCopiedShare] = useState(false);
  const [selectedRating, setSelectedRating] = useState<number | null>(null);

  const handleShareClick = () => {
    navigator.clipboard.writeText(window.location.href);
    setCopiedShare(true);
    setTimeout(() => setCopiedShare(false), 2000);
  };

  const ratings = [
    { value: 1, label: 'Poor', icon: <Frown className="w-6 h-6" /> },
    { value: 2, label: 'Okay', icon: <Meh className="w-6 h-6" /> },
    { value: 3, label: 'Good', icon: <Smile className="w-6 h-6" /> },
    { value: 4, label: 'Great', icon: <Heart className="w-6 h-6" /> },
  ];

  return (
    <div className="w-full max-w-2xl mx-auto px-4 py-8">
      {/* Success View Inner Frame Container */}
      <div className="bg-white rounded-[32px] p-6 md:p-8 border border-gray-100 shadow-[0px_4px_30px_rgba(15,23,42,0.06)] flex flex-col items-center text-center">
        
        {/* Success Visual Rings */}
        <div className="w-20 h-20 bg-emerald-50 text-emerald-600 rounded-full flex items-center justify-center mb-6 shadow-sm border border-emerald-100/50">
          <CheckCircle className="w-10 h-10 animate-bounce" />
        </div>

        <h1 className="text-3xl md:text-4xl font-display font-extrabold text-gray-900 tracking-tight leading-tight mb-2">
          Download Complete!
        </h1>
        <p className="text-sm font-medium text-gray-500 max-w-md mx-auto mb-8">
          Your requested Instagram media was securely processed and compiled inside your temporary folder.
        </p>

        {/* Media Package Details Card */}
        <div className="w-full bg-gray-50/50 rounded-2xl border border-gray-100 p-4 md:p-6 mb-8 flex flex-col sm:flex-row gap-5 items-center sm:items-start text-left">
          <div className="w-28 h-28 rounded-xl overflow-hidden shrink-0 border border-gray-100 bg-gray-100 shadow-sm">
            <img src={thumbnail} alt="Final Thumbnail" className="w-full h-full object-cover" />
          </div>

          <div className="flex-grow space-y-3.5 w-full">
            <div>
              <span className="text-xs font-semibold text-gray-400 uppercase tracking-widest block mb-0.5">Filename</span>
              <p className="font-mono text-sm font-bold text-gray-800 truncate max-w-xs sm:max-w-md">
                {downloadResult.filename}
              </p>
            </div>

            <div className="flex gap-8">
              <div>
                <span className="text-xs font-semibold text-gray-400 uppercase tracking-widest block mb-0.5">Format</span>
                <p className="text-sm font-semibold text-gray-800 capitalize">
                  {downloadResult.mimetype === 'application/zip' ? 'ZIP Archive' : 'Direct Media'}
                </p>
              </div>

              <div>
                <span className="text-xs font-semibold text-gray-400 uppercase tracking-widest block mb-0.5">Profile</span>
                <p className="text-sm font-semibold text-gray-800">
                  {compression === 'compressed' ? 'Data Saver (PIL)' : 'Original (HD)'}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Trigger Download Trigger Link */}
        <div className="w-full mb-8">
          <a 
            href={downloadResult.download_url}
            download={downloadResult.filename}
            className="w-full h-14 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl font-display font-bold text-base shadow-lg shadow-indigo-100 flex items-center justify-center gap-2.5 transition-all active:scale-95"
          >
            <Download className="w-5 h-5" />
            <span>Click to Trigger Download</span>
          </a>
        </div>

        {/* Dual Actions Controls */}
        <div className="w-full grid grid-cols-1 sm:grid-cols-2 gap-3.5 mb-8">
          <button
            onClick={onReset}
            className="w-full h-12 border border-gray-200 hover:border-gray-300 text-gray-700 font-display font-semibold rounded-xl text-sm hover:bg-gray-50/80 active:scale-95 transition-all"
          >
            Download Another
          </button>
          
          <button
            onClick={handleShareClick}
            className="w-full h-12 border border-gray-200 hover:border-indigo-100 text-gray-700 font-display font-semibold rounded-xl text-sm flex items-center justify-center gap-2 hover:bg-indigo-50/20 active:scale-95 transition-all"
          >
            {copiedShare ? (
              <>
                <Check className="w-4 h-4 text-emerald-600 animate-pulse" />
                <span className="text-emerald-700 font-semibold">Copied Vault Link!</span>
              </>
            ) : (
              <>
                <Share2 className="w-4 h-4 text-gray-400" />
                <span>Share ReelVault</span>
              </>
            )}
          </button>
        </div>

        {/* Emoji Rating Interface Section */}
        <div className="w-full border-t border-gray-100 pt-6 flex flex-col items-center">
          <p className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-4">How was your experience?</p>
          <div className="flex gap-4">
            {ratings.map((rate) => {
              const isActive = selectedRating === rate.value;
              return (
                <button
                  key={rate.value}
                  type="button"
                  onClick={() => setSelectedRating(rate.value)}
                  className={`flex flex-col items-center gap-1.5 p-2 rounded-xl transition-all ${
                    isActive 
                      ? 'text-indigo-600 scale-110 bg-indigo-50/30' 
                      : 'text-gray-400 hover:text-indigo-500 hover:scale-105 active:scale-95'
                  }`}
                >
                  {rate.icon}
                  <span className="text-[10px] font-semibold">{rate.label}</span>
                </button>
              );
            })}
          </div>
          {selectedRating !== null && (
            <div className="mt-3 text-xs font-semibold text-emerald-700 bg-emerald-50 px-3.5 py-1.5 rounded-full border border-emerald-100/50 flex items-center gap-1.5 animate-pulse">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Feedback stored securely! Thank you.</span>
            </div>
          )}
        </div>

      </div>
    </div>
  );
};
