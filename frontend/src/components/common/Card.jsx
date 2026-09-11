import React from 'react';

export const Card = ({ children, className = '', hover = true, ...props }) => {
  return (
    <div
      className={`${hover ? 'glass-card' : 'glass-panel'} p-6 rounded-2xl ${className}`}
      {...props}
    >
      {children}
    </div>
  );
};
