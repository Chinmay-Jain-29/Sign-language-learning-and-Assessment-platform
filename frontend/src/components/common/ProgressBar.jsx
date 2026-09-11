import React from 'react';

export const ProgressBar = ({ value = 0, max = 100, label, color = 'sky', className = '' }) => {
  const percentage = Math.min(100, Math.max(0, (value / max) * 100));

  const colors = {
    sky: 'bg-sky-500',
    emerald: 'bg-emerald-500',
    amber: 'bg-amber-500',
    indigo: 'bg-indigo-500',
    rose: 'bg-rose-500'
  };

  return (
    <div className={`space-y-1.5 w-full ${className}`}>
      {label && (
        <div className="flex justify-between text-xs font-medium">
          <span className="text-slate-300">{label}</span>
          <span className="font-bold text-white">{Math.round(percentage)}%</span>
        </div>
      )}
      <div
        role="progressbar"
        aria-valuenow={Math.round(percentage)}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label={label || "Progress"}
        className="w-full bg-slate-900 rounded-full h-2.5 overflow-hidden border border-slate-800"
      >
        <div
          className={`h-full rounded-full transition-all duration-500 ${colors[color] || 'bg-sky-500'}`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
};
