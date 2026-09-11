import React from 'react';
import { BarChart3, TrendingUp } from 'lucide-react';

export const TrendChart = React.memo(({ data = [], height = 180, title = 'Session Performance Trend' }) => {
  if (!data || data.length === 0) {
    return (
      <div className="glass-card p-5 rounded-2xl border border-slate-800/80 bg-slate-900/60 shadow-xl flex flex-col justify-between" style={{ minHeight: height }}>
        <h4 className="text-sm font-semibold uppercase tracking-wider text-slate-400">{title}</h4>
        <div className="flex flex-col items-center justify-center py-10 text-center text-slate-500">
          <BarChart3 className="w-8 h-8 mb-2 opacity-40 text-slate-400" />
          <p className="text-xs font-medium text-slate-400">No session performance data yet.</p>
          <p className="text-[11px] text-slate-500 mt-0.5">Complete your first webcam practice session to view your progress trend.</p>
        </div>
      </div>
    );
  }

  const scores = data.map((d) => d.score ?? d.accuracy ?? 0);
  const minScore = Math.max(0, Math.min(...scores) - 10);
  const maxScore = Math.min(100, Math.max(...scores) + 10);
  const range = maxScore - minScore || 1;

  const svgWidth = 500;
  const svgHeight = height;
  const paddingLeft = 45;
  const paddingRight = 25;
  const paddingTop = 25;
  const paddingBottom = 35;

  const chartWidth = svgWidth - paddingLeft - paddingRight;
  const chartHeight = svgHeight - paddingTop - paddingBottom;

  const isSingle = data.length === 1;

  const points = data.map((d, index) => {
    const scoreVal = d.score ?? d.accuracy ?? 0;
    const x = isSingle
      ? paddingLeft + chartWidth / 2
      : paddingLeft + (index / (data.length - 1)) * chartWidth;
    const y = paddingTop + chartHeight - ((scoreVal - minScore) / range) * chartHeight;
    return {
      x,
      y,
      score: scoreVal,
      label: d.label || `S${index + 1}`,
      attempts: d.attempts,
      correct: d.correct_attempts ?? d.correct
    };
  });

  const pathD = isSingle
    ? `M ${points[0].x - 20} ${points[0].y} L ${points[0].x + 20} ${points[0].y}`
    : points.reduce((acc, p, i) => (i === 0 ? `M ${p.x} ${p.y}` : `${acc} L ${p.x} ${p.y}`), '');

  const areaD = isSingle
    ? ''
    : `${pathD} L ${points[points.length - 1].x} ${svgHeight - paddingBottom} L ${points[0].x} ${svgHeight - paddingBottom} Z`;

  return (
    <div className="glass-card p-5 rounded-2xl border border-slate-800/80 bg-slate-900/60 shadow-xl">
      <div className="flex justify-between items-center mb-4">
        <div className="flex items-center gap-2">
          <h4 className="text-sm font-semibold uppercase tracking-wider text-slate-400">{title}</h4>
          <TrendingUp className="w-4 h-4 text-sky-400" />
        </div>
        <span className="text-xs bg-sky-500/10 text-sky-400 border border-sky-500/30 px-2.5 py-1 rounded-full font-medium">
          {data.length === 1 ? '1 Session Recorded' : `Last ${data.length} Sessions`}
        </span>
      </div>

      <div className="w-full overflow-x-auto">
        <svg viewBox={`0 0 ${svgWidth} ${svgHeight}`} className="w-full h-auto min-w-[320px] overflow-visible">
          <defs>
            <linearGradient id="chartGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#0ea5e9" stopOpacity="0.35" />
              <stop offset="100%" stopColor="#0ea5e9" stopOpacity="0.0" />
            </linearGradient>
          </defs>

          {/* Y-Axis Grid Lines */}
          {[0, 25, 50, 75, 100].map((val) => {
            if (val < minScore || val > maxScore) return null;
            const y = paddingTop + chartHeight - ((val - minScore) / range) * chartHeight;
            return (
              <g key={val}>
                <line x1={paddingLeft} y1={y} x2={svgWidth - paddingRight} y2={y} stroke="#1e293b" strokeDasharray="3 3" />
                <text x={paddingLeft - 8} y={y + 3.5} fill="#64748b" fontSize="10" textAnchor="end">
                  {val}%
                </text>
              </g>
            );
          })}

          {/* Area Fill */}
          {areaD && <path d={areaD} fill="url(#chartGradient)" />}

          {/* Line Path */}
          <path d={pathD} fill="none" stroke="#0ea5e9" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />

          {/* Data Points */}
          {points.map((p, i) => (
            <g key={i} className="group cursor-pointer">
              <circle
                cx={p.x}
                cy={p.y}
                r="5.5"
                fill="#0f172a"
                stroke="#38bdf8"
                strokeWidth="2.5"
                className="transition-transform group-hover:scale-125"
              />
              <text
                x={p.x}
                y={p.y - 10}
                fill="#f8fafc"
                fontSize="11"
                fontWeight="bold"
                textAnchor="middle"
                className="opacity-90"
              >
                {p.score}%
              </text>
              <text
                x={p.x}
                y={svgHeight - 10}
                fill="#64748b"
                fontSize="10"
                textAnchor="middle"
              >
                {p.label}
              </text>
            </g>
          ))}
        </svg>
      </div>
    </div>
  );
});
