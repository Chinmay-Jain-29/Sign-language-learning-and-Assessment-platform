import os
import csv
import joblib
import numpy as np

for m_name in ["models/asl_rf_v001/model.joblib", "models/randomforest_model.joblib", "models/decisiontree_model.joblib"]:
    m_path = os.path.join("..", m_name)
    if not os.path.exists(m_path):
        continue
    clf = joblib.load(m_path)
    print(f"\n================ Model: {m_name} (Size: {os.path.getsize(m_path):,} bytes) ================")
    print("Classes:", clf.classes_)
    
    # Test on val.csv
    val_csv = os.path.join("..", "datasets", "val.csv")
    if os.path.exists(val_csv):
        X_val, y_val = [], []
        with open(val_csv, "r") as f:
            reader = csv.reader(f)
            header = next(reader)
            for row in reader:
                if len(row) >= 64:
                    y_val.append(row[0].strip().upper())
                    X_val.append([float(x) for x in row[1:64]])
        X_val = np.array(X_val, dtype=np.float32)
        y_val = np.array(y_val)
        
        preds = clf.predict(X_val)
        acc = np.mean(preds == y_val) * 100.0
        print(f"Validation Accuracy on {len(y_val)} samples from val.csv: {acc:.2f}%")
        
        # Test class breakdown for first 5 classes
        for c in ['A', 'B', 'C', 'D', 'E', 'Z']:
            mask = (y_val == c)
            if np.sum(mask) > 0:
                c_acc = np.mean(preds[mask] == y_val[mask]) * 100.0
                print(f"  Class {c}: {c_acc:.1f}% ({np.sum(mask)} samples)")
