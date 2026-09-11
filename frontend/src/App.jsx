import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { AccessibilityProvider } from './context/AccessibilityContext';
import { ToastProvider } from './components/common/Toast';
import { ErrorBoundary } from './components/common/ErrorBoundary';
import { Navbar } from './components/layout/Navbar';

// Auth Pages
import { Login } from './pages/auth/Login';
import { Register } from './pages/auth/Register';
import { ForgotPassword } from './pages/auth/ForgotPassword';
import { ResetPassword } from './pages/auth/ResetPassword';

// Public Pages
import { Landing } from './pages/public/Landing';
import { About, Features, HowItWorks, AccessibilityInfo } from './pages/public/PublicPages';

// Profile & Achievements Pages (Shared Across All Roles)
import { Profile } from './pages/profile/Profile';
import { Achievements } from './pages/learner/Achievements';

// Learner Pages
import { LearnerDashboard } from './pages/learner/Dashboard';
import { PracticeModes } from './pages/learner/PracticeModes';
import { Practice } from './pages/learner/Practice';
import { IntermediatePractice } from './pages/learner/IntermediatePractice';
import { ExpertPractice } from './pages/learner/ExpertPractice';
import { AdvancedPractice } from './pages/learner/AdvancedPractice';
import { PracticeLevelGuard } from './components/practice/PracticeLevelGuard';
import {
  Courses, CourseDetails, LessonDetails, PracticeSelection,
  LiveRecognition, AssessmentResult, PracticeReview, Progress, SkillMastery,
  Recommendations, PracticeHistory, Reports, Certification, Notifications, Settings
} from './pages/learner/LearnerPages';

// Instructor Pages
import {
  InstructorDashboard, Students, StudentDetails, ClassProgress,
  AssessmentAnalytics, WeakAreas, CourseManagement, LessonManagement, InstructorReports
} from './pages/instructor/InstructorPages';

// Trainer Pages
import {
  TrainerDashboard, LearnerEngagement, SkillDevelopment,
  TrainerAssessmentAnalytics, CertificationMonitoring, TrainerReports
} from './pages/trainer/TrainerPages';

// Admin Pages
import { AdminDashboard } from './pages/admin/Dashboard';
import {
  UserManagement, RoleManagement, AdminCourseManagement,
  ContentManagement, PlatformAnalytics, SystemMonitoring, ModelAIMonitoring,
  AdminNotifications, AuditLogs
} from './pages/admin/AdminPages';

import { DesignSystemShowcase } from './pages/DesignSystemShowcase';

/**
 * Reusable Route Guard:
 * - Shows a clean loading state while authentication is being resolved.
 * - If user is unauthenticated, directly returns the public Landing Page component.
 * - If user is authenticated, verifies role authorization and renders the requested protected page.
 */
const ProtectedRoute = ({ children, allowedRoles }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-950 text-slate-400">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 border-2 border-sky-500 border-t-transparent rounded-full animate-spin"></div>
          <span className="text-sm font-medium">Authenticating...</span>
        </div>
      </div>
    );
  }

  // Unauthenticated direct access to any protected route renders the canonical Landing page
  if (!user) {
    return <Landing />;
  }

  // Role authorization guard
  if (allowedRoles && !allowedRoles.includes(user.role)) {
    if (user.role === 'Instructor') return <Navigate to="/instructor" replace />;
    if (user.role === 'Accessibility Trainer') return <Navigate to="/trainer" replace />;
    if (user.role === 'Administrator') return <Navigate to="/admin" replace />;
    return <Navigate to="/dashboard" replace />;
  }

  return children;
};

export default function App() {
  return (
    <AccessibilityProvider>
      <AuthProvider>
        <ToastProvider>
          <BrowserRouter>
            <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
              <Navbar />
              <main className="flex-1">
                <ErrorBoundary>
                  <Routes>
                    {/* Public Pages */}
                    <Route path="/" element={<Landing />} />
                    <Route path="/about" element={<About />} />
                    <Route path="/features" element={<Features />} />
                    <Route path="/how-it-works" element={<HowItWorks />} />
                    <Route path="/accessibility-info" element={<AccessibilityInfo />} />
                    <Route path="/login" element={<Login />} />
                    <Route path="/register" element={<Register />} />
                    <Route path="/forgot-password" element={<ForgotPassword />} />
                    <Route path="/reset-password" element={<ResetPassword />} />
                    <Route path="/design-system" element={<DesignSystemShowcase />} />

                    {/* Learner Protected Routes */}
                    <Route path="/dashboard" element={<ProtectedRoute allowedRoles={['Learner']}><LearnerDashboard /></ProtectedRoute>} />
                    {/* Practice Level Navigation & Route Protected Hierarchy */}
                    <Route path="/practice" element={<ProtectedRoute allowedRoles={['Learner']}><PracticeModes /></ProtectedRoute>} />
                    <Route path="/practice/beginner" element={<ProtectedRoute allowedRoles={['Learner']}><Practice /></ProtectedRoute>} />
                    <Route path="/webcam-practice" element={<ProtectedRoute allowedRoles={['Learner']}><Practice /></ProtectedRoute>} />
                    <Route path="/practice/intermediate" element={<ProtectedRoute allowedRoles={['Learner']}><PracticeLevelGuard requiredLevel="Intermediate"><IntermediatePractice /></PracticeLevelGuard></ProtectedRoute>} />
                    <Route path="/practice/expert" element={<ProtectedRoute allowedRoles={['Learner']}><PracticeLevelGuard requiredLevel="Expert"><ExpertPractice /></PracticeLevelGuard></ProtectedRoute>} />
                    <Route path="/practice/advanced" element={<ProtectedRoute allowedRoles={['Learner']}><PracticeLevelGuard requiredLevel="Expert"><AdvancedPractice /></PracticeLevelGuard></ProtectedRoute>} />
                    <Route path="/lessons" element={<ProtectedRoute allowedRoles={['Learner']}><Courses /></ProtectedRoute>} />
                    <Route path="/lessons/:id" element={<ProtectedRoute allowedRoles={['Learner']}><LessonDetails /></ProtectedRoute>} />
                    <Route path="/courses" element={<ProtectedRoute allowedRoles={['Learner']}><Courses /></ProtectedRoute>} />
                    <Route path="/courses/:id" element={<ProtectedRoute allowedRoles={['Learner']}><CourseDetails /></ProtectedRoute>} />
                    <Route path="/quizzes" element={<ProtectedRoute allowedRoles={['Learner']}><SkillMastery /></ProtectedRoute>} />
                    <Route path="/assessments" element={<ProtectedRoute allowedRoles={['Learner']}><SkillMastery /></ProtectedRoute>} />
                    <Route path="/certificate" element={<ProtectedRoute allowedRoles={['Learner']}><Certification /></ProtectedRoute>} />
                    <Route path="/certification" element={<ProtectedRoute allowedRoles={['Learner']}><Certification /></ProtectedRoute>} />
                    <Route path="/profile" element={<ProtectedRoute allowedRoles={['Learner', 'Instructor', 'Accessibility Trainer', 'Administrator']}><Profile /></ProtectedRoute>} />
                    <Route path="/achievements" element={<ProtectedRoute allowedRoles={['Learner', 'Instructor', 'Accessibility Trainer', 'Administrator']}><Achievements /></ProtectedRoute>} />
                    <Route path="/practice-selection" element={<ProtectedRoute allowedRoles={['Learner']}><PracticeSelection /></ProtectedRoute>} />
                    <Route path="/live-recognition" element={<ProtectedRoute allowedRoles={['Learner']}><LiveRecognition /></ProtectedRoute>} />
                    <Route path="/assessment-result" element={<ProtectedRoute allowedRoles={['Learner']}><AssessmentResult /></ProtectedRoute>} />
                    <Route path="/practice-review" element={<ProtectedRoute allowedRoles={['Learner']}><PracticeReview /></ProtectedRoute>} />
                    <Route path="/progress" element={<ProtectedRoute allowedRoles={['Learner']}><Progress /></ProtectedRoute>} />
                    <Route path="/skill-mastery" element={<ProtectedRoute allowedRoles={['Learner']}><SkillMastery /></ProtectedRoute>} />
                    <Route path="/recommendations" element={<ProtectedRoute allowedRoles={['Learner']}><Recommendations /></ProtectedRoute>} />
                    <Route path="/practice-history" element={<ProtectedRoute allowedRoles={['Learner']}><PracticeHistory /></ProtectedRoute>} />
                    <Route path="/reports" element={<ProtectedRoute allowedRoles={['Learner']}><Reports /></ProtectedRoute>} />
                    <Route path="/notifications" element={<ProtectedRoute allowedRoles={['Learner']}><Notifications /></ProtectedRoute>} />
                    <Route path="/settings" element={<ProtectedRoute allowedRoles={['Learner']}><Settings /></ProtectedRoute>} />

                    {/* Instructor Protected Routes */}
                    <Route path="/instructor" element={<ProtectedRoute allowedRoles={['Instructor', 'Administrator']}><InstructorDashboard /></ProtectedRoute>} />
                    <Route path="/instructor/students" element={<ProtectedRoute allowedRoles={['Instructor', 'Administrator']}><Students /></ProtectedRoute>} />
                    <Route path="/instructor/students/:id" element={<ProtectedRoute allowedRoles={['Instructor', 'Administrator']}><StudentDetails /></ProtectedRoute>} />
                    <Route path="/instructor/class-progress" element={<ProtectedRoute allowedRoles={['Instructor', 'Administrator']}><ClassProgress /></ProtectedRoute>} />
                    <Route path="/instructor/assessment-analytics" element={<ProtectedRoute allowedRoles={['Instructor', 'Administrator']}><AssessmentAnalytics /></ProtectedRoute>} />
                    <Route path="/instructor/weak-areas" element={<ProtectedRoute allowedRoles={['Instructor', 'Administrator']}><WeakAreas /></ProtectedRoute>} />
                    <Route path="/instructor/course-management" element={<ProtectedRoute allowedRoles={['Instructor', 'Administrator']}><CourseManagement /></ProtectedRoute>} />
                    <Route path="/instructor/lesson-management" element={<ProtectedRoute allowedRoles={['Instructor', 'Administrator']}><LessonManagement /></ProtectedRoute>} />
                    <Route path="/instructor/reports" element={<ProtectedRoute allowedRoles={['Instructor', 'Administrator']}><InstructorReports /></ProtectedRoute>} />

                    {/* Accessibility Trainer Protected Routes */}
                    <Route path="/trainer" element={<ProtectedRoute allowedRoles={['Accessibility Trainer', 'Administrator']}><TrainerDashboard /></ProtectedRoute>} />
                    <Route path="/trainer/learner-engagement" element={<ProtectedRoute allowedRoles={['Accessibility Trainer', 'Administrator']}><LearnerEngagement /></ProtectedRoute>} />
                    <Route path="/trainer/skill-development" element={<ProtectedRoute allowedRoles={['Accessibility Trainer', 'Administrator']}><SkillDevelopment /></ProtectedRoute>} />
                    <Route path="/trainer/assessment-analytics" element={<ProtectedRoute allowedRoles={['Accessibility Trainer', 'Administrator']}><TrainerAssessmentAnalytics /></ProtectedRoute>} />
                    <Route path="/trainer/certification-monitoring" element={<ProtectedRoute allowedRoles={['Accessibility Trainer', 'Administrator']}><CertificationMonitoring /></ProtectedRoute>} />
                    <Route path="/trainer/reports" element={<ProtectedRoute allowedRoles={['Accessibility Trainer', 'Administrator']}><TrainerReports /></ProtectedRoute>} />

                    {/* Admin Protected Routes */}
                    <Route path="/admin" element={<ProtectedRoute allowedRoles={['Administrator']}><AdminDashboard /></ProtectedRoute>} />
                    <Route path="/admin/user-management" element={<ProtectedRoute allowedRoles={['Administrator']}><UserManagement /></ProtectedRoute>} />
                    <Route path="/admin/role-management" element={<ProtectedRoute allowedRoles={['Administrator']}><RoleManagement /></ProtectedRoute>} />
                    <Route path="/admin/course-management" element={<ProtectedRoute allowedRoles={['Administrator']}><AdminCourseManagement /></ProtectedRoute>} />
                    <Route path="/admin/content-management" element={<ProtectedRoute allowedRoles={['Administrator']}><ContentManagement /></ProtectedRoute>} />
                    <Route path="/admin/platform-analytics" element={<ProtectedRoute allowedRoles={['Administrator']}><PlatformAnalytics /></ProtectedRoute>} />
                    <Route path="/admin/system-monitoring" element={<ProtectedRoute allowedRoles={['Administrator']}><SystemMonitoring /></ProtectedRoute>} />
                    <Route path="/admin/model-ai-monitoring" element={<ProtectedRoute allowedRoles={['Administrator']}><ModelAIMonitoring /></ProtectedRoute>} />
                    <Route path="/admin/notifications" element={<ProtectedRoute allowedRoles={['Administrator']}><AdminNotifications /></ProtectedRoute>} />
                    <Route path="/admin/audit-logs" element={<ProtectedRoute allowedRoles={['Administrator']}><AuditLogs /></ProtectedRoute>} />

                    {/* Fallback */}
                    <Route path="*" element={<Navigate to="/" replace />} />
                  </Routes>
                </ErrorBoundary>
              </main>
            </div>
          </BrowserRouter>
        </ToastProvider>
      </AuthProvider>
    </AccessibilityProvider>
  );
}
