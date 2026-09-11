import React from 'react';
import { EmptyState } from './EmptyState';

export const Table = ({
  columns = [],
  data = [],
  emptyTitle = "No records found",
  emptyDescription = "There are no data items available to display.",
  onRowClick,
  className = ''
}) => {
  if (!data || data.length === 0) {
    return <EmptyState title={emptyTitle} description={emptyDescription} />;
  }

  return (
    <div className={`w-full overflow-x-auto rounded-xl border border-slate-800 glass-panel ${className}`}>
      <table className="w-full text-left border-collapse">
        <thead>
          <tr className="border-b border-slate-800 bg-slate-900/60 text-xs font-semibold text-slate-400 uppercase tracking-wider">
            {columns.map((col, idx) => (
              <th key={idx} className={`px-4 py-3.5 ${col.className || ''}`}>
                {col.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-800/60 text-xs text-slate-300">
          {data.map((row, rowIdx) => (
            <tr
              key={rowIdx}
              onClick={() => onRowClick && onRowClick(row)}
              className={`transition-colors ${
                onRowClick ? 'cursor-pointer hover:bg-slate-800/40' : 'hover:bg-slate-800/20'
              }`}
            >
              {columns.map((col, colIdx) => (
                <td key={colIdx} className={`px-4 py-3.5 ${col.className || ''}`}>
                  {col.render ? col.render(row, rowIdx) : row[col.accessor]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
