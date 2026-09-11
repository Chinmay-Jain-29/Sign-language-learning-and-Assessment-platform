import React from 'react';

export const Input = ({
  label,
  error,
  icon: Icon,
  className = '',
  id,
  helperText,
  ...props
}) => {
  const inputId = id || (label ? label.toLowerCase().replace(/\s+/g, '-') : undefined);
  const errorId = error ? `${inputId}-error` : undefined;

  return (
    <div className="space-y-1.5 w-full">
      {label && (
        <label htmlFor={inputId} className="block text-xs font-semibold text-slate-300 uppercase tracking-wider">
          {label}
        </label>
      )}
      <div className="relative">
        {Icon && (
          <Icon className="w-5 h-5 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500 pointer-events-none" />
        )}
        <input
          id={inputId}
          aria-invalid={!!error}
          aria-describedby={errorId}
          className={`w-full bg-slate-900/90 border rounded-xl py-2.5 text-white text-sm placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-sky-500/50 transition-all ${
            Icon ? 'pl-11 pr-4' : 'px-4'
          } ${error ? 'border-rose-500 focus:border-rose-500' : 'border-slate-800 focus:border-sky-500'} ${className}`}
          {...props}
        />
      </div>
      {helperText && !error && (
        <p className="text-xs text-slate-400 mt-1">{helperText}</p>
      )}
      {error && (
        <p id={errorId} className="text-xs text-rose-400 font-medium mt-1">
          {error}
        </p>
      )}
    </div>
  );
};
