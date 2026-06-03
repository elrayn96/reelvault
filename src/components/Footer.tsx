import React from 'react';
import { Lock, Zap, Shield, Sparkles } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="w-full bg-white border-t border-gray-100 mt-auto">
      
      {/* Bento Grid Features Guide - Desktop layout limits context scroll beautifully */}
      <section id="how-it-works" className="max-w-6xl mx-auto px-4 py-16 grid grid-cols-1 md:grid-cols-3 gap-8">
        
        {/* Bento Column 1: Speed */}
        <div className="bg-gray-50/50 rounded-2xl p-6 border border-gray-100 hover:translate-y-[-2px] transition-all duration-200">
          <div className="w-10 h-10 rounded-full bg-indigo-50/80 border border-indigo-100/50 text-indigo-600 flex items-center justify-center mb-4">
            <Zap className="w-5 h-5" />
          </div>
          <h4 className="text-base font-bold font-display text-gray-900 mb-1.5">Turbo Media Extraction</h4>
          <p className="text-sm text-gray-500 leading-relaxed font-sans">
            Our high-speed scrapers fetch direct CDN endpoints instantly, preventing long buffering pipelines.
          </p>
        </div>

        {/* Bento Column 2: Privacy */}
        <div className="bg-gray-50/50 rounded-2xl p-6 border border-gray-100 hover:translate-y-[-2px] transition-all duration-200">
          <div className="w-10 h-10 rounded-full bg-indigo-50/80 border border-indigo-100/50 text-indigo-600 flex items-center justify-center mb-4">
            <Lock className="w-5 h-5" />
          </div>
          <h4 className="text-base font-bold font-display text-gray-900 mb-1.5">Zero Data Logs Retention</h4>
          <p className="text-sm text-gray-500 leading-relaxed font-sans">
            Your downloads are streamed directly to your browser's disk caches. We never store or cache account records.
          </p>
        </div>

        {/* Bento Column 3: Compression */}
        <div className="bg-gray-50/50 rounded-2xl p-6 border border-gray-100 hover:translate-y-[-2px] transition-all duration-200">
          <div className="w-10 h-10 rounded-full bg-indigo-50/80 border border-indigo-100/50 text-indigo-600 flex items-center justify-center mb-4">
            <Shield className="w-5 h-5" />
          </div>
          <h4 className="text-base font-bold font-display text-gray-900 mb-1.5">Smart JPEG Compression</h4>
          <p className="text-sm text-gray-500 leading-relaxed font-sans">
            Our Pillow layout engine compresses and scales parsed images efficiently to optimize local drive space.
          </p>
        </div>

      </section>

      {/* Actual Legal Footer links */}
      <div className="border-t border-gray-100 py-8">
        <div className="max-w-6xl mx-auto px-4 flex flex-col md:flex-row justify-between items-center gap-4 text-center md:text-left">
          <div className="space-y-1">
            <p className="text-sm font-semibold text-gray-900 font-display">
              ReelVault
            </p>
            <p className="text-xs text-gray-500 leading-relaxed">
              &copy; {new Date().getFullYear()} ReelVault. Secure Media Transit System. Clean design corporate aesthetics.
            </p>
          </div>

          <div className="flex gap-6 text-xs font-semibold text-gray-500">
            <a href="#privacy" className="hover:text-indigo-600 transition-colors">Privacy Policy</a>
            <a href="#terms" className="hover:text-indigo-600 transition-colors">Terms of Service</a>
            <a href="#support" className="hover:text-indigo-600 transition-colors">Contact Support</a>
          </div>
        </div>
      </div>
    </footer>
  );
};
