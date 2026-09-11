import React, { useState, useEffect, useRef } from 'react';
import { Link, useSearchParams, useNavigate, useLocation } from 'react-router-dom';
import api from '../../api/client';
import { WebcamStateIndicator, WEBCAM_STATES } from '../../components/practice/WebcamStateIndicator';
import { Camera, CheckCircle2, AlertTriangle, Sparkles, Clock, Target, ArrowRight, ArrowLeft, Play, Square, Info, XCircle, ShieldCheck, Trophy } from 'lucide-react';

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
  const [webcamState, setWebcamState] = useState(WEBCAM_STATES.NO_HAND_DETECTED);
  
  // Real-Time ML Model Outputs (Derived solely from MediaPipe + Trained RF Model)
  const [detectedSign, setDetectedSign] = useState(null);
  const [detectionConfidence, setDetectionConfidence] = useState(null);
  const [isSignCorrect, setIsSignCorrect] = useState(null);
  const [inferenceLatency, setInferenceLatency] = useState(0.0);
  const [feedbackMessage, setFeedbackMessage] = useState(`Position your hand in front of the camera to begin practicing sign '${initialTarget}'.`);
  const [hasValidHand, setHasValidHand] = useState(false);

  // Session Statistics
  const [attemptCount, setAttemptCount] = useState(0);
  const [correctAttempts, setCorrectAttempts] = useState(0);
  const [sessionAccuracy, setSessionAccuracy] = useState('0.0');
  const [sessionTime, setSessionTime] = useState(0);
  const [sessionId, setSessionId] = useState(null);
  const [recommendation, setRecommendation] = useState(null);
  const [masteryData, setMasteryData] = useState([]);

  // Refs for State Synchronization & Stale Closure Prevention
  const targetSignRef = useRef(initialTarget);
  const targetGenerationRef = useRef(1); // Incremented on each target change to discard in-flight race condition responses
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const cameraInstanceRef = useRef(null);
  const handsInstanceRef = useRef(null);
  const timerRef = useRef(null);
  const lastInferenceTimeRef = useRef(0);
  const isInferringRef = useRef(false);
  const frameIntervalRef = useRef(null);

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
        // Only set target from recommendation if NO explicit target was supplied in the URL
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
   * Authoritative Target Change Handler:
   * 1. Updates targetSignRef immediately (single source of truth).
   * 2. Increments targetGenerationRef to invalidate any pending in-flight async inferences.
   * 3. Clears all transient prediction states (detectedSign, isSignCorrect, skeleton canvas).
   * 4. Resets backend temporal stabilizer history without dropping webcam stream or model.
   */
  const handleTargetChange = (newTarget) => {
    if (!newTarget) return;
    const cleanTarget = newTarget.trim().toUpperCase();

    // Invalidate in-flight inference generation
    targetGenerationRef.current += 1;
    targetSignRef.current = cleanTarget;
    setSelectedSign(cleanTarget);

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

  // Draw 21-landmark hand skeleton overlay onto canvas
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
    ctx.lineWidth = 3;

    connections.forEach(([i, j]) => {
      const p1 = landmarks[i];
      const p2 = landmarks[j];
      ctx.beginPath();
      ctx.moveTo(p1.x * canvas.width, p1.y * canvas.height);
      ctx.lineTo(p2.x * canvas.width, p2.y * canvas.height);
      ctx.stroke();
    });

    // Landmark joints
    landmarks.forEach((pt, idx) => {
      ctx.fillStyle = idx === 0 ? '#F43F5E' : (idx % 4 === 0 ? '#38BDF8' : '#A855F7');
      ctx.beginPath();
      ctx.arc(pt.x * canvas.width, pt.y * canvas.height, 4.5, 0, 2 * Math.PI);
      ctx.fill();
    });
  };

  // Process extracted 21 spatial landmarks through trained Random Forest backend model
  const processLandmarkInference = async (landmarks21) => {
    if (isInferringRef.current) return;
    const now = Date.now();
    // Throttle inference requests to ~4-5 Hz for optimal temporal stabilization
    if (now - lastInferenceTimeRef.current < 200) return;

    const currentGeneration = targetGenerationRef.current;
    const currentTarget = targetSignRef.current;

    lastInferenceTimeRef.current = now;
    isInferringRef.current = true;

    try {
      const res = await api.post('/recognition/predict-landmarks', {
        landmarks: landmarks21.map(pt => ({ x: pt.x, y: pt.y, z: pt.z })),
        target_sign: currentTarget,
        session_id: sessionId
      });

      // Discard stale in-flight response if target changed while awaiting response!
      if (currentGeneration !== targetGenerationRef.current || currentTarget !== targetSignRef.current) {
        return;
      }

      const data = res.data;
      setInferenceLatency(data.inference_time_ms || 12.0);
      setHasValidHand(true);

      if (data.status === 'UNCERTAIN' || data.predicted_class === 'UNCERTAIN') {
        setDetectedSign('Uncertain');
        setDetectionConfidence((data.confidence * 100).toFixed(1));
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
      console.error("Landmark prediction error:", err);
    } finally {
      isInferringRef.current = false;
    }
  };

  // Fallback frame capture when client-side MediaPipe is unavailable
  const captureAndPredictFrame = async () => {
    if (!videoRef.current || !isCameraActive || isInferringRef.current) return;
    const now = Date.now();
    if (now - lastInferenceTimeRef.current < 250) return;

    const video = videoRef.current;
    if (video.readyState < 2) return;

    const currentGeneration = targetGenerationRef.current;
    const currentTarget = targetSignRef.current;

    const tempCanvas = document.createElement('canvas');
    tempCanvas.width = 320;
    tempCanvas.height = 240;
    const ctx = tempCanvas.getContext('2d');
    ctx.drawImage(video, 0, 0, tempCanvas.width, tempCanvas.height);
    const base64 = tempCanvas.toDataURL('image/jpeg', 0.6);

    isInferringRef.current = true;
    lastInferenceTimeRef.current = now;

    try {
      const res = await api.post('/recognition/predict-frame', {
        image_base64: base64,
        target_sign: currentTarget
      });

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
    }
  };

  // Start real-time webcam and initialize MediaPipe tracking
  const startCamera = async () => {
    setWebcamState(WEBCAM_STATES.PERMISSION_REQUESTED);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 640, height: 480, facingMode: 'user' }
      });

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
        setIsCameraActive(true);
        setWebcamState(WEBCAM_STATES.VALID_INPUT);

        // Check if MediaPipe is available in browser window
        if (window.Hands && window.Camera) {
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
            if (results.multiHandLandmarks && results.multiHandLandmarks.length > 0) {
              const rawLms = results.multiHandLandmarks[0];
              processLandmarkInference(rawLms);
            } else {
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
            }
          });

          const camera = new window.Camera(videoRef.current, {
            onFrame: async () => {
              if (videoRef.current && videoRef.current.readyState >= 2) {
                await hands.send({ image: videoRef.current });
              }
            },
            width: 640,
            height: 480
          });

          camera.start();
          handsInstanceRef.current = hands;
          cameraInstanceRef.current = camera;
        } else {
          // Continuous backend frame capture fallback if MediaPipe CDN was delayed
          frameIntervalRef.current = setInterval(captureAndPredictFrame, 250);
        }
      }
    } catch (err) {
      console.error("Camera start error:", err);
      setWebcamState(WEBCAM_STATES.CAMERA_DENIED);
      setFeedbackMessage("Camera access denied or unavailable. Please enable webcam permissions.");
    }
  };

  // Stop webcam and release hardware stream
  const stopCamera = () => {
    if (cameraInstanceRef.current) {
      try { cameraInstanceRef.current.stop(); } catch (e) {}
      cameraInstanceRef.current = null;
    }
    if (handsInstanceRef.current) {
      try { handsInstanceRef.current.close(); } catch (e) {}
      handsInstanceRef.current = null;
    }
    if (frameIntervalRef.current) {
      clearInterval(frameIntervalRef.current);
      frameIntervalRef.current = null;
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
  };

  // Record an official attempt to persistent database
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
    <div className="max-w-7xl mx-auto px-6 py-6 space-y-6 bg-slate-950 text-slate-100 min-h-screen">
      
      {/* Header & Target Sign Picker */}
      <div className="glass-card p-5 rounded-2xl border border-slate-800/80 bg-slate-900/60 shadow-xl flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
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
            Target Sign: <span className="text-sky-400 font-bold text-sm">'{selectedSign}'</span> — Perform the gesture in front of your webcam.
          </p>
        </div>

        {/* Target Sign Quick Selector (Learner selects ONLY target sign from all 26 classes A-Z) */}
        <div className="flex items-center gap-1.5 overflow-x-auto max-w-2xl py-1">
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
              <li>Show your hand clearly within the camera box.</li>
              <li>The AI model will <strong>automatically detect</strong> which sign you are performing in real-time.</li>
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
              <span>Confidence Threshold:</span>
              <span className="text-slate-200 font-mono">70.0%</span>
            </div>
          </div>
        </div>

        {/* CENTER COLUMN: Live Webcam Stream & Skeleton Overlay */}
        <div className="lg:col-span-6 space-y-4">
          <div className="glass-card p-4 rounded-2xl border border-slate-800/80 bg-slate-900/60 shadow-xl flex flex-col items-center relative">
            
            {/* 15-State Webcam Status Indicator */}
            <div className="w-full mb-3">
              <WebcamStateIndicator state={webcamState} />
            </div>

            {/* Video + Canvas Frame */}
            <div className="relative w-full aspect-video rounded-xl bg-slate-950 border border-slate-800 overflow-hidden flex items-center justify-center">
              <video
                ref={videoRef}
                playsInline
                muted
                className={`w-full h-full object-cover transform -scale-x-100 ${isCameraActive ? 'block' : 'hidden'}`}
              />
              <canvas
                ref={canvasRef}
                width={640}
                height={480}
                className="absolute inset-0 w-full h-full pointer-events-none z-10 transform -scale-x-100"
              />
              {!isCameraActive && (
                <div className="flex flex-col items-center justify-center p-8 text-center">
                  <Camera className="w-14 h-14 text-slate-600 mb-3" />
                  <p className="text-slate-200 font-bold text-sm">Webcam Standby</p>
                  <p className="text-slate-500 text-xs mt-1 max-w-sm">
                    Click "Start Camera" to enable MediaPipe 21-landmark tracking and real-time gesture recognition.
                  </p>
                </div>
              )}
            </div>

            {/* Live Camera Controls */}
            <div className="flex items-center gap-3 mt-4 w-full justify-center">
              {!isCameraActive ? (
                <button
                  onClick={startCamera}
                  className="bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold px-6 py-2.5 rounded-xl text-xs flex items-center gap-2 shadow-lg shadow-emerald-500/20 transition-all"
                >
                  <Play className="w-4 h-4 fill-current" /> Start Camera
                </button>
              ) : (
                <>
                  <button
                    onClick={stopCamera}
                    className="bg-rose-500/20 text-rose-400 hover:bg-rose-500/30 border border-rose-500/30 font-bold px-5 py-2.5 rounded-xl text-xs flex items-center gap-2 transition-all"
                  >
                    <Square className="w-3.5 h-3.5 fill-current" /> Stop Camera
                  </button>

                  <button
                    onClick={recordCurrentAttempt}
                    disabled={!hasValidHand}
                    className="bg-sky-500 hover:bg-sky-400 text-slate-950 font-bold px-5 py-2.5 rounded-xl text-xs flex items-center gap-2 shadow-lg shadow-sky-500/20 disabled:opacity-50 transition-all"
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
            {isSignCorrect === false && <AlertTriangle className="w-6 h-6 animate-bounce" />}
            {isSignCorrect === true && <CheckCircle2 className="w-6 h-6 animate-pulse" />}
            {isSignCorrect === null && <Sparkles className="w-6 h-6" />}
          </div>
          <div>
            <span className={`text-xs font-bold uppercase tracking-wider ${
              isSignCorrect === false ? 'text-rose-400' : (isSignCorrect === true ? 'text-emerald-400' : 'text-sky-400')
            }`}>
              {isSignCorrect === false ? '⚠️ Sign Mismatch' : (isSignCorrect === true ? '✅ Gesture Verified' : 'AI Real-Time Feedback')}
            </span>
            <p className="text-sm font-semibold text-white mt-1">
              {feedbackMessage}
            </p>
            <p className="text-xs text-slate-400 mt-0.5">
              Next Recommended Target: Letter '{recommendation ? recommendation.recommended_sign : 'B'}'
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => {
              const nextChar = String.fromCharCode(selectedSign.charCodeAt(0) + 1);
              if (nextChar <= 'Z') {
                handleTargetChange(nextChar);
              }
            }}
            className="bg-slate-800 hover:bg-slate-700 text-slate-200 font-bold px-4 py-2.5 rounded-xl text-xs border border-slate-700 flex items-center gap-1.5 transition-all"
          >
            Next Sign <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </div>
  );
};
