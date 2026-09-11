import React from 'react';
import { Navigate } from 'react-router-dom';

export const Register = () => {
  // Seamlessly routes to the unified Auth page with Register active
  return <Navigate to="/login" replace state={{ tab: 'register' }} />;
};
