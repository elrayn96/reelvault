import React from 'react';
import { Database, Archive, RefreshCw, Sparkles, CheckCircle, ShieldAlert } from 'lucide-react';

interface ProcessIndicatorProps {
  status: string;
  progress: number;
  stage: string;
  onRetry: () => void;
}

export const ProcessIndicator: React.FC<ProcessIndicatorProps> = ({ status, progress, stage, onRetry }) => {
  const getStageIcon = () => {
    switch (stage) {
      case 'validating':
      case 'connecting':
        return <RefreshCw className="w-6 h-6 text-indigo-600 animate-spin" />;
      case 'downloading':
        return <Database className="w-6 h-6 text-indigo-600 animate-pulse" />;
      case 'compressing':
      case 'processing':
        return <Sparkles className="w-6 h-6 text-amber-500 animate-bounce" />;
      case 'packaging':
        return <Archive className="w-6 h-6 text-indigo-600" />;
      case 'completed':
      case 'finalized':
        return <CheckCircle className="w-6 h-6 text-emerald-600" />;
      case 'error':
        return <ShieldAlert className="w-6 h-6 text-rose-500 animate-shake" />;
      default:
        return <RefreshCw className="w-6 h-6 text-indigo-600 animate-spin" />;
    }
  };

  const isError = stage === 'error';

  return (
    <div className="w-full max-w-2xl mx-auto px-4 py-8">
      <div className="bg-white rounded-3xl p-6 md:p-8 shadow-[0px_4px_30px_rgba(15,23,42,0.06)] border border-gray-100 flex flex-col items-center">
        {/* Animated Icon Circle */}
        <div className={`w-16 h-16 rounded-full flex items-center justify-center mb-6 shadow-sm ${
          isError ? 'bg-rose-50' : stage === 'completed' || stage === 'finalized' ? 'bg-emerald-50' : 'bg-indigo-50'
        }`}>
          {getStageIcon()}
        </div>

        {/* Title & Description */}
        <div className="text-center space-y-2 mb-6">
          <h2 className="text-xl md:text-2xl font-display font-bold text-gray-900 leading-tight">
            {isError ? 'Secure Transit Interrupted' : 'Securing and Moving Media...'}
          </h2>
          <p className="text-sm font-medium text-gray-500 max-w-md mx-auto">
            {isError ? 'The pipeline encountered an issue.' : 'Establishing an encrypted route directly to local storage layers.'}
          </p>
        </div>

        {/* Progress Bar Track */}
        {!isError && (
          <div className="w-full max-w-md space-y-3">
            <div className="flex justify-between text-xs font-mono font-bold text-indigo-600">
              <span className="capitalize">{stage || 'analyzing'} stage</span>
              <span>{Math.round(progress)}%</span>
            </div>
            
            <div className="h-2.5 w-full bg-indigo-50 rounded-full overflow-hidden border border-indigo-100/30">
              <div 
                className="h-full bg-indigo-600 rounded-full transition-all duration-300 ease-out"
                style={{ width: `${progress}%` }}
              ></div>
            </div>
          </div>
        )}

        {/* Real-time Status Caption */}
        <div className={`mt-6 px-4 py-2.5 rounded-xl border text-sm font-semibold max-w-md text-center ${
          isError 
            ? 'bg-rose-50 border-rose-100 text-rose-700' 
            : 'bg-indigo-50/50 border-indigo-100/50 text-indigo-700'
        }`}>
          {status}
        </div>

        {/* Fallback layout simulator indicator */}
        {status.includes('API limit') && (
          <div className="mt-4 flex items-center gap-1.5 text-xs font-medium text-amber-700 bg-amber-50/70 border border-amber-100/50 rounded-lg px-3.5 py-1.5">
            <Sparkles className="w-3.5 h-3.5 shrink-0" />
            <span>Responsive placeholder loaded for review</span>
          </div>
        )}

        {isError && (
          <button
            onClick={onRetry}
            className="mt-6 px-6 py-2.5 bg-gray-900 hover:bg-gray-800 text-white font-display font-semibold rounded-xl text-sm transition-all active:scale-95"
          >
            Retry Download
          </button>
        )}

        {/* Bento skeleton loading panel */}
        {!isError && stage !== 'completed' && (
          <div className="mt-8 w-full border-t border-gray-100/80 pt-6">
            <div className="grid grid-cols-1 md:grid-cols-12 gap-4 items-stretch opacity-60">
              {/* Media Skeleton */}
              <div className="md:col-span-8 bg-gray-50/50 rounded-2xl p-2 border border-gray-100 flex flex-col gap-2">
                <div className="aspect-video w-full rounded-xl skeleton-shimmer"></div>
                <div className="px-1 py-2 space-y-2">
                  <div className="h-5 w-2/3 skeleton-shimmer rounded-md"></div>
                  <div className="h-4 w-1/2 skeleton-shimmer rounded-md opacity-60"></div>
                </div>
              </div>

              {/* Sidebar Skeletons */}
              <div className="md:col-span-4 flex flex-col gap-4">
                <div className="bg-gray-50/50 border border-gray-100 p-4 rounded-2xl flex-grow flex flex-col justify-between">
                  <div className="space-y-2">
                    <div className="h-3 w-1/2 skeleton-shimmer rounded"></div>
                    <div className="h-5 w-3/4 skeleton-shimmer rounded-md"></div>
                  </div>
                  <div className="h-1 w-full bg-gray-100 rounded-full overflow-hidden">
                    <div className="h-full w-1/3 bg-indigo-200 skeleton-shimmer"></div>
                  </div>
                </div>

                <div className="bg-gray-50/50 border border-gray-100 p-4 rounded-2xl flex-grow flex flex-col justify-between">
                  <div className="space-y-2">
                    <div className="h-3 w-1/2 skeleton-shimmer rounded"></div>
                    <div className="h-5 w-3/4 skeleton-shimmer rounded-md"></div>
                  </div>
                  <div className="h-1 w-full bg-gray-100 rounded-full overflow-hidden">
                    <div className="h-full w-1/2 bg-indigo-200 skeleton-shimmer"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
