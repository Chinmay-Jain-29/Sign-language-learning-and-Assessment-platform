import React from 'react';
import { AlertCircle } from 'lucide-react';

export const ErrorMessage = ({ message = "An error occurred", className = '' }) => {
  return (
    <div className={`p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs font-semibold flex items-center gap-3 ${className}`}>
      <AlertCircle className="w-5 h-5 flex-shrink-0" />
      <span>{message}</span>
    </div>
  );
};
