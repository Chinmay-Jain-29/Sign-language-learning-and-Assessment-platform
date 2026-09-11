import React, { useMemo } from 'react';

/**
 * 29-Sign Canonical ASL Alphabet & Gesture Class List
 */
const CANONICAL_SIGNS = [
  'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
  'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
  'DEL', 'NOTHING', 'SPACE'
];

/**
 * Normalizes sign string keys by trimming whitespace and converting to uppercase.
 */
const normalizeSign = (sign) => String(sign || '').trim().toUpperCase();

export const MasteryMatrix = React.memo(({
  signClassification = [],
  mastered = [],
  learning = [],
  needsRevision = []
}) => {
  /**
   * Builds canonical sign-keyed dictionary.
   * STRICTLY avoids index-based mapping to prevent array order mismatch.
   */
  const classificationBySign = useMemo(() => {
    const map = {};

    // 1. Primary: Use authoritative signClassification array of objects
    if (Array.isArray(signClassification) && signClassification.length > 0) {
      signClassification.forEach((item) => {
        const key = normalizeSign(item.sign || item.character || item.sign_character);
        if (key) {
          map[key] = {
            sign: key,
            category: item.category || item.state || 'Not Attempted',
            accuracy: item.accuracy ?? (item.gesture_accuracy ?? 0.0),
            average_confidence: item.average_confidence ?? (item.confidence ?? 0.0),
            total_attempts: item.total_attempts ?? item.attempts ?? 0,
            correct_attempts: item.correct_attempts ?? 0
          };
        }
      });
    } else {
      // 2. Fallback: Parse string arrays if passed from legacy callers
      mastered.forEach((s) => {
        const k = normalizeSign(s);
        if (k) map[k] = { sign: k, category: 'Mastered' };
      });
      needsRevision.forEach((s) => {
        const k = normalizeSign(s);
        if (k) map[k] = { sign: k, category: 'Needs Revision' };
      });
      learning.forEach((s) => {
        const k = normalizeSign(s);
        if (k && !map[k]) map[k] = { sign: k, category: 'Learning' };
      });
    }

    return map;
  }, [signClassification, mastered, learning, needsRevision]);

  /**
   * Deterministic status & label mapping from canonical category.
   * Mastered -> Green
   * Learner / Learning / Practicing -> Blue
   * Revision -> Red
   * Unattempted -> Slate
   */
  const getSignPresentation = (sign) => {
    const normKey = normalizeSign(sign);
    const item = classificationBySign[normKey] || { category: 'Not Attempted' };
    const rawCat = (item.category || '').toLowerCase().trim();

    if (rawCat === 'mastered') {
      return {
        status: 'mastered',
        label: 'Mastered',
        styles: 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400 hover:bg-emerald-500/20 shadow-emerald-500/5',
        details: item
      };
    }

    if (rawCat === 'needs revision' || rawCat === 'revision') {
      return {
        status: 'revision',
        label: 'Revision',
        styles: 'bg-rose-500/10 border-rose-500/30 text-rose-400 hover:bg-rose-500/20 shadow-rose-500/5',
        details: item
      };
    }

    if (
      rawCat === 'learning' ||
      rawCat === 'learner' ||
      rawCat === 'practicing' ||
      rawCat === 'improving'
    ) {
      return {
        status: 'learning',
        label: 'Learner',
        styles: 'bg-sky-500/10 border-sky-500/30 text-sky-400 hover:bg-sky-500/20 shadow-sky-500/5',
        details: item
      };
    }

    return {
      status: 'unattempted',
      label: 'Unattempted',
      styles: 'bg-slate-800/40 border-slate-700/50 text-slate-400 hover:bg-slate-800/70',
      details: item
    };
  };

  return (
    <div className="glass-card p-5 rounded-2xl border border-slate-800/80 bg-slate-900/60 shadow-xl">
      <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-3 mb-4">
        <div>
          <h4 className="text-sm font-semibold uppercase tracking-wider text-slate-400">
            29-Sign Alphabet Mastery Matrix
          </h4>
          <p className="text-xs text-slate-400 mt-0.5">
            Real-time status breakdown across all ASL gesture classes
          </p>
        </div>
        <div className="flex flex-wrap gap-3 text-xs">
          <span className="flex items-center gap-1.5 text-emerald-400 font-medium">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span> Mastered
          </span>
          <span className="flex items-center gap-1.5 text-sky-400 font-medium">
            <span className="w-2.5 h-2.5 rounded-full bg-sky-500"></span> Learner
          </span>
          <span className="flex items-center gap-1.5 text-rose-400 font-medium">
            <span className="w-2.5 h-2.5 rounded-full bg-rose-500"></span> Revision
          </span>
          <span className="flex items-center gap-1.5 text-slate-400 font-medium">
            <span className="w-2.5 h-2.5 rounded-full bg-slate-600"></span> Unattempted
          </span>
        </div>
      </div>

      <div className="grid grid-cols-5 sm:grid-cols-8 md:grid-cols-10 gap-2.5">
        {CANONICAL_SIGNS.map((sign) => {
          const { status, label, styles, details } = getSignPresentation(sign);
          const attCount = details.total_attempts || 0;
          const accVal = details.accuracy !== undefined ? details.accuracy : 0;
          const confVal = details.average_confidence !== undefined ? details.average_confidence : 0;

          return (
            <div
              key={sign}
              id={`matrix-sign-${sign}`}
              className={`flex flex-col items-center justify-center p-2.5 rounded-xl border text-center font-bold text-xs transition-all duration-200 cursor-pointer shadow-sm ${styles}`}
              title={`${sign}: ${label} (${attCount} attempts, ${accVal}% acc, ${confVal}% conf)`}
              tabIndex={0}
              role="button"
              aria-label={`Sign ${sign}, Status ${label}, ${attCount} attempts`}
            >
              <span className="text-sm tracking-tight">{sign}</span>
              <span className="text-[10px] opacity-75 font-normal capitalize mt-0.5">
                {label}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
});
