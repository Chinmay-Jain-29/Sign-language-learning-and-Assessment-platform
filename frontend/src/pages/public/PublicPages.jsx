import React from 'react';

export const About = () => (
  <div className="max-w-5xl mx-auto px-6 py-12 text-slate-100">
    <h1 className="text-3xl font-extrabold mb-4">About ASL AI Platform</h1>
    <p className="text-slate-400 text-lg leading-relaxed mb-8">
      Our platform bridges accessibility gaps in American Sign Language education by pairing high-speed MediaPipe 3D hand tracking with Random Forest machine learning.
    </p>

    <div className="grid md:grid-cols-2 gap-6">
      <div className="glass-card p-6 rounded-2xl border border-slate-800 bg-slate-900/60">
        <h3 className="text-xl font-bold mb-2 text-sky-400">Our Mission</h3>
        <p className="text-slate-400 text-sm leading-relaxed">
          Democratize sign language learning with real-time feedback, objective assessment metrics, and individualized learning pathways.
        </p>
      </div>
      <div className="glass-card p-6 rounded-2xl border border-slate-800 bg-slate-900/60">
        <h3 className="text-xl font-bold mb-2 text-emerald-400">Anatomical Accuracy</h3>
        <p className="text-slate-400 text-sm leading-relaxed">
          Provides feedback down to individual finger joints (PIP, DIP, MCP) for gesture spatial corrections.
        </p>
      </div>
    </div>
  </div>
);

export const Features = () => (
  <div className="max-w-6xl mx-auto px-6 py-12 text-slate-100">
    <h1 className="text-3xl font-extrabold mb-2">Platform Features</h1>
    <p className="text-slate-400 mb-8">Dedicated tools across 4 specialized user roles</p>

    <div className="grid md:grid-cols-2 gap-6">
      <div className="glass-card p-6 rounded-2xl border border-slate-800 bg-slate-900/60">
        <h3 className="text-xl font-bold text-sky-400 mb-2">Learner Portal</h3>
        <ul className="list-disc list-inside text-slate-400 text-sm space-y-2">
          <li>14-metric interactive progress dashboard with trend charts</li>
          <li>4-Zone Practice UI with MediaPipe 3D landmark overlays</li>
          <li>Dynamic 29-sign Alphabet Mastery Matrix</li>
          <li>Personalized recommendation engine suggestions</li>
        </ul>
      </div>

      <div className="glass-card p-6 rounded-2xl border border-slate-800 bg-slate-900/60">
        <h3 className="text-xl font-bold text-emerald-400 mb-2">Instructor Portal</h3>
        <ul className="list-disc list-inside text-slate-400 text-sm space-y-2">
          <li>Class-wide accuracy analytics and difficult sign identification</li>
          <li>Course and module content management system</li>
          <li>Student roster progress drilldown</li>
        </ul>
      </div>

      <div className="glass-card p-6 rounded-2xl border border-slate-800 bg-slate-900/60">
        <h3 className="text-xl font-bold text-indigo-400 mb-2">Accessibility Trainer Portal</h3>
        <ul className="list-disc list-inside text-slate-400 text-sm space-y-2">
          <li>Learner engagement and sign acquisition speed metrics</li>
          <li>Certification monitoring and level verification</li>
        </ul>
      </div>

      <div className="glass-card p-6 rounded-2xl border border-slate-800 bg-slate-900/60">
        <h3 className="text-xl font-bold text-purple-400 mb-2">Administrator Portal</h3>
        <ul className="list-disc list-inside text-slate-400 text-sm space-y-2">
          <li>Platform health, user accounts, and RBAC role management</li>
          <li>Model inference latency and accuracy drift monitoring</li>
          <li>System broadcast alerts and security audit logs</li>
        </ul>
      </div>
    </div>
  </div>
);

export const HowItWorks = () => (
  <div className="max-w-5xl mx-auto px-6 py-12 text-slate-100">
    <h1 className="text-3xl font-extrabold mb-2">How It Works</h1>
    <p className="text-slate-400 mb-10">4-step real-time AI recognition pipeline</p>

    <div className="space-y-6">
      {[
        { step: '01', title: 'Webcam Video Stream', desc: 'Captures live video frames directly from your camera in browser using HTML5 Canvas.' },
        { step: '02', title: 'MediaPipe 3D Hand Tracking', desc: 'Detects 21 hand keypoints (x, y, z) at sub-millimeter precision in real time.' },
        { step: '03', title: 'Normalization & Feature Vector', desc: 'Subtracts wrist origin for translation invariance and scales to maximum hand span.' },
        { step: '04', title: 'Random Forest Classification & Feedback', desc: 'Evaluates 99.38% accurate model to predict ASL sign and deliver anatomical feedback.' },
      ].map((item) => (
        <div key={item.step} className="glass-card p-6 rounded-2xl border border-slate-800 bg-slate-900/60 flex items-start gap-4">
          <span className="text-2xl font-extrabold text-sky-400 font-mono px-3 py-1 bg-sky-500/10 rounded-xl border border-sky-500/30">
            {item.step}
          </span>
          <div>
            <h3 className="text-lg font-bold text-slate-100">{item.title}</h3>
            <p className="text-sm text-slate-400 mt-1">{item.desc}</p>
          </div>
        </div>
      ))}
    </div>
  </div>
);

export const AccessibilityInfo = () => (
  <div className="max-w-5xl mx-auto px-6 py-12 text-slate-100">
    <h1 className="text-3xl font-extrabold mb-4">Accessibility Statement (WCAG 2.1 AA)</h1>
    <p className="text-slate-400 text-sm leading-relaxed mb-6">
      Our application adheres to WCAG 2.1 AA accessibility guidelines, ensuring equal access for all users.
    </p>

    <div className="glass-card p-6 rounded-2xl border border-slate-800 bg-slate-900/60 space-y-4">
      <div>
        <h4 className="font-bold text-sky-400">Keyboard Navigation</h4>
        <p className="text-xs text-slate-400 mt-1">Every element is operable using standard keyboard navigation (`Tab`, `Shift+Tab`, `Enter`, `Space`). Focus rings are highlighted with high contrast sky blue.</p>
      </div>
      <div>
        <h4 className="font-bold text-sky-400">Screen Reader Compatibility</h4>
        <p className="text-xs text-slate-400 mt-1">Interactive controls feature appropriate `aria-label`, `aria-describedby`, `role="progressbar"`, and `role="status"` live region attributes.</p>
      </div>
      <div>
        <h4 className="font-bold text-sky-400">High Contrast Palette</h4>
        <p className="text-xs text-slate-400 mt-1">Color combinations strictly exceed the minimum 4.5:1 contrast ratio required for normal text.</p>
      </div>
    </div>
  </div>
);
