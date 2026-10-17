import React from 'react';
import { PhoneCall, ShieldAlert, HeartHandshake } from 'lucide-react';

export const HelplineBanner: React.FC<{ compact?: boolean }> = ({ compact = false }) => {
  if (compact) {
    return (
      <div className="bg-slate-900 text-slate-200 text-xs py-2 px-4 flex flex-wrap items-center justify-between gap-2 border-b border-slate-800">
        <div className="flex items-center gap-1.5 text-teal-400 font-medium">
          <ShieldAlert className="w-3.5 h-3.5" />
          <span>24/7 Confidential Crisis Support:</span>
        </div>
        <div className="flex items-center gap-4 font-mono">
          <span>Tele-MANAS: <strong className="text-white font-bold">14416</strong></span>
          <span>Emergency: <strong className="text-white font-bold">112</strong></span>
          <span>Women: <strong className="text-white font-bold">1091</strong></span>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gradient-to-r from-teal-900 to-slate-900 text-white rounded-xl p-4 sm:p-5 shadow-sm border border-teal-800/50">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-teal-800/80 flex items-center justify-center text-teal-300 shrink-0">
            <HeartHandshake className="w-5 h-5" />
          </div>
          <div>
            <h4 className="text-sm font-bold text-white tracking-wide">
              Immediate Crisis & Trauma Support
            </h4>
            <p className="text-xs text-teal-100/80 mt-0.5">
              Free, confidential 24/7 national mental health and emergency lines
            </p>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-3 w-full sm:w-auto">
          <a
            href="tel:14416"
            className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-teal-800/60 hover:bg-teal-700 text-white text-xs font-semibold transition border border-teal-700/50"
          >
            <PhoneCall className="w-3.5 h-3.5 text-teal-300" />
            <span>Tele-MANAS: 14416</span>
          </a>
          <a
            href="tel:112"
            className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-rose-950/60 hover:bg-rose-900 text-rose-200 text-xs font-semibold transition border border-rose-800/50"
          >
            <ShieldAlert className="w-3.5 h-3.5 text-rose-400" />
            <span>Emergency: 112</span>
          </a>
          <a
            href="tel:1091"
            className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800/80 hover:bg-slate-700 text-slate-200 text-xs font-semibold transition border border-slate-700/50"
          >
            <PhoneCall className="w-3.5 h-3.5 text-slate-400" />
            <span>Women: 1091</span>
          </a>
        </div>
      </div>
    </div>
  );
};
