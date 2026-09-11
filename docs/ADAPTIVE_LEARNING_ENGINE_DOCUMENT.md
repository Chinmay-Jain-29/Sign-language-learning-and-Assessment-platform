# Adaptive Learning Engine Documentation: Intelligent Platform Core

This document details the expected objectives, actual implementation, architecture diagram, and test plan for the **Adaptive Learning & Intelligent Platform Engine**.

---

## 1. Expected To Do (Requirements & Objectives)
- Eliminate hardcoded stats, fake AI predictions, and static recommendations.
- Build a data-driven 5-State Machine (`Not Attempted`, `Learning`, `Improving`, `Mastered`, `Needs Revision`) evaluating learner progress across signs.
- Log every state transition into `learner_state_history` for longitudinal tracking.
- Build an Adaptive Recommendation Engine generating explicit reasons (e.g., *"3 consecutive mistakes on sign 'D'"*, *"Mastered 3 signs - try unattempted letter 'E'"*).
- Execute a unified closed-loop workflow:
  $$\text{Assessment} \rightarrow \text{Analytics} \rightarrow \text{Learner Profile} \rightarrow \text{Learner State} \rightarrow \text{Feedback} \rightarrow \text{Recommendation} \rightarrow \text{Dashboard}$$
- Deliver real-time dashboard state updates without requiring page refreshes.

---

## 2. Implementation Details

### Service Layer Files
- [`backend/app/services/learner_state_service.py`](file:///d:/SIGN%20LANGUAGE%20LEARNING%20AND%20ASSESSNMENT/backend/app/services/learner_state_service.py): Evaluates state transitions based on consecutive attempts, accuracy metrics, and logs history in `learner_state_history`.
- [`backend/app/services/recommendation_service.py`](file:///d:/SIGN%20LANGUAGE%20LEARNING%20AND%20ASSESSNMENT/backend/app/services/recommendation_service.py): Generates prioritized recommendations with data-driven explicit human-readable reasons.
- [`backend/app/services/adaptive_learning_service.py`](file:///d:/SIGN%20LANGUAGE%20LEARNING%20AND%20ASSESSNMENT/backend/app/services/adaptive_learning_service.py): Orchestrates the complete 7-stage closed-loop assessment pipeline.

### API Router
- [`backend/app/api/assessment.py`](file:///d:/SIGN%20LANGUAGE%20LEARNING%20AND%20ASSESSNMENT/backend/app/api/assessment.py): `POST /api/v1/assessment/submit` executing the adaptive learning pipeline.

---

## 3. Architecture & Workflow Diagram

```mermaid
graph TB
    subgraph ClientPractice ["📹 1. Real-Time Practice Input"]
        WebcamClient["Webcam Practice Component"]
        LandmarksPayload["Landmark Points JSON (x, y, z)"]
    end

    subgraph AdaptivePipeline ["⚡ 2. Closed-Loop Adaptive Learning Pipeline"]
        AssessmentRouter["Assessment Router (/api/v1/assessment/submit)"]
        MetricsEvaluator["Anatomical Metrics Calculator\n(Gesture, Hand Shape, Motion)"]
        StateMachine["5-State Learner State Machine\n(NOT_ATTEMPTED, LEARNING, IMPROVING, MASTERED, NEEDS_REVISION)"]
        ProfileUpdater["Learner Profile Analytics Engine\n(Streak, Time, Performance Score)"]
        RecommendationEngine["Adaptive Recommendation Engine\n(Generate Reasoned Action Items)"]
    end

    subgraph CloudDatabase ["🗄️ 3. Neon Cloud PostgreSQL Database"]
        AttemptsTable[("assessment_attempts Table")]
        StatesTable[("learner_alphabet_states Table")]
        HistoryTable[("learner_state_history Table")]
        RecommendationsTable[("recommendations Table")]
        ProfilesTable[("learner_profiles Table")]
    end

    WebcamClient -->|Submit Frame Landmarks| LandmarksPayload
    LandmarksPayload --> AssessmentRouter
    AssessmentRouter --> MetricsEvaluator
    
    MetricsEvaluator -->|Log Attempt| AttemptsTable
    MetricsEvaluator --> StateMachine
    
    StateMachine -->|Evaluate Transitions| StatesTable
    StateMachine -->|Log State Change| HistoryTable
    
    StateMachine --> ProfileUpdater
    ProfileUpdater -->|Update Streak & Score| ProfilesTable
    
    ProfileUpdater --> RecommendationEngine
    RecommendationEngine -->|Store Priority Recommendations| RecommendationsTable
    
    RecommendationEngine -->> AssessmentRouter: Return Unified Dashboard Payload
    AssessmentRouter -->> WebcamClient: 200 OK (Instant Dashboard UI Update)
```

---

## 4. Test Plan & Verification Results

### Automated Test Suite
- Test Script: [`backend/tests/test_adaptive_learning.py`](file:///d:/SIGN%20LANGUAGE%20LEARNING%20AND%20ASSESSNMENT/backend/tests/test_adaptive_learning.py)

### Multi-Session Test Scenario
1. **Session 1 (Initial Struggle)**:
   - Attempt sign 'D' with 40% accuracy.
   - *Result*: State transitions `NOT_ATTEMPTED` $\rightarrow$ `LEARNING`. Recommendation generated: *"Focus on sign 'D' - low accuracy"*.
2. **Session 2 (Repeated Mistakes)**:
   - 3 consecutive incorrect attempts on sign 'D'.
   - *Result*: State transitions `LEARNING` $\rightarrow$ `NEEDS_REVISION`. Recommendation generated: *"High mistake count on sign 'D'"*.
3. **Session 3 (High Mastery)**:
   - Submit high accuracy (95%) for sign 'D'.
   - *Result*: State transitions `NEEDS_REVISION` $\rightarrow$ `MASTERED`. Recommendation shifts dynamically to next unattempted sign 'E'.

### Execution Command
```bash
cd backend
py -m unittest tests/test_adaptive_learning.py
```

### Verification Result
- Status: **100% Passed**. Dynamic recommendation shifts verified across all 3 practice sessions.
