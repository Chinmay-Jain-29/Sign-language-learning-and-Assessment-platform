# Landmark Normalization Specification (`docs/LANDMARK_NORMALIZATION.md`)

This document outlines the mathematical formulation, implementation rationale, and performance guarantees of the hand landmark normalization pipeline used across training and real-time inference.

---

## 1. Why Landmark Normalization is Needed

Raw 3D hand keypoints extracted by MediaPipe depend heavily on:
1. **Camera Distance & Scale**: A hand close to the camera produces larger coordinate spans than a hand far away.
2. **Bounding Box Offset & Position**: Moving a hand across the camera frame shifts raw $(x, y)$ values arbitrarily.
3. **User Hand Anatomical Variation**: Individual variations in hand size impact raw Euclidean distances.

Without normalization, a machine learning model would overfit to camera distance and image position rather than learning scale-invariant finger posture geometries.

---

## 2. Mathematical Formulation

Given a 21-landmark hand pose $P = \{ (x_i, y_i, z_i) \}_{i=0}^{20}$, where $P_0 = (x_0, y_0, z_0)$ represents the wrist landmark:

### Step 1: Translation (Wrist Origin Shift)
Shift the wrist landmark $P_0$ to $(0, 0, 0)$:
$$P'_{i} = P_{i} - P_{0} \quad \forall i \in \{0, 1, \dots, 20\}$$

### Step 2: Scale Calculation
Compute the maximum Euclidean distance from the wrist origin across all 21 keypoints:
$$S = \max_{i \in \{0, \dots, 20\}} \sqrt{ (x'_i)^2 + (y'_i)^2 + (z'_i)^2 }$$

### Step 3: Scale Normalization & Zero-Division Safety
Divide all coordinates by the hand scale $S$:
$$P''_{i} = \frac{P'_{i}}{\max(S, 10^{-6})}$$

The resulting 63-element feature vector $(x''_0, y''_0, z''_0, \dots, x''_{20}, y''_{20}, z''_{20})$ is bounded, zero-centered at the wrist, and invariant to translation and distance.

---

## 3. Before & After Coordinate Examples

### Raw Landmark Input (Sample 'A'):
- Wrist $(x_0, y_0, z_0) = (0.521, 0.784, 0.000)$
- Index Tip $(x_{8}, y_{8}, z_{8}) = (0.490, 0.510, -0.045)$
- Maximum Euclidean Scale $S = 0.285$

### Normalized Landmark Output:
- Wrist $(x''_0, y''_0, z''_0) = (0.000, 0.000, 0.000)$
- Index Tip $(x''_{8}, y''_{8}, z''_{8}) = (-0.108, -0.961, -0.158)$
- Maximum Euclidean Scale $S'' = 1.000$

---

## 4. Uniformity Guarantee

The exact same transformation function `LandmarkNormalizer.normalize()` is executed:
- During batch feature extraction on `datasets/asl_alphabet/asl_alphabet_train`.
- Inside backend API real-time inference (`/api/v1/practice/attempt`).
- On frontend MediaPipe webcam canvas processing.

No model is ever trained or evaluated on unnormalized coordinates.
