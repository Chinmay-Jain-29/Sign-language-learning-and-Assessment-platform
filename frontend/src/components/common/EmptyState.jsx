import React from 'react';
import { HelpCircle } from 'lucide-react';
import { Button } from './Button';

export const EmptyState = ({
  title = "No Data Available",
  description = "There are currently no items to display.",
  icon: Icon = HelpCircle,
  actionLabel,
  onAction,
  className = ''
}) => {
  return (
    <div className={`glass-panel p-8 rounded-2xl text-center flex flex-col items-center justify-center space-y-3 ${className}`}>
      <div className="p-4 rounded-2xl bg-slate-900 border border-slate-800 text-slate-500 mb-1">
        <Icon className="w-10 h-10" />
      </div>
      <h3 className="text-base font-bold text-white">{title}</h3>
      <p className="text-xs text-slate-400 max-w-sm">{description}</p>
      {actionLabel && onAction && (
        <Button onClick={onAction} size="sm" className="mt-2">
          {actionLabel}
        </Button>
      )}
    </div>
  );
};
