import csv
import os
import joblib
import numpy as np

csv_path = os.path.join("..", "datasets", "landmarks_normalized.csv")
if not os.path.exists(csv_path):
    csv_path = os.path.join("..", "datasets", "landmarks.csv")

model = joblib.load(os.path.join("..", "models", "asl_rf_v001", "model.joblib"))

print("Evaluating dataset:", csv_path)
samples_by_label = {}

with open(csv_path, "r") as f:
    reader = csv.reader(f)
    header = next(reader)
    print("Header columns count:", len(header), "First 5 cols:", header[:5], "Last 2 cols:", header[-2:])
    for row in reader:
        if not row or len(row) < 64:
            continue
        label = row[0].strip().upper()
        if label not in samples_by_label:
            samples_by_label[label] = []
        features = [float(x) for x in row[1:64]]
        samples_by_label[label].append(features)

print("Found classes in CSV:", sorted(samples_by_label.keys()))

correct_by_class = {}
total_by_class = {}

for label, samples in sorted(samples_by_label.items()):
    X = np.array(samples, dtype=np.float32)
    preds = model.predict(X)
    probs = model.predict_proba(X)
    max_probs = np.max(probs, axis=1)
    
    correct = np.sum(preds == label)
    total = len(samples)
    correct_by_class[label] = correct
    total_by_class[label] = total
    avg_conf = np.mean(max_probs)
    print(f"Class {label:2s}: {correct:3d}/{total:3d} correct ({correct/total*100:5.1f}%) | Avg Conf: {avg_conf*100:5.1f}%")

total_all = sum(total_by_class.values())
correct_all = sum(correct_by_class.values())
print("=" * 60)
print(f"OVERALL MODEL ACCURACY ON DATASET: {correct_all}/{total_all} ({correct_all/total_all*100:.2f}%)")
