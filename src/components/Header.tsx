import React from 'react';
import { ShieldCheck, CircleDot } from 'lucide-react';

interface HeaderProps {
  wsConnected: boolean;
  onReset: () => void;
}

export const Header: React.FC<HeaderProps> = ({ wsConnected, onReset }) => {
  return (
    <header className="bg-white border-b border-gray-100 sticky top-0 z-50">
      <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
        <div 
          className="flex items-center gap-2 cursor-pointer group"
          onClick={onReset}
        >
          <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center text-white font-display font-black text-lg transition-transform group-hover:scale-105 active:scale-95 duration-150">
            RV
          </div>
          <span className="font-display font-black text-xl text-gray-900 tracking-tight">
            Reel<span className="text-indigo-600">Vault</span>
          </span>
        </div>

        {/* Navigation Info */}
        <nav className="hidden md:flex items-center gap-6">
          <a href="#how-it-works" className="text-sm font-medium text-gray-500 hover:text-indigo-600 transition-colors">How it works</a>
          <a href="#security" className="text-sm font-medium text-gray-500 hover:text-indigo-600 transition-colors">Security</a>
          <a href="#about" className="text-sm font-medium text-gray-500 hover:text-indigo-600 transition-colors">About</a>
        </nav>

        {/* Real-time Status Badge */}
        <div className="flex items-center gap-3">
          <div className={`flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold ${
            wsConnected 
              ? 'bg-green-50 text-green-700 border border-green-100/50' 
              : 'bg-amber-50 text-amber-700 border border-amber-100/50'
          }`}>
            <CircleDot className={`w-3.5 h-3.5 ${wsConnected ? 'text-green-500 animate-pulse' : 'text-amber-500'}`} />
            <span>{wsConnected ? 'Transit Active' : 'Connecting'}</span>
          </div>

          <div className="hidden sm:flex items-center gap-1 text-xs font-semibold bg-indigo-50 text-indigo-700 px-3 py-1 rounded-full border border-indigo-100/50">
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>SSL Encrypted</span>
          </div>
        </div>
      </div>
    </header>
  );
};
