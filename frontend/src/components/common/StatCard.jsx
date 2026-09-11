import React from 'react';

export const StatCard = React.memo(({ title, value, subtitle, icon, badgeText, badgeColor = 'sky' }) => {
  const badgeStyles = {
    sky: 'bg-sky-500/10 text-sky-400 border-sky-500/30',
    emerald: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
    amber: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
    indigo: 'bg-indigo-500/10 text-indigo-400 border-indigo-500/30',
    rose: 'bg-rose-500/10 text-rose-400 border-rose-500/30',
  }[badgeColor] || 'bg-sky-500/10 text-sky-400 border-sky-500/30';

  return (
    <div className="glass-card p-5 rounded-2xl border border-slate-800/80 bg-slate-900/60 shadow-xl flex flex-col justify-between">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">{title}</p>
          <h3 className="text-2xl sm:text-3xl font-extrabold text-slate-100 mt-1 tracking-tight">{value}</h3>
        </div>
        {icon && (
          <div className="p-2.5 rounded-xl bg-slate-800/80 text-sky-400 border border-slate-700/50 shadow-inner">
            {icon}
          </div>
        )}
      </div>

      <div className="mt-4 flex items-center justify-between">
        {subtitle && <p className="text-xs text-slate-400">{subtitle}</p>}
        {badgeText && (
          <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${badgeStyles}`}>
            {badgeText}
          </span>
        )}
      </div>
    </div>
  );
});
