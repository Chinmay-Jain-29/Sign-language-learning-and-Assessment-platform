import React, { useState, useEffect, useRef } from 'react';
import { Link, useSearchParams, useNavigate, useLocation } from 'react-router-dom';
import api from '../../api/client';
import { WebcamStateIndicator, WEBCAM_STATES } from '../../components/practice/WebcamStateIndicator';
import { DeveloperDiagnosticsOverlay } from '../../components/practice/DeveloperDiagnosticsOverlay';
import { 
  Camera, CheckCircle2, AlertTriangle, Sparkles, Clock, Target, 
  ArrowRight, ArrowLeft, Play, Square, Info, XCircle, ShieldCheck, 
  Trophy, RefreshCw, SwitchCamera
} from 'lucide-react';

export const Practice = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const location = useLocation();

  const alphabet = Array.from({ length: 26 }, (_, i) => String.fromCharCode(65 + i));

  // Determine initial target sign from URL query parameter (e.g. ?target=D or ?sign=D)
  const getInitialTarget = () => {
    const rawTarget = searchParams.get('target') || searchParams.get('sign');
    if (rawTarget && typeof rawTarget === 'string') {
      const clean = rawTarget.trim().toUpperCase();
      if (alphabet.includes(clean)) {
        return clean;
      }
    }
    return 'A';
  };

  const hasExplicitTarget = Boolean(searchParams.get('target') || searchParams.get('sign'));
  const initialTarget = getInitialTarget();

  // Target Expected Sign (Learner selects ONLY target sign)
  const [selectedSign, setSelectedSign] = useState(initialTarget);
  const [isCameraActive, setIsCameraActive] = useState(false);
  const [facingMode, setFacingMode] = useState('user'); // 'user' (front) or 'environment' (rear)
  const [webcamState, setWebcamState] = useState(WEBCAM_STATES.NO_HAND_DETECTED);
  
  // Real-Time ML Model Outputs (Derived solely from MediaPipe + Trained RF Model)
  const [detectedSign, setDetectedSign] = useState(null);
  const [detectionConfidence, setDetectionConfidence] = useState(null);
  const [isSignCorrect, setIsSignCorrect] = useState(null);
  const [inferenceLatency, setInferenceLatency] = useState(0.0);
  const [roundTripLatency, setRoundTripLatency] = useState(0.0);
  const [feedbackMessage, setFeedbackMessage] = useState(`Position your hand in front of the camera to begin practicing sign '${initialTarget}'.`);
  const [hasValidHand, setHasValidHand] = useState(false);

  // Diagnostic HUD Telemetry State
  const [cameraInfo, setCameraInfo] = useState({
    resolution: '—',
    fps: 0,
    facingMode: 'user',
    orientation: 'portrait',
    readyState: '—'
  });
  const [mediaPipeInfo, setMediaPipeInfo] = useState({
    status: 'Standby',
    hasHand: false,
    landmarkCount: 0,
    fps: 0
  });
  const [networkInfo, setNetworkInfo] = useState({
    mode: 'Landmarks JSON (500B)',
    inFlight: false,
    rttMs: 0
  });

  // Session Statistics
  const [attemptCount, setAttemptCount] = useState(0);
  const [correctAttempts, setCorrectAttempts] = useState(0);
  const [sessionAccuracy, setSessionAccuracy] = useState('0.0');
  const [sessionTime, setSessionTime] = useState(0);
  const [sessionId, setSessionId] = useState(null);
  const [recommendation, setRecommendation] = useState(null);
  const [masteryData, setMasteryData] = useState([]);

  // Refs for State Synchronization & Memory Management
  const targetSignRef = useRef(initialTarget);
  const targetGenerationRef = useRef(1); // Incremented on each target change to discard in-flight race condition responses
  const facingModeRef = useRef('user');
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const handsInstanceRef = useRef(null);
  const animFrameIdRef = useRef(null);
  const isTrackingRunningRef = useRef(false);
  const isHandsBusyRef = useRef(false);
  const timerRef = useRef(null);
  const lastInferenceTimeRef = useRef(0);
  const isInferringRef = useRef(false);
  const abortControllerRef = useRef(null);
  const frameIntervalRef = useRef(null);
  
  // FPS Telemetry Counters
  const mpFramesCountRef = useRef(0);
  const lastMpFpsTimeRef = useRef(performance.now());
  const cameraFramesCountRef = useRef(0);
  const lastCameraFpsTimeRef = useRef(performance.now());

  // Handle in-app query parameter updates (e.g., clicking different achievement links)
  useEffect(() => {
    const rawTarget = searchParams.get('target') || searchParams.get('sign');
    if (rawTarget && typeof rawTarget === 'string') {
      const clean = rawTarget.trim().toUpperCase();
      if (alphabet.includes(clean) && clean !== targetSignRef.current) {
        handleTargetChange(clean);
      }
    }
  }, [searchParams]);

  // Window resize & orientation change listener to keep canvas scaled 1:1
  useEffect(() => {
    const handleResize = () => {
      syncCanvasDimensions();
      const isPortrait = window.innerHeight > window.innerWidth;
      setCameraInfo(prev => ({
        ...prev,
        orientation: isPortrait ? 'portrait' : 'landscape'
      }));
    };

    window.addEventListener('resize', handleResize);
    window.addEventListener('orientationchange', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      window.removeEventListener('orientationchange', handleResize);
    };
  }, []);

  // Initialize practice session & recommendations on mount
  useEffect(() => {
    initSession();
    fetchRecommendation();
    fetchMastery();

    timerRef.current = setInterval(() => {
      setSessionTime((prev) => prev + 1);
    }, 1000);

    return () => {
      stopCamera();
      if (timerRef.current) clearInterval(timerRef.current);
      if (frameIntervalRef.current) clearInterval(frameIntervalRef.current);
    };
  }, []);

  const initSession = async () => {
    try {
      const res = await api.post('/practice/sessions/start', ['A', 'B', 'C', 'D']);
      if (res.data && res.data.session_id) {
        setSessionId(res.data.session_id);
      }
    } catch (err) {
      console.error("Session start notice:", err);
    }
  };

  const fetchRecommendation = async () => {
    try {
      const res = await api.get('/recommendations/next-sign');
      if (res.data) {
        setRecommendation(res.data);
        if (res.data.recommended_sign && !hasExplicitTarget) {
          handleTargetChange(res.data.recommended_sign);
        }
      }
    } catch (err) {
      console.error("Failed to load recommendation:", err);
    }
  };

  const fetchMastery = async () => {
    try {
      const res = await api.get('/practice/mastery');
      if (res.data) {
        setMasteryData(res.data);
      }
    } catch (err) {
      console.error("Failed to load mastery:", err);
    }
  };

  /**
   * Synchronizes Canvas Buffer Dimensions directly with Video Native Stream
   */
  const syncCanvasDimensions = () => {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    if (video && canvas && video.videoWidth > 0 && video.videoHeight > 0) {
      if (canvas.width !== video.videoWidth || canvas.height !== video.videoHeight) {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        setCameraInfo(prev => ({
          ...prev,
          resolution: `${video.videoWidth}x${video.videoHeight}`
        }));
      }
    }
  };

  /**
   * Authoritative Target Change Handler:
   * Resets transient prediction states without dropping camera or MediaPipe stream.
   */
  const handleTargetChange = (newTarget) => {
    if (!newTarget) return;
    const cleanTarget = newTarget.trim().toUpperCase();

    // Invalidate in-flight inference generation
    targetGenerationRef.current += 1;
    targetSignRef.current = cleanTarget;
    setSelectedSign(cleanTarget);

    // Abort pending fetch if any
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    isInferringRef.current = false;

    // Reset transient evaluation state immediately
    setDetectedSign(null);
    setDetectionConfidence(null);
    setIsSignCorrect(null);
    setWebcamState(WEBCAM_STATES.PROCESSING);
    setFeedbackMessage(`Target updated to '${cleanTarget}'. Hold your hand steady to perform sign '${cleanTarget}'.`);

    // Clear canvas skeleton
    if (canvasRef.current) {
      const ctx = canvasRef.current.getContext('2d');
      ctx.clearRect(0, 0, canvasRef.current.width, canvasRef.current.height);
    }

    // Reset backend temporal stabilizer
    api.post('/recognition/reset-stabilizer', { target_sign: cleanTarget }).catch(() => {});
  };

  /**
   * Toggles Front ("user") vs Rear ("environment") Camera on mobile devices
   */
  const handleToggleCameraFacing = async () => {
    const nextMode = facingMode === 'user' ? 'environment' : 'user';
    facingModeRef.current = nextMode;
    setFacingMode(nextMode);
    if (isCameraActive) {
      stopCamera();
      setTimeout(() => {
        startCamera(nextMode);
      }, 200);
    }
  };

  /**
   * Draws 21-landmark hand skeleton overlay onto canvas
   */
  const drawHandSkeleton = (landmarks, isCorrect) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    if (!landmarks || landmarks.length !== 21) return;

    const connections = [
      [0,1],[1,2],[2,3],[3,4],
      [0,5],[5,6],[6,7],[7,8],
      [9,10],[10,11],[11,12],
      [13,14],[14,15],[15,16],
      [0,17],[17,18],[18,19],[19,20],
      [5,9],[9,13],[13,17]
    ];

    // Connection bone lines
    ctx.strokeStyle = isCorrect === true ? '#10B981' : (isCorrect === false ? '#F43F5E' : '#38BDF8');
    ctx.lineWidth = Math.max(2, Math.round(canvas.width / 200));

    connections.forEach(([i, j]) => {
      const p1 = landmarks[i];
      const p2 = landmarks[j];
      ctx.beginPath();
      ctx.moveTo(p1.x * canvas.width, p1.y * canvas.height);
      ctx.lineTo(p2.x * canvas.width, p2.y * canvas.height);
      ctx.stroke();
    });

    // Landmark joints
    const radius = Math.max(3.5, Math.round(canvas.width / 140));
    landmarks.forEach((pt, idx) => {
      ctx.fillStyle = idx === 0 ? '#F43F5E' : (idx % 4 === 0 ? '#38BDF8' : '#A855F7');
      ctx.beginPath();
      ctx.arc(pt.x * canvas.width, pt.y * canvas.height, radius, 0, 2 * Math.PI);
      ctx.fill();
    });
  };

  /**
   * Process extracted 21 spatial landmarks through trained Random Forest backend model
   */
  const processLandmarkInference = async (landmarks21) => {
    if (isInferringRef.current) return;
    const now = Date.now();
    // Controlled throttling: ~5-7 requests per second (150ms interval) to protect mobile cellular bandwidth
    if (now - lastInferenceTimeRef.current < 150) return;

    const currentGeneration = targetGenerationRef.current;
    const currentTarget = targetSignRef.current;

    lastInferenceTimeRef.current = now;
    isInferringRef.current = true;
    setNetworkInfo(prev => ({ ...prev, inFlight: true, mode: 'Landmarks JSON (500B)' }));

    const controller = new AbortController();
    abortControllerRef.current = controller;
    const startTime = performance.now();

    try {
      const res = await api.post('/recognition/predict-landmarks', {
        landmarks: landmarks21.map(pt => ({ x: pt.x, y: pt.y, z: pt.z })),
        target_sign: currentTarget,
        session_id: sessionId
      }, {
        signal: controller.signal,
        timeout: 1500 // Fast 1.5s timeout on mobile to prevent stalling
      });

      const rtt = Math.round(performance.now() - startTime);
      setRoundTripLatency(rtt);
      setNetworkInfo(prev => ({ ...prev, rttMs: rtt, inFlight: false }));

      // Discard stale in-flight response if target changed while awaiting response!
      if (currentGeneration !== targetGenerationRef.current || currentTarget !== targetSignRef.current) {
        return;
      }

      const data = res.data;
      const inferMs = data.inference_time_ms || 12.0;
      setInferenceLatency(inferMs);
      setHasValidHand(true);

      if (data.status === 'UNCERTAIN' || data.predicted_class === 'UNCERTAIN') {
        setDetectedSign('Uncertain');
        const confStr = (data.confidence * 100).toFixed(1);
        setDetectionConfidence(confStr);
        setIsSignCorrect(null);
        setWebcamState(WEBCAM_STATES.PROCESSING);
        setFeedbackMessage(data.message || "I couldn't confidently recognize the sign. Please position your hand clearly.");
        drawHandSkeleton(landmarks21, null);
      } else {
        const pred = data.predicted_sign || data.predicted_class;
        const conf = (data.confidence * 100).toFixed(1);
        const correct = data.correct !== undefined ? data.correct : (pred.toUpperCase() === currentTarget.toUpperCase());

        setDetectedSign(pred);
        setDetectionConfidence(conf);
        setIsSignCorrect(correct);
        setWebcamState(correct ? WEBCAM_STATES.STABLE_PREDICTION : WEBCAM_STATES.PREDICTION);
        setFeedbackMessage(data.message || (correct ? `Correct. The model detected ${pred}, which matches the expected ${currentTarget} sign.` : `Incorrect. The model detected ${pred}, while the expected sign was ${currentTarget}. Please try the ${currentTarget} sign again.`));

        drawHandSkeleton(landmarks21, correct);
      }
    } catch (err) {
      if (err.name !== 'CanceledError' && err.name !== 'AbortError') {
        console.error("Landmark prediction error:", err);
      }
    } finally {
      isInferringRef.current = false;
      setNetworkInfo(prev => ({ ...prev, inFlight: false }));
    }
  };

  /**
   * Fallback frame capture when client-side MediaPipe is unavailable or initializing
   */
  const captureAndPredictFrame = async () => {
    if (!videoRef.current || !isCameraActive || isInferringRef.current) return;
    const now = Date.now();
    if (now - lastInferenceTimeRef.current < 300) return;

    const video = videoRef.current;
    if (video.readyState < 2) return;

    const currentGeneration = targetGenerationRef.current;
    const currentTarget = targetSignRef.current;

    // Use compact 240x180 thumbnail to minimize mobile cellular bandwidth
    const tempCanvas = document.createElement('canvas');
    tempCanvas.width = 240;
    tempCanvas.height = 180;
    const ctx = tempCanvas.getContext('2d');
    ctx.drawImage(video, 0, 0, tempCanvas.width, tempCanvas.height);
    const base64 = tempCanvas.toDataURL('image/jpeg', 0.5);

    isInferringRef.current = true;
    lastInferenceTimeRef.current = now;
    setNetworkInfo(prev => ({ ...prev, inFlight: true, mode: 'Frame Base64 (25KB)' }));
    const startTime = performance.now();

    try {
      const res = await api.post('/recognition/predict-frame', {
        image_base64: base64,
        target_sign: currentTarget
      });

      const rtt = Math.round(performance.now() - startTime);
      setRoundTripLatency(rtt);
      setNetworkInfo(prev => ({ ...prev, rttMs: rtt, inFlight: false }));

      // Discard stale response if target changed in the interim
      if (currentGeneration !== targetGenerationRef.current || currentTarget !== targetSignRef.current) {
        return;
      }

      const data = res.data;
      setInferenceLatency(data.inference_time_ms || 15.0);

      if (!data.is_valid_hand || data.predicted_class === 'NONE') {
        setHasValidHand(false);
        setDetectedSign('None');
        setDetectionConfidence(0.0);
        setIsSignCorrect(null);
        setWebcamState(WEBCAM_STATES.NO_HAND_DETECTED);
        setFeedbackMessage("No hand detected. Position your hand clearly within the camera frame.");
        if (canvasRef.current) {
          const c = canvasRef.current.getContext('2d');
          c.clearRect(0, 0, canvasRef.current.width, canvasRef.current.height);
        }
        return;
      }

      setHasValidHand(true);

      if (data.status === 'UNCERTAIN' || data.predicted_class === 'UNCERTAIN') {
        setDetectedSign('Uncertain');
        setDetectionConfidence((data.confidence * 100).toFixed(1));
        setIsSignCorrect(null);
        setWebcamState(WEBCAM_STATES.PROCESSING);
        setFeedbackMessage(data.message || "I couldn't confidently recognize the sign. Please stabilize your hand posture.");
      } else {
        const pred = data.predicted_sign || data.predicted_class;
        const conf = (data.confidence * 100).toFixed(1);
        const correct = data.correct !== undefined ? data.correct : (pred.toUpperCase() === currentTarget.toUpperCase());

        setDetectedSign(pred);
        setDetectionConfidence(conf);
        setIsSignCorrect(correct);
        setWebcamState(correct ? WEBCAM_STATES.STABLE_PREDICTION : WEBCAM_STATES.PREDICTION);
        setFeedbackMessage(data.message || (correct ? `Correct. The model detected ${pred}, which matches the expected ${currentTarget} sign.` : `Incorrect. The model detected ${pred}, while the expected sign was ${currentTarget}. Please try the ${currentTarget} sign again.`));
      }
    } catch (err) {
      console.error("Frame prediction error:", err);
    } finally {
      isInferringRef.current = false;
      setNetworkInfo(prev => ({ ...prev, inFlight: false }));
    }
  };

  /**
   * Start real-time webcam and initialize smooth MediaPipe tracking loop
   */
  const startCamera = async (explicitFacing = null) => {
    const activeFacing = explicitFacing || facingMode;
    setWebcamState(WEBCAM_STATES.PERMISSION_REQUESTED);

    // Mobile-compatible flexible constraints
    const constraints = {
      video: {
        facingMode: activeFacing,
        width: { ideal: 640, max: 1280 },
        height: { ideal: 480, max: 720 },
        frameRate: { ideal: 30, max: 30 }
      },
      audio: false
    };

    try {
      const stream = await navigator.mediaDevices.getUserMedia(constraints);

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.setAttribute('playsinline', 'true');
        videoRef.current.setAttribute('webkit-playsinline', 'true');
        videoRef.current.muted = true;
        videoRef.current.autoplay = true;

        await videoRef.current.play();
        setIsCameraActive(true);
        setWebcamState(WEBCAM_STATES.VALID_INPUT);

        // Update telemetry
        setCameraInfo({
          resolution: `${videoRef.current.videoWidth || 640}x${videoRef.current.videoHeight || 480}`,
          fps: 30,
          facingMode: activeFacing,
          orientation: window.innerHeight > window.innerWidth ? 'portrait' : 'landscape',
          readyState: 'HAVE_ENOUGH_DATA'
        });

        syncCanvasDimensions();

        // Check if MediaPipe is available in browser window
        if (window.Hands) {
          setMediaPipeInfo(prev => ({ ...prev, status: 'Initializing WASM Graph' }));
          
          const hands = new window.Hands({
            locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`
          });

          hands.setOptions({
            maxNumHands: 1,
            modelComplexity: 1,
            minDetectionConfidence: 0.5,
            minTrackingConfidence: 0.5
          });

          hands.onResults((results) => {
            // Measure MediaPipe FPS
            mpFramesCountRef.current += 1;
            const now = performance.now();
            if (now - lastMpFpsTimeRef.current >= 1000) {
              const currentMpFps = Math.round((mpFramesCountRef.current * 1000) / (now - lastMpFpsTimeRef.current));
              setMediaPipeInfo(prev => ({ ...prev, fps: currentMpFps }));
              mpFramesCountRef.current = 0;
              lastMpFpsTimeRef.current = now;
            }

            if (results.multiHandLandmarks && results.multiHandLandmarks.length > 0) {
              const rawLms = results.multiHandLandmarks[0];
              setMediaPipeInfo(prev => ({
                ...prev,
                status: 'Active (Tracking)',
                hasHand: true,
                landmarkCount: rawLms.length
              }));
              processLandmarkInference(rawLms);
            } else {
              setHasValidHand(false);
              setDetectedSign('None');
              setDetectionConfidence(0.0);
              setIsSignCorrect(null);
              setWebcamState(WEBCAM_STATES.NO_HAND_DETECTED);
              setMediaPipeInfo(prev => ({
                ...prev,
                status: 'Active (Searching)',
                hasHand: false,
                landmarkCount: 0
              }));
              setFeedbackMessage("No hand detected. Position your hand clearly within the camera frame.");
              if (canvasRef.current) {
                const c = canvasRef.current.getContext('2d');
                c.clearRect(0, 0, canvasRef.current.width, canvasRef.current.height);
              }
            }
          });

          handsInstanceRef.current = hands;
          isTrackingRunningRef.current = true;

          // Controlled requestAnimationFrame loop (~15-20 FPS) to prevent mobile CPU thermal throttling
          let lastProcessTime = 0;
          const TARGET_INTERVAL_MS = 60; // ~16 FPS tracking cadence

          const runTrackingLoop = async () => {
            if (!isTrackingRunningRef.current) return;
            const currentTime = performance.now();

            if (
              currentTime - lastProcessTime >= TARGET_INTERVAL_MS &&
              videoRef.current &&
              videoRef.current.readyState >= 2 &&
              !isHandsBusyRef.current
            ) {
              lastProcessTime = currentTime;
              isHandsBusyRef.current = true;
              try {
                await hands.send({ image: videoRef.current });
              } catch (err) {
                console.warn("MediaPipe frame send warning:", err);
              } finally {
                isHandsBusyRef.current = false;
              }
            }

            animFrameIdRef.current = requestAnimationFrame(runTrackingLoop);
          };

          animFrameIdRef.current = requestAnimationFrame(runTrackingLoop);
        } else {
          // Continuous lightweight frame capture fallback if MediaPipe CDN was unavailable
          setMediaPipeInfo(prev => ({ ...prev, status: 'Fallback Frame Pipeline' }));
          frameIntervalRef.current = setInterval(captureAndPredictFrame, 300);
        }
      }
    } catch (err) {
      console.error("Camera start error:", err);
      setWebcamState(WEBCAM_STATES.CAMERA_DENIED);
      setFeedbackMessage("Camera access denied or unavailable. Please enable webcam permissions.");
    }
  };

  /**
   * Stop webcam and cleanly release hardware resources
   */
  const stopCamera = () => {
    isTrackingRunningRef.current = false;

    if (animFrameIdRef.current) {
      cancelAnimationFrame(animFrameIdRef.current);
      animFrameIdRef.current = null;
    }

    if (handsInstanceRef.current) {
      try { handsInstanceRef.current.close(); } catch (e) {}
      handsInstanceRef.current = null;
    }

    if (frameIntervalRef.current) {
      clearInterval(frameIntervalRef.current);
      frameIntervalRef.current = null;
    }

    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }

    if (videoRef.current && videoRef.current.srcObject) {
      const stream = videoRef.current.srcObject;
      stream.getTracks().forEach(track => track.stop());
      videoRef.current.srcObject = null;
    }

    if (canvasRef.current) {
      const c = canvasRef.current.getContext('2d');
      c.clearRect(0, 0, canvasRef.current.width, canvasRef.current.height);
    }

    setIsCameraActive(false);
    setHasValidHand(false);
    setDetectedSign(null);
    setIsSignCorrect(null);
    setWebcamState(WEBCAM_STATES.NO_HAND_DETECTED);
    setMediaPipeInfo({
      status: 'Standby',
      hasHand: false,
      landmarkCount: 0,
      fps: 0
    });
  };

  /**
   * Record an official attempt to persistent database
   */
  const recordCurrentAttempt = async () => {
    if (!detectedSign || detectedSign === 'None' || detectedSign === 'Uncertain') {
      alert("Please perform a clear sign in front of the camera before recording an attempt.");
      return;
    }

    const currentTarget = targetSignRef.current;
    const predSign = detectedSign;
    const confVal = detectionConfidence ? parseFloat(detectionConfidence) / 100.0 : 0.0;
    const isCorr = isSignCorrect === true || (predSign.toUpperCase() === currentTarget.toUpperCase());
    const accVal = isCorr ? 100.0 : 0.0;
    const feedbackStr = isCorr 
      ? `Correct. The model detected ${predSign}, which matches the expected ${currentTarget} sign.` 
      : `Incorrect. The model detected ${predSign}, while the expected sign was ${currentTarget}. Please try the ${currentTarget} sign again.`;

    const newAttempts = attemptCount + 1;
    const newCorrect = isCorr ? correctAttempts + 1 : correctAttempts;
    setAttemptCount(newAttempts);
    if (isCorr) setCorrectAttempts(newCorrect);

    const sessionAcc = ((newCorrect / newAttempts) * 100).toFixed(1);
    setSessionAccuracy(sessionAcc);

    try {
      await api.post('/practice/attempt', {
        expected_sign: currentTarget,
        predicted_sign: predSign,
        confidence: confVal,
        is_correct: isCorr,
        gesture_accuracy: accVal,
        feedback: feedbackStr
      }, {
        params: sessionId ? { session_id: sessionId } : {}
      });
      fetchMastery();
    } catch (err) {
      console.error("Failed to record attempt:", err);
    }
  };

  const formatTime = (secs) => {
    const m = Math.floor(secs / 60);
    const s = secs % 60;
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 py-6 space-y-6 bg-slate-950 text-slate-100 min-h-screen">
      
      {/* Header & Target Sign Picker */}
      <div className="glass-card p-4 sm:p-5 rounded-2xl border border-slate-800/80 bg-slate-900/60 shadow-xl flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex flex-wrap items-center gap-2 mb-2.5">
            <button
              onClick={() => navigate(-1)}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-750 text-slate-200 hover:text-white text-xs font-bold transition-all border border-slate-700 cursor-pointer shadow-sm"
              title="Return to previous page"
            >
              <ArrowLeft className="w-4 h-4" /> Back
            </button>
            <Link
              to="/practice"
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-400 hover:text-slate-200 text-xs font-bold transition-all border border-slate-800"
              title="Practice Modes selection"
            >
              Practice Modes
            </Link>
            <Link
              to="/achievements"
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-amber-500/10 hover:bg-amber-500/20 text-amber-400 hover:text-amber-300 text-xs font-bold transition-all border border-amber-500/30"
              title="View ASL Sign Achievements"
            >
              <Trophy className="w-3.5 h-3.5" /> Achievements
            </Link>
          </div>
          <h1 className="text-xl font-extrabold text-white flex items-center gap-2">
            <Camera className="w-5 h-5 text-sky-400" /> Real-Time AI Gesture Recognition & Practice
            <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-sky-500/10 text-sky-400 border border-sky-500/30 ml-1">
              Beginner Mode
            </span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Target Sign: <span className="text-sky-400 font-bold text-sm">'{selectedSign}'</span> — Perform the gesture in front of your camera.
          </p>
        </div>

        {/* Target Sign Quick Selector */}
        <div className="flex items-center gap-1.5 overflow-x-auto max-w-full md:max-w-2xl py-1">
          <span className="text-xs font-bold text-slate-400 mr-1 flex items-center gap-1 shrink-0">
            <Target className="w-3.5 h-3.5 text-sky-400" /> Target Sign:
          </span>
          {alphabet.map((char) => (
            <button
              key={char}
              onClick={() => handleTargetChange(char)}
              className={`px-2.5 py-1 rounded-lg text-xs font-bold transition-all border shrink-0 ${
                selectedSign === char
                  ? 'bg-sky-500 text-slate-950 border-sky-400 font-extrabold shadow-md shadow-sky-500/20'
                  : 'bg-slate-800 text-slate-300 border-slate-700 hover:border-slate-500'
              }`}
            >
              {char}
            </button>
          ))}
        </div>
      </div>

      {/* 3-Column Main Recognition Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* LEFT COLUMN: Target Reference & Instructions */}
        <div className="lg:col-span-3 glass-card p-5 rounded-2xl border border-slate-800/80 bg-slate-900/60 shadow-xl space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-sky-400">Target Sign</span>
            <span className="text-[10px] font-semibold bg-sky-500/10 text-sky-400 border border-sky-500/30 px-2 py-0.5 rounded-full">
              ASL Alphabet
            </span>
          </div>

          <div className="flex items-center gap-4 p-4 rounded-xl bg-slate-950 border border-slate-800">
            <div className="w-16 h-16 rounded-xl bg-gradient-to-br from-sky-500 to-indigo-600 flex items-center justify-center text-3xl font-black text-white shadow-lg">
              {selectedSign}
            </div>
            <div>
              <h3 className="text-lg font-bold text-white">Target: Letter '{selectedSign}'</h3>
              <p className="text-xs text-slate-400">Perform this sign to camera</p>
            </div>
          </div>

          <div className="space-y-2 text-xs">
            <h4 className="font-bold text-slate-300 flex items-center gap-1.5">
              <Info className="w-3.5 h-3.5 text-sky-400" /> Instructions
            </h4>
            <ul className="list-disc list-inside text-slate-400 space-y-1.5 leading-relaxed">
              <li>Click <strong>Start Camera</strong>.</li>
              <li>Position your hand clearly inside the frame.</li>
              <li>Good lighting enhances landmark resolution.</li>
              <li>Switch target letters anytime without refreshing!</li>
            </ul>
          </div>

          <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 space-y-1 text-xs">
            <div className="flex justify-between text-slate-400">
              <span>Model Version:</span>
              <span className="text-slate-200 font-mono">asl_rf_v001</span>
            </div>
            <div className="flex justify-between text-slate-400">
              <span>Inference Latency:</span>
              <span className="text-emerald-400 font-mono">{inferenceLatency} ms</span>
            </div>
            <div className="flex justify-between text-slate-400">
              <span>Round-Trip (RTT):</span>
              <span className="text-sky-400 font-mono">{roundTripLatency} ms</span>
            </div>
            <div className="flex justify-between text-slate-400">
              <span>Confidence Threshold:</span>
              <span className="text-slate-200 font-mono">70.0%</span>
            </div>
          </div>
        </div>

        {/* CENTER COLUMN: Live Webcam Stream & Responsive Skeleton Overlay */}
        <div className="lg:col-span-6 space-y-4">
          <div className="glass-card p-4 rounded-2xl border border-slate-800/80 bg-slate-900/60 shadow-xl flex flex-col items-center relative">
            
            {/* 15-State Webcam Status Indicator */}
            <div className="w-full mb-3">
              <WebcamStateIndicator state={webcamState} />
            </div>

            {/* Video + Canvas Frame with Responsive Aspect Container */}
            <div className="relative w-full max-w-full rounded-xl bg-slate-950 border border-slate-800 overflow-hidden flex items-center justify-center min-h-[300px] sm:min-h-[400px]">
              <video
                ref={videoRef}
                playsInline
                webkit-playsinline="true"
                muted
                autoPlay
                onLoadedMetadata={syncCanvasDimensions}
                className={`w-full h-auto max-h-[60vh] object-contain ${facingMode === 'user' ? 'transform -scale-x-100' : ''} ${isCameraActive ? 'block' : 'hidden'}`}
              />
              <canvas
                ref={canvasRef}
                className={`absolute inset-0 w-full h-full pointer-events-none z-10 ${facingMode === 'user' ? 'transform -scale-x-100' : ''}`}
              />
              {!isCameraActive && (
                <div className="flex flex-col items-center justify-center p-8 text-center">
                  <Camera className="w-14 h-14 text-slate-600 mb-3" />
                  <p className="text-slate-200 font-bold text-sm">Camera Standby</p>
                  <p className="text-slate-500 text-xs mt-1 max-w-sm">
                    Click "Start Camera" to enable MediaPipe 21-landmark tracking and real-time gesture recognition.
                  </p>
                </div>
              )}
            </div>

            {/* Live Camera Controls */}
            <div className="flex flex-wrap items-center gap-3 mt-4 w-full justify-center">
              {!isCameraActive ? (
                <button
                  onClick={() => startCamera()}
                  className="bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold px-6 py-2.5 rounded-xl text-xs flex items-center gap-2 shadow-lg shadow-emerald-500/20 transition-all cursor-pointer"
                >
                  <Play className="w-4 h-4 fill-current" /> Start Camera
                </button>
              ) : (
                <>
                  <button
                    onClick={stopCamera}
                    className="bg-rose-500/20 text-rose-400 hover:bg-rose-500/30 border border-rose-500/30 font-bold px-4 sm:px-5 py-2.5 rounded-xl text-xs flex items-center gap-2 transition-all cursor-pointer"
                  >
                    <Square className="w-3.5 h-3.5 fill-current" /> Stop Camera
                  </button>

                  <button
                    onClick={handleToggleCameraFacing}
                    className="bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 font-bold px-3.5 py-2.5 rounded-xl text-xs flex items-center gap-2 transition-all cursor-pointer"
                    title={`Switch to ${facingMode === 'user' ? 'Rear' : 'Front'} Camera`}
                  >
                    <SwitchCamera className="w-4 h-4 text-sky-400" />
                    <span className="hidden sm:inline">Flip Camera</span>
                  </button>

                  <button
                    onClick={recordCurrentAttempt}
                    disabled={!hasValidHand}
                    className="bg-sky-500 hover:bg-sky-400 text-slate-950 font-bold px-4 sm:px-5 py-2.5 rounded-xl text-xs flex items-center gap-2 shadow-lg shadow-sky-500/20 disabled:opacity-50 transition-all cursor-pointer"
                  >
                    <ShieldCheck className="w-4 h-4" /> Record Attempt
                  </button>
                </>
              )}
            </div>
          </div>
        </div>

        {/* RIGHT COLUMN: Real-Time Model Classification Output & Comparison */}
        <div className="lg:col-span-3 glass-card p-5 rounded-2xl border border-slate-800/80 bg-slate-900/60 shadow-xl space-y-4">
          <span className="text-xs font-bold uppercase tracking-wider text-sky-400 block mb-2">
            Automated Model Detection
          </span>

          {/* Model Detected Sign Card */}
          <div className={`p-4 rounded-xl border text-center space-y-2 transition-all ${
            detectedSign && isSignCorrect === true
              ? 'bg-emerald-950/40 border-emerald-500/40'
              : (detectedSign && isSignCorrect === false
                ? 'bg-rose-950/40 border-rose-500/40'
                : 'bg-slate-950 border-slate-800')
          }`}>
            <span className="text-[10px] text-slate-400 uppercase font-semibold block">
              AI Detected Sign
            </span>
            
            <div className={`text-5xl font-black ${
              isSignCorrect === true
                ? 'text-emerald-400'
                : (isSignCorrect === false
                  ? 'text-rose-400'
                  : 'text-slate-400')
            }`}>
              {detectedSign || (isCameraActive ? 'Waiting...' : '—')}
            </div>

            {detectedSign && (
              <div className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold ${
                isSignCorrect === true
                  ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                  : (isSignCorrect === false
                    ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                    : 'bg-amber-500/20 text-amber-400 border border-amber-500/30')
              }`}>
                {isSignCorrect === true && <CheckCircle2 className="w-3.5 h-3.5" />}
                {isSignCorrect === false && <XCircle className="w-3.5 h-3.5" />}
                {isSignCorrect === null && <AlertTriangle className="w-3.5 h-3.5" />}
                {isSignCorrect === true
                  ? 'CORRECT GESTURE'
                  : (isSignCorrect === false
                    ? `INCORRECT (Expected '${selectedSign}')`
                    : 'UNCERTAIN')}
              </div>
            )}

            <div className="text-[11px] text-slate-400 font-semibold block mt-1">
              Model Confidence: {detectionConfidence !== null ? `${detectionConfidence}%` : '—'}
            </div>
          </div>

          {/* Session Statistics */}
          <div className="grid grid-cols-2 gap-3 text-xs">
            <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 text-center">
              <span className="text-[10px] text-slate-400 block font-semibold">Attempts</span>
              <span className="text-base font-bold text-white mt-1 block">#{attemptCount}</span>
            </div>

            <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 text-center">
              <span className="text-[10px] text-slate-400 block font-semibold">Session Time</span>
              <span className="text-base font-bold text-sky-400 mt-1 block flex items-center justify-center gap-1">
                <Clock className="w-3 h-3" /> {formatTime(sessionTime)}
              </span>
            </div>
          </div>

          <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 text-center">
            <span className="text-[10px] text-slate-400 block font-semibold">Session Accuracy (Success Rate)</span>
            <span className={`text-xl font-black mt-0.5 block ${
              parseFloat(sessionAccuracy) >= 75 ? 'text-emerald-400' : 'text-amber-400'
            }`}>
              {attemptCount > 0 ? `${sessionAccuracy}%` : '—'}
            </span>
            <span className="text-[10px] text-slate-500 mt-0.5 block">
              {correctAttempts} correct / {attemptCount} completed
            </span>
          </div>
        </div>

      </div>

      {/* BOTTOM BAR: Real-Time Anatomical Feedback & Next Target */}
      <div className={`glass-card p-5 rounded-2xl border shadow-xl flex flex-col md:flex-row items-center justify-between gap-6 transition-all ${
        isSignCorrect === false
          ? 'bg-rose-950/20 border-rose-500/40'
          : (isSignCorrect === true
            ? 'bg-emerald-950/20 border-emerald-500/40'
            : 'bg-slate-900/60 border-slate-800/80')
      }`}>
        <div className="flex items-start gap-4">
          <div className={`p-3 rounded-xl border ${
            isSignCorrect === false
              ? 'bg-rose-500/20 text-rose-400 border-rose-500/30'
              : (isSignCorrect === true
                ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30'
                : 'bg-sky-500/20 text-sky-400 border-sky-500/30')
          }`}>
            <Sparkles className="w-6 h-6" />
          </div>
          <div>
            <h4 className="text-sm font-bold text-white">
              {isSignCorrect === true
                ? 'Sign Performed Accurately'
                : (isSignCorrect === false ? 'Sign Adjustment Guidance' : 'Ready for Hand Gesture')}
            </h4>
            <p className="text-xs text-slate-300 mt-0.5 max-w-2xl leading-relaxed">
              {feedbackMessage}
            </p>
          </div>
        </div>

        {recommendation && (
          <div className="flex items-center gap-3 bg-slate-950/80 p-3 rounded-xl border border-slate-800 shrink-0">
            <div>
              <span className="text-[10px] font-bold text-slate-400 block uppercase">Adaptive Path</span>
              <span className="text-xs font-bold text-sky-400">
                Next: Sign '{recommendation.recommended_sign}'
              </span>
            </div>
            <button
              onClick={() => handleTargetChange(recommendation.recommended_sign)}
              className="bg-indigo-600 hover:bg-indigo-500 text-white font-bold p-2 rounded-lg text-xs transition-all cursor-pointer"
              title={`Switch target to recommended sign ${recommendation.recommended_sign}`}
            >
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        )}
      </div>

      {/* Developer Diagnostics Overlay HUD */}
      <DeveloperDiagnosticsOverlay
        cameraInfo={cameraInfo}
        mediaPipeInfo={mediaPipeInfo}
        inferenceInfo={{
          model: 'asl_rf_v001',
          targetSign: selectedSign,
          predictedSign: detectedSign,
          confidence: detectionConfidence,
          isCorrect: isSignCorrect,
          latencyMs: inferenceLatency
        }}
        networkInfo={networkInfo}
      />

    </div>
  );
};
