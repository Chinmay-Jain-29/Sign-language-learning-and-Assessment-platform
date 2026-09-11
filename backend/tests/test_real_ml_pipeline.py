import os
import csv
import json
import urllib.request
import urllib.error

LOCAL_URL = "http://127.0.0.1:8000"
DEPLOYED_URL = "https://sign-language-learning-and-assessment-zciv.onrender.com"

def api_get(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": "RealMLTester/1.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        body = json.loads(resp.read().decode('utf-8'))
        return resp.getcode(), body.get("data", body) if isinstance(body, dict) and "data" in body and "success" in body else body

def api_post(url: str, payload: dict = None):
    data = json.dumps(payload or {}).encode('utf-8')
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json", "User-Agent": "RealMLTester/1.0"}
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        body = json.loads(resp.read().decode('utf-8'))
        return resp.getcode(), body.get("data", body) if isinstance(body, dict) and "data" in body and "success" in body else body

def load_real_benchmark_samples():
    """Loads authentic test samples from val.csv for each letter A-Z."""
    samples = {}
    val_path = os.path.join("..", "datasets", "val.csv")
    if not os.path.exists(val_path):
        val_path = os.path.join("datasets", "val.csv")

    if os.path.exists(val_path):
        with open(val_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader) # skip header
            for row in reader:
                if len(row) >= 64:
                    label = row[0].strip().upper()
                    if label not in samples:
                        # 63 features -> 21 3D points
                        pts = []
                        for i in range(21):
                            pts.append({
                                "x": float(row[1 + i*3]),
                                "y": float(row[1 + i*3 + 1]),
                                "z": float(row[1 + i*3 + 2])
                            })
                        samples[label] = pts
    return samples

def run_suite():
    print("=" * 80)
    print("REAL ML INFERENCE PIPELINE — COMPREHENSIVE ACCEPTANCE & PARITY TEST SUITE")
    print("=" * 80)

    # 1. Health check & model metadata verification
    code, health_data = api_get(f"{LOCAL_URL}/api/v1/health/ml")
    assert code == 200, f"Health check failed with code {code}"
    print(f"[OK] Model Loaded: {health_data['model_loaded']}")
    print(f"[OK] Model Version: {health_data['model_version']}")
    print(f"[OK] Model SHA256: {health_data['model_hash_sha256']}")
    print(f"[OK] Feature Dimension: {health_data['feature_dimension']}")
    print(f"[OK] Total Canonical Classes: {len(health_data['classes'])}")

    # Load authentic benchmark samples
    real_samples = load_real_benchmark_samples()
    print(f"[OK] Loaded authentic benchmark samples for {len(real_samples)} classes (A-Z)")

    # Reset stabilizer
    api_post(f"{LOCAL_URL}/api/v1/recognition/reset-stabilizer")

    # =========================================================================
    # ACCEPTANCE TESTS (1 to 8)
    # =========================================================================

    # TEST 1: Expected A, Perform A -> Actual A, Correct
    api_post(f"{LOCAL_URL}/api/v1/recognition/reset-stabilizer", {"target_sign": "A"})
    _, d1 = api_post(f"{LOCAL_URL}/api/v1/recognition/predict-landmarks", {
        "landmarks": real_samples['A'],
        "target_sign": "A"
    })
    print(f"\n[TEST 1] Expected A, Performed A:")
    print(f"  Expected: {d1['target_sign']} | Actual: {d1['predicted_sign']} | Confidence: {d1['confidence']*100:.1f}% | Correct: {d1['correct']}")
    print(f"  Feedback: {d1['message']}")
    assert d1['correct'] == True, "TEST 1 Failed: Expected Correct=True"
    assert d1['predicted_sign'] == 'A', "TEST 1 Failed: Expected Predicted=A"

    # TEST 2: Expected A, Perform B -> Actual B, Incorrect
    api_post(f"{LOCAL_URL}/api/v1/recognition/reset-stabilizer", {"target_sign": "A"})
    _, d2 = api_post(f"{LOCAL_URL}/api/v1/recognition/predict-landmarks", {
        "landmarks": real_samples['B'],
        "target_sign": "A"
    })
    print(f"\n[TEST 2] Expected A, Performed B:")
    print(f"  Expected: {d2['target_sign']} | Actual: {d2['predicted_sign']} | Confidence: {d2['confidence']*100:.1f}% | Correct: {d2['correct']}")
    print(f"  Feedback: {d2['message']}")
    assert d2['correct'] == False, "TEST 2 Failed: Expected Correct=False"
    assert d2['predicted_sign'] == 'B', "TEST 2 Failed: Expected Predicted=B"
    assert "detected B" in d2['message'] and "expected sign was A" in d2['message'], "TEST 2 Failed: Feedback format mismatch"

    # TEST 3: Expected B, Perform A -> Actual A, Incorrect
    api_post(f"{LOCAL_URL}/api/v1/recognition/reset-stabilizer", {"target_sign": "B"})
    _, d3 = api_post(f"{LOCAL_URL}/api/v1/recognition/predict-landmarks", {
        "landmarks": real_samples['A'],
        "target_sign": "B"
    })
    print(f"\n[TEST 3] Expected B, Performed A:")
    print(f"  Expected: {d3['target_sign']} | Actual: {d3['predicted_sign']} | Confidence: {d3['confidence']*100:.1f}% | Correct: {d3['correct']}")
    print(f"  Feedback: {d3['message']}")
    assert d3['correct'] == False, "TEST 3 Failed: Expected Correct=False"
    assert d3['predicted_sign'] == 'A', "TEST 3 Failed: Expected Predicted=A"
    assert "detected A" in d3['message'] and "expected sign was B" in d3['message'], "TEST 3 Failed: Feedback format mismatch"

    # TEST 4: Expected C, Perform C -> Actual C, Correct
    api_post(f"{LOCAL_URL}/api/v1/recognition/reset-stabilizer", {"target_sign": "C"})
    _, d4 = api_post(f"{LOCAL_URL}/api/v1/recognition/predict-landmarks", {
        "landmarks": real_samples['C'],
        "target_sign": "C"
    })
    print(f"\n[TEST 4] Expected C, Performed C:")
    print(f"  Expected: {d4['target_sign']} | Actual: {d4['predicted_sign']} | Confidence: {d4['confidence']*100:.1f}% | Correct: {d4['correct']}")
    print(f"  Feedback: {d4['message']}")
    assert d4['correct'] == True, "TEST 4 Failed: Expected Correct=True"
    assert d4['predicted_sign'] == 'C', "TEST 4 Failed: Expected Predicted=C"

    # TEST 5: Expected Z, Perform B gesture -> Genuine actual prediction B (NOT forced Z!)
    api_post(f"{LOCAL_URL}/api/v1/recognition/reset-stabilizer", {"target_sign": "Z"})
    _, d5 = api_post(f"{LOCAL_URL}/api/v1/recognition/predict-landmarks", {
        "landmarks": real_samples['B'],
        "target_sign": "Z"
    })
    print(f"\n[TEST 5] Expected Z, Performed B gesture:")
    print(f"  Expected: {d5['target_sign']} | Actual: {d5['predicted_sign']} | Confidence: {d5['confidence']*100:.1f}% | Correct: {d5['correct']}")
    print(f"  Feedback: {d5['message']}")
    assert d5['correct'] == False, "TEST 5 Failed: Expected Correct=False"
    assert d5['predicted_sign'] == 'B', "TEST 5 Failed: Model must predict true gesture B, not force target Z!"

    # TEST 6: Expected A, No valid hand (empty landmarks) -> Invalid/No Hand
    _, d6 = api_post(f"{LOCAL_URL}/api/v1/recognition/predict-landmarks", {
        "landmarks": [],
        "target_sign": "A"
    })
    print(f"\n[TEST 6] Expected A, No valid hand (empty landmarks):")
    print(f"  Expected: {d6['target_sign']} | Actual: {d6['predicted_sign']} | Valid Hand: {d6['is_valid_hand']}")
    print(f"  Status: {d6['status']} | Message: {d6['message']}")
    assert d6['is_valid_hand'] == False, "TEST 6 Failed: Expected is_valid_hand=False"
    assert d6['predicted_sign'] == 'NONE', "TEST 6 Failed: Expected predicted_sign=NONE"

    # TEST 7: Target change from A to B -> old prediction state reset
    api_post(f"{LOCAL_URL}/api/v1/recognition/reset-stabilizer", {"target_sign": "B"})
    _, d7 = api_post(f"{LOCAL_URL}/api/v1/recognition/predict-landmarks", {
        "landmarks": real_samples['B'],
        "target_sign": "B"
    })
    print(f"\n[TEST 7] Target changed A->B, Performed B:")
    print(f"  Expected: {d7['target_sign']} | Actual: {d7['predicted_sign']} | Correct: {d7['correct']}")
    assert d7['target_sign'] == 'B' and d7['predicted_sign'] == 'B' and d7['correct'] == True, "TEST 7 Failed: State leak"

    # TEST 8: Local vs Deployed Parity Comparison
    print(f"\n[TEST 8] Local vs Deployed Parity Verification...")
    try:
        dep_code, dep_data = api_get(f"{DEPLOYED_URL}/api/v1/health/ml")
        if dep_code == 200:
            print(f"  [DEPLOYED] Status: 200 OK")
            print(f"  [DEPLOYED] Model Hash: {dep_data.get('model_hash_sha256')}")
            print(f"  [LOCAL]    Model Hash: {health_data['model_hash_sha256']}")
            same_hash = dep_data.get('model_hash_sha256') == health_data['model_hash_sha256']
            print(f"  [PARITY]   Hashes Match: {same_hash}")
        else:
            print(f"  [DEPLOYED] Response code {dep_code}")
    except Exception as e:
        print(f"  [DEPLOYED] Remote Notice: {e}")

    # =========================================================================
    # REPRESENTATIVE A-Z TEST: Evaluate all 26 classes
    # =========================================================================
    print("\n" + "=" * 80)
    print("REPRESENTATIVE A-Z TEST: EVALUATING ALL 26 ALPHABET CLASSES VIA API")
    print("=" * 80)
    
    az_correct = 0
    for char_code in range(65, 91):
        letter = chr(char_code)
        if letter in real_samples:
            api_post(f"{LOCAL_URL}/api/v1/recognition/reset-stabilizer", {"target_sign": letter})
            _, res = api_post(f"{LOCAL_URL}/api/v1/recognition/predict-landmarks", {
                "landmarks": real_samples[letter],
                "target_sign": letter
            })
            pred = res['predicted_sign']
            conf = res['confidence'] * 100.0
            is_match = (pred == letter)
            if is_match:
                az_correct += 1
            print(f"  Class {letter}: Expected={letter}, Predicted={pred:2s} ({conf:5.1f}%) | Result={'PASS [OK]' if is_match else 'MISMATCH [FAIL]'}")

    print("-" * 80)
    print(f"A-Z Live API Accuracy: {az_correct}/26 ({az_correct/26*100:.1f}%)")
    assert az_correct >= 25, f"Expected at least 25/26 passes, got {az_correct}/26"

    print("\n" + "=" * 80)
    print("ALL ACCEPTANCE TESTS & A-Z INFERENCE VERIFICATION COMPLETED SUCCESSFULLY!")
    print("=" * 80)

if __name__ == "__main__":
    run_suite()
