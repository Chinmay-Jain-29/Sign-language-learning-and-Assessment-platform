import React from 'react';
import { 
  Camera, Lock, AlertOctagon, HelpCircle, Users, EyeOff, ZoomIn, ZoomOut, 
  CheckCircle2, RefreshCw, Sparkles, Activity, CheckSquare 
} from 'lucide-react';

export const WEBCAM_STATES = {
  PERMISSION_REQUESTED: 'permission_requested',
  PERMISSION_DENIED: 'permission_denied',
  CAMERA_UNAVAILABLE: 'camera_unavailable',
  NO_HAND_DETECTED: 'no_hand_detected',
  MULTIPLE_HANDS: 'multiple_hands',
  MULTIPLE_PEOPLE: 'multiple_people',
  PARTIAL_HAND: 'partial_hand',
  POOR_VISIBILITY: 'poor_visibility',
  HAND_TOO_FAR: 'hand_too_far',
  HAND_TOO_CLOSE: 'hand_too_close',
  VALID_INPUT: 'valid_input',
  PROCESSING: 'processing',
  PREDICTION: 'prediction',
  STABLE_PREDICTION: 'stable_prediction',
  ASSESSMENT_COMPLETE: 'assessment_complete'
};

export const WebcamStateIndicator = ({ state = WEBCAM_STATES.NO_HAND_DETECTED, customMessage }) => {
  const getStateConfig = () => {
    switch (state) {
      case WEBCAM_STATES.PERMISSION_REQUESTED:
        return {
          icon: <Camera className="w-5 h-5 text-sky-400 animate-pulse" />,
          title: 'Camera Permission Requested',
          message: 'Please allow browser camera permissions to initiate hand tracking.',
          badgeColor: 'bg-sky-500/20 text-sky-300 border-sky-500/40',
          ariaLive: 'polite'
        };
      case WEBCAM_STATES.PERMISSION_DENIED:
        return {
          icon: <Lock className="w-5 h-5 text-rose-400" />,
          title: 'Camera Permission Denied',
          message: 'Webcam permission was blocked. Enable camera access in browser settings.',
          badgeColor: 'bg-rose-500/20 text-rose-300 border-rose-500/40',
          ariaLive: 'assertive'
        };
      case WEBCAM_STATES.CAMERA_UNAVAILABLE:
        return {
          icon: <AlertOctagon className="w-5 h-5 text-rose-400" />,
          title: 'Camera Unavailable',
          message: 'No active webcam detected. Connect a camera or check device manager.',
          badgeColor: 'bg-rose-500/20 text-rose-300 border-rose-500/40',
          ariaLive: 'assertive'
        };
      case WEBCAM_STATES.NO_HAND_DETECTED:
        return {
          icon: <HelpCircle className="w-5 h-5 text-amber-400" />,
          title: 'No Hand Detected',
          message: 'Show the sign — Position your hand clearly within the camera frame.',
          badgeColor: 'bg-amber-500/20 text-amber-300 border-amber-500/40',
          ariaLive: 'polite'
        };
      case WEBCAM_STATES.MULTIPLE_HANDS:
        return {
          icon: <Users className="w-5 h-5 text-amber-400" />,
          title: 'Multiple Hands Detected',
          message: 'Please present only one hand for single-hand gesture evaluation.',
          badgeColor: 'bg-amber-500/20 text-amber-300 border-amber-500/40',
          ariaLive: 'polite'
        };
      case WEBCAM_STATES.MULTIPLE_PEOPLE:
        return {
          icon: <Users className="w-5 h-5 text-indigo-400" />,
          title: 'Multiple People in View',
          message: 'Ensure only one person is centered in the camera view for accuracy.',
          badgeColor: 'bg-indigo-500/20 text-indigo-300 border-indigo-500/40',
          ariaLive: 'polite'
        };
      case WEBCAM_STATES.PARTIAL_HAND:
        return {
          icon: <EyeOff className="w-5 h-5 text-amber-400" />,
          title: 'Partial Hand Detected',
          message: 'Fingertips or wrist cropped. Move your hand fully into frame.',
          badgeColor: 'bg-amber-500/20 text-amber-300 border-amber-500/40',
          ariaLive: 'polite'
        };
      case WEBCAM_STATES.POOR_VISIBILITY:
        return {
          icon: <EyeOff className="w-5 h-5 text-rose-400" />,
          title: 'Poor Lighting / Visibility',
          message: 'Lighting is low or background blur interferes with keypoint tracking.',
          badgeColor: 'bg-rose-500/20 text-rose-300 border-rose-500/40',
          ariaLive: 'polite'
        };
      case WEBCAM_STATES.HAND_TOO_FAR:
        return {
          icon: <ZoomIn className="w-5 h-5 text-sky-400" />,
          title: 'Hand Too Far Away',
          message: 'Move your hand closer to the camera to resolve landmark coordinates.',
          badgeColor: 'bg-sky-500/20 text-sky-300 border-sky-500/40',
          ariaLive: 'polite'
        };
      case WEBCAM_STATES.HAND_TOO_CLOSE:
        return {
          icon: <ZoomOut className="w-5 h-5 text-sky-400" />,
          title: 'Hand Too Close',
          message: 'Move your hand back slightly so wrist and all 5 fingers remain visible.',
          badgeColor: 'bg-sky-500/20 text-sky-300 border-sky-500/40',
          ariaLive: 'polite'
        };
      case WEBCAM_STATES.VALID_INPUT:
        return {
          icon: <CheckCircle2 className="w-5 h-5 text-emerald-400" />,
          title: 'Hand Detected & Position Valid',
          message: 'Optimal geometry captured. Ready for sign evaluation.',
          badgeColor: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40',
          ariaLive: 'polite'
        };
      case WEBCAM_STATES.PROCESSING:
        return {
          icon: <RefreshCw className="w-5 h-5 text-sky-400 animate-spin" />,
          title: 'Analyzing...',
          message: 'Extracting 21 3D spatial landmarks and calculating normalization.',
          badgeColor: 'bg-sky-500/20 text-sky-300 border-sky-500/40',
          ariaLive: 'polite'
        };
      case WEBCAM_STATES.PREDICTION:
        return {
          icon: <Activity className="w-5 h-5 text-indigo-400" />,
          title: 'Evaluating Sign Prediction',
          message: 'Random Forest model classifying landmark feature vector.',
          badgeColor: 'bg-indigo-500/20 text-indigo-300 border-indigo-500/40',
          ariaLive: 'polite'
        };
      case WEBCAM_STATES.STABLE_PREDICTION:
        return {
          icon: <Sparkles className="w-5 h-5 text-emerald-400" />,
          title: 'Prediction Stabilized',
          message: 'Multi-frame consensus achieved across temporal landmark window.',
          badgeColor: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40',
          ariaLive: 'polite'
        };
      case WEBCAM_STATES.ASSESSMENT_COMPLETE:
        return {
          icon: <CheckSquare className="w-5 h-5 text-emerald-400" />,
          title: 'Assessment Complete',
          message: 'Attempt logged to database. Anatomical feedback generated.',
          badgeColor: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40',
          ariaLive: 'polite'
        };
      default:
        return {
          icon: <Camera className="w-5 h-5 text-sky-400" />,
          title: 'Camera Ready',
          message: 'Show the sign to evaluate gesture.',
          badgeColor: 'bg-sky-500/20 text-sky-300 border-sky-500/40',
          ariaLive: 'polite'
        };
    }
  };

  const config = getStateConfig();

  return (
    <div
      className={`p-3.5 rounded-xl border flex items-center justify-between gap-3 shadow-md transition-all ${config.badgeColor}`}
      role="status"
      aria-live={config.ariaLive}
    >
      <div className="flex items-center gap-3">
        <div className="p-2 rounded-lg bg-slate-950/40 border border-white/10">
          {config.icon}
        </div>
        <div>
          <h4 className="text-xs font-extrabold uppercase tracking-wider text-slate-100">{config.title}</h4>
          <p className="text-xs text-slate-200 mt-0.5">{customMessage || config.message}</p>
        </div>
      </div>

      <span className="text-[10px] font-bold uppercase tracking-widest px-2.5 py-1 rounded-md bg-slate-950/60 border border-white/10 text-white whitespace-nowrap">
        {state.replace(/_/g, ' ')}
      </span>
    </div>
  );
};
