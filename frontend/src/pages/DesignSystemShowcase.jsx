import React, { useState } from 'react';
import { Button } from '../components/common/Button';
import { Input } from '../components/common/Input';
import { Card } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { ProgressBar } from '../components/common/ProgressBar';
import { Modal } from '../components/common/Modal';
import { Table } from '../components/common/Table';
import { Skeleton } from '../components/common/Skeleton';
import { EmptyState } from '../components/common/EmptyState';
import { ErrorMessage } from '../components/common/ErrorMessage';
import { useToast } from '../components/common/Toast';
import { Sparkles, Mail, Lock, CheckCircle, Shield, AlertTriangle } from 'lucide-react';

export const DesignSystemShowcase = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const { showToast } = useToast();

  const sampleColumns = [
    { header: "Letter", accessor: "sign" },
    { header: "Attempts", accessor: "attempts" },
    { header: "Accuracy", render: (row) => <Badge variant={row.accuracy > 80 ? 'success' : 'warning'}>{row.accuracy}%</Badge> },
    { header: "Status", render: (row) => <Badge variant="neutral">{row.status}</Badge> }
  ];

  const sampleData = [
    { sign: "Sign A", attempts: 15, accuracy: 92, status: "Mastered" },
    { sign: "Sign B", attempts: 8, accuracy: 64, status: "Improving" },
    { sign: "Sign C", attempts: 3, accuracy: 45, status: "Learning" }
  ];

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-10 animate-fade-in">
      <div className="space-y-2 border-b border-slate-800 pb-6">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-sky-500/10 border border-sky-500/20 text-sky-400">
            <Sparkles className="w-6 h-6" />
          </div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight">
            UI/UX Design System Showcase (Phase 1)
          </h1>
        </div>
        <p className="text-slate-400 text-sm">
          Comprehensive EdTech Accessibility Component Library built with WCAG 2.1 AA design tokens, glassmorphic themes, and responsive layouts.
        </p>
      </div>

      {/* Buttons & Badges */}
      <Card hover={false} className="space-y-6">
        <h2 className="text-lg font-bold text-white border-b border-slate-800 pb-3">1. Buttons & Status Badges</h2>
        
        <div className="flex flex-wrap gap-4 items-center">
          <Button variant="primary" icon={Sparkles}>Primary Button</Button>
          <Button variant="secondary" icon={CheckCircle}>Secondary Button</Button>
          <Button variant="outline">Outline Button</Button>
          <Button variant="danger" icon={AlertTriangle}>Danger Action</Button>
          <Button variant="ghost">Ghost Button</Button>
          <Button variant="primary" isLoading={true}>Loading State</Button>
        </div>

        <div className="flex flex-wrap gap-3 items-center pt-2">
          <Badge variant="info">Info Badge</Badge>
          <Badge variant="success">Success Badge</Badge>
          <Badge variant="warning">Warning Badge</Badge>
          <Badge variant="danger">Danger Badge</Badge>
          <Badge variant="neutral">Neutral Badge</Badge>
        </div>
      </Card>

      {/* Inputs & Form Controls */}
      <Card hover={false} className="space-y-6">
        <h2 className="text-lg font-bold text-white border-b border-slate-800 pb-3">2. Inputs & Form Components</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Input label="Email Address" icon={Mail} placeholder="learner@example.com" helperText="We will never share your email." />
          <Input label="Password" icon={Lock} type="password" placeholder="••••••••" error="Password must be at least 8 characters long." />
        </div>
      </Card>

      {/* Progress Bars & Skeletons */}
      <Card hover={false} className="space-y-6">
        <h2 className="text-lg font-bold text-white border-b border-slate-800 pb-3">3. Progress Indicators & Loading Skeletons</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-4">
            <ProgressBar label="ASL Alphabet Mastery" value={78} color="sky" />
            <ProgressBar label="Gesture Stability Score" value={92} color="emerald" />
            <ProgressBar label="Assessment Progress" value={45} color="amber" />
          </div>
          <div className="space-y-3">
            <p className="text-xs font-semibold text-slate-400 uppercase">Skeleton Loader Line</p>
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-3/4" />
            <Skeleton className="h-10 w-1/2" />
          </div>
        </div>
      </Card>

      {/* Interactive Toasts & Modals */}
      <Card hover={false} className="space-y-6">
        <h2 className="text-lg font-bold text-white border-b border-slate-800 pb-3">4. Interactive Modals & Toast Alerts</h2>
        <div className="flex flex-wrap gap-4">
          <Button onClick={() => setIsModalOpen(true)} variant="primary">Open Accessible Modal</Button>
          <Button onClick={() => showToast('Practice attempt saved successfully!', 'success')} variant="secondary">Success Toast</Button>
          <Button onClick={() => showToast('Invalid gesture position detected.', 'warning')} variant="outline">Warning Toast</Button>
          <Button onClick={() => showToast('Failed to connect to AI engine.', 'danger')} variant="danger">Error Toast</Button>
        </div>
      </Card>

      {/* Data Table */}
      <Card hover={false} className="space-y-6">
        <h2 className="text-lg font-bold text-white border-b border-slate-800 pb-3">5. Accessible Data Table</h2>
        <Table columns={sampleColumns} data={sampleData} />
      </Card>

      {/* Error & Empty States */}
      <Card hover={false} className="space-y-6">
        <h2 className="text-lg font-bold text-white border-b border-slate-800 pb-3">6. Error & Empty States</h2>
        <ErrorMessage message="Authentication token expired. Please log in again to continue." />
        <EmptyState
          title="No Practice Attempts Recorded"
          description="Start your first ASL practice session using the interactive camera view."
          actionLabel="Start Practice"
          onAction={() => showToast('Navigating to Practice...', 'info')}
        />
      </Card>

      {/* Modal Integration */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Phase 1 Design System Modal"
        footer={
          <>
            <Button variant="outline" onClick={() => setIsModalOpen(false)}>Cancel</Button>
            <Button variant="primary" onClick={() => { setIsModalOpen(false); showToast('Modal Action Executed', 'success'); }}>Confirm</Button>
          </>
        }
      >
        <p className="text-sm text-slate-300 leading-relaxed">
          This accessible modal dialog features backdrop blur, ARIA accessibility bindings, focus handling, Esc key closure, and smooth fade animations.
        </p>
      </Modal>
    </div>
  );
};
