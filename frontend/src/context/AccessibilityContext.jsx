import React, { createContext, useContext, useState, useEffect } from 'react';

const AccessibilityContext = createContext();

export const AccessibilityProvider = ({ children }) => {
  const [highContrast, setHighContrast] = useState(() => {
    return localStorage.getItem('asl_high_contrast') === 'true';
  });

  const [largeText, setLargeText] = useState(() => {
    return localStorage.getItem('asl_large_text') === 'true';
  });

  const [reducedMotion, setReducedMotion] = useState(() => {
    return localStorage.getItem('asl_reduced_motion') === 'true';
  });

  useEffect(() => {
    localStorage.setItem('asl_high_contrast', highContrast);
    if (highContrast) {
      document.documentElement.classList.add('high-contrast');
    } else {
      document.documentElement.classList.remove('high-contrast');
    }
  }, [highContrast]);

  useEffect(() => {
    localStorage.setItem('asl_large_text', largeText);
    if (largeText) {
      document.documentElement.classList.add('text-large');
    } else {
      document.documentElement.classList.remove('text-large');
    }
  }, [largeText]);

  useEffect(() => {
    localStorage.setItem('asl_reduced_motion', reducedMotion);
    if (reducedMotion) {
      document.documentElement.classList.add('reduced-motion');
    } else {
      document.documentElement.classList.remove('reduced-motion');
    }
  }, [reducedMotion]);

  return (
    <AccessibilityContext.Provider
      value={{
        highContrast,
        setHighContrast,
        largeText,
        setLargeText,
        reducedMotion,
        setReducedMotion
      }}
    >
      {children}
    </AccessibilityContext.Provider>
  );
};

export const useAccessibility = () => useContext(AccessibilityContext);
