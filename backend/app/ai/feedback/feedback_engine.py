import numpy as np
from typing import List, Dict, Any, Tuple

# Landmarks indices reference (MediaPipe Hands):
# Wrist: 0
# Thumb: 1, 2, 3, 4
# Index: 5, 6, 7, 8
# Middle: 9, 10, 11, 12
# Ring: 13, 14, 15, 16
# Pinky: 17, 18, 19, 20

FINGER_JOINTS = {
    'Thumb': [1, 2, 3, 4],
    'Index': [5, 6, 7, 8],
    'Middle': [9, 10, 11, 12],
    'Ring': [13, 14, 15, 16],
    'Pinky': [17, 18, 19, 20]
}

def calculate_joint_angle(p1: np.ndarray, p2: np.ndarray, p3: np.ndarray) -> float:
    """Calculates angle in degrees between p1-p2 and p3-p2."""
    v1 = p1 - p2
    v2 = p3 - p2
    cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-6)
    angle = np.degrees(np.arccos(np.clip(cos_angle, -1.0, 1.0)))
    return float(angle)

def analyze_hand_feedback(
    expected_sign: str,
    predicted_sign: str,
    confidence: float,
    landmarks: List[Dict[str, float]]
) -> Tuple[float, float, float, float, str]:
    """
    Analyzes landmark geometry vs expected sign requirements.
    Returns:
    (overall_accuracy, hand_shape_accuracy, position_accuracy, motion_accuracy, feedback_string)
    """
    coords = np.array([[lm['x'], lm['y'], lm['z']] for lm in landmarks], dtype=np.float32)
    
    # 1. Base shape accuracy derived from ML classifier match & confidence
    if predicted_sign == expected_sign:
        hand_shape_acc = max(75.0, confidence)
    else:
        # Penalize if predicted sign differs
        hand_shape_acc = max(30.0, confidence * 0.4)
        
    # 2. Position & Orientation accuracy (wrist-to-middle MCP angle relative to vertical)
    wrist = coords[0]
    middle_mcp = coords[9]
    direction_vec = middle_mcp - wrist
    vertical_alignment = abs(direction_vec[1]) / (np.linalg.norm(direction_vec) + 1e-6)
    position_acc = min(100.0, max(50.0, float(vertical_alignment * 100.0)))
    
    # 3. Motion / Stability accuracy
    # Check joint smoothness across fingers
    joint_strains = []
    for finger, indices in FINGER_JOINTS.items():
        p1, p2, p3 = coords[indices[0]], coords[indices[1]], coords[indices[2]]
        angle = calculate_joint_angle(p1, p2, p3)
        joint_strains.append(angle)
        
    motion_acc = float(np.clip(100.0 - np.std(joint_strains) * 0.5, 60.0, 98.0))
    
    # Weighted overall accuracy score
    overall_acc = round(
        0.50 * hand_shape_acc + 0.30 * position_acc + 0.20 * motion_acc, 2
    )
    
    # 4. Generate intelligent corrective feedback
    feedback_messages = []
    
    if predicted_sign == expected_sign:
        if overall_acc >= 90.0:
            feedback_messages.append(f"Excellent! Perfect '{expected_sign}' hand formation with crisp joint positioning.")
        else:
            feedback_messages.append(f"Good job forming '{expected_sign}'! Keep your hand steady and hold fingers firm.")
    else:
        feedback_messages.append(f"Sign detected as '{predicted_sign}' instead of '{expected_sign}'.")
        
        # Anatomical guidance based on expected sign
        if expected_sign in ['A', 'S', 'E', 'M', 'N', 'T']:
            feedback_messages.append("Ensure your fingers are tightly curled into a fist shape.")
            # Check thumb position
            thumb_tip = coords[4]
            index_mcp = coords[5]
            if np.linalg.norm(thumb_tip - index_mcp) > 0.3:
                feedback_messages.append("Tuck thumb closely against the side of your index finger.")
                
        elif expected_sign in ['B', 'C', 'F', 'D', 'K', 'L', 'V', 'W']:
            feedback_messages.append(f"Extend your fingers upright clearly for sign '{expected_sign}'.")
            index_angle = calculate_joint_angle(coords[5], coords[6], coords[7])
            if index_angle < 140.0:
                feedback_messages.append("Straighten your index finger completely upwards.")
        else:
            feedback_messages.append("Align your palm facing forward towards the camera.")

    full_feedback = " ".join(feedback_messages)
    
    return overall_acc, round(hand_shape_acc, 2), round(position_acc, 2), round(motion_acc, 2), full_feedback
