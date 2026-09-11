import os
import sys
import csv
import json
import joblib
import numpy as np
from typing import Dict, Any, List, Tuple, Optional
from sklearn.metrics import confusion_matrix, classification_report, precision_recall_fscore_support

# Anatomical explanations for common ASL confusion pairs
ANATOMICAL_EXPLANATIONS = {
    ("M", "N"): "Both signs involve a tucked thumb under fingers; 'M' tucks under 3 fingers while 'N' tucks under 2 fingers.",
    ("N", "M"): "Both signs involve a tucked thumb under fingers; 'M' tucks under 3 fingers while 'N' tucks under 2 fingers.",
    ("A", "S"): "Both signs form a closed fist; 'A' places the thumb alongside the index finger while 'S' crosses the thumb over the fingers.",
    ("S", "A"): "Both signs form a closed fist; 'A' places the thumb alongside the index finger while 'S' crosses the thumb over the fingers.",
    ("E", "O"): "Both signs feature curved fingers touching the thumb; 'E' rests fingertips on the thumb edge while 'O' forms an oval ring.",
    ("O", "E"): "Both signs feature curved fingers touching the thumb; 'E' rests fingertips on the thumb edge while 'O' forms an oval ring.",
    ("K", "V"): "Both signs extend index and middle fingers in a V-shape; 'K' places the thumb tip between index and middle fingers.",
    ("V", "K"): "Both signs extend index and middle fingers in a V-shape; 'K' places the thumb tip between index and middle fingers.",
    ("R", "U"): "Both signs extend index and middle fingers upright; 'R' crosses index over middle finger while 'U' holds them tightly together.",
    ("U", "R"): "Both signs extend index and middle fingers upright; 'R' crosses index over middle finger while 'U' holds them tightly together.",
    ("G", "H"): "Both signs point fingers horizontally; 'G' extends index finger and thumb, while 'H' extends index and middle fingers together.",
    ("H", "G"): "Both signs point fingers horizontally; 'G' extends index finger and thumb, while 'H' extends index and middle fingers together.",
    ("C", "O"): "Both signs form a curved hand shape; 'C' maintains an open gap between thumb and fingers while 'O' closes the gap."
}

class ASLErrorAnalyzer:
    def __init__(
        self,
        test_csv: str,
        model_path: str,
        report_json: str
    ):
        self.test_csv = os.path.abspath(test_csv)
        self.model_path = os.path.abspath(model_path)
        self.report_json = os.path.abspath(report_json)

    def _load_data(self) -> Tuple[np.ndarray, np.ndarray]:
        X, y = [], []
        with open(self.test_csv, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader)
            for row in reader:
                if len(row) < 65:
                    continue
                label = row[0]
                coords = [float(v) for v in row[1:64]]
                X.append(coords)
                y.append(label)
        return np.array(X, dtype=np.float32), np.array(y)

    def run_analysis(self) -> Dict[str, Any]:
        report = {
            "test_csv": self.test_csv,
            "model_path": self.model_path,
            "total_test_samples": 0,
            "overall_accuracy": 0.0,
            "macro_f1": 0.0,
            "weighted_f1": 0.0,
            "classes": [],
            "per_class_metrics": {},
            "top_confused_pairs": [],
            "confusion_matrix": []
        }

        if not os.path.exists(self.test_csv):
            report["error"] = f"Test dataset missing: {self.test_csv}"
            return report

        if not os.path.exists(self.model_path):
            report["error"] = f"Model artifact missing: {self.model_path}"
            return report

        X_test, y_true = self._load_data()
        clf = joblib.load(self.model_path)
        y_pred = clf.predict(X_test)

        labels = sorted(list(set(y_true).union(set(y_pred))))
        report["total_test_samples"] = len(X_test)
        report["classes"] = labels

        acc = float(np.mean(y_true == y_pred))
        p_m, r_m, f1_m, _ = precision_recall_fscore_support(y_true, y_pred, average="macro", zero_division=0)
        p_w, r_w, f1_w, _ = precision_recall_fscore_support(y_true, y_pred, average="weighted", zero_division=0)

        report["overall_accuracy"] = round(acc, 4)
        report["macro_f1"] = round(float(f1_m), 4)
        report["weighted_f1"] = round(float(f1_w), 4)

        # Per-class metrics calculation
        p_class, r_class, f1_class, supp_class = precision_recall_fscore_support(y_true, y_pred, labels=labels, zero_division=0)
        for i, label in enumerate(labels):
            report["per_class_metrics"][label] = {
                "precision": round(float(p_class[i]), 4),
                "recall": round(float(r_class[i]), 4),
                "f1_score": round(float(f1_class[i]), 4),
                "support": int(supp_class[i])
            }

        # Confusion matrix computation
        cm = confusion_matrix(y_true, y_pred, labels=labels)
        report["confusion_matrix"] = cm.tolist()

        # Identify top confused pairs (where true != pred)
        confused_pairs = []
        for i, true_label in enumerate(labels):
            for j, pred_label in enumerate(labels):
                if i != j and cm[i, j] > 0:
                    count = int(cm[i, j])
                    explanation = ANATOMICAL_EXPLANATIONS.get(
                        (true_label, pred_label),
                        f"Visual geometric overlap in landmark spatial configuration between '{true_label}' and '{pred_label}'."
                    )
                    confused_pairs.append({
                        "true_label": true_label,
                        "predicted_label": pred_label,
                        "error_count": count,
                        "error_percentage": round((count / max(1, supp_class[i])) * 100.0, 2),
                        "anatomical_explanation": explanation
                    })

        # Sort by highest error count
        confused_pairs.sort(key=lambda x: x["error_count"], reverse=True)
        report["top_confused_pairs"] = confused_pairs[:10]

        os.makedirs(os.path.dirname(self.report_json), exist_ok=True)
        with open(self.report_json, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        print(f"Error Analysis Completed. Test Accuracy: {report['overall_accuracy']*100:.2f}% | Top Confused Pairs: {len(confused_pairs)}")
        print(f"Report saved to: {self.report_json}")
        return report

if __name__ == "__main__":
    base_dir = os.path.join(os.path.dirname(__file__), "..", "datasets")
    t_csv = os.path.join(base_dir, "test.csv")
    m_path = os.path.join(os.path.dirname(__file__), "..", "models", "randomforest_tuned.joblib")
    if not os.path.exists(m_path):
        m_path = os.path.join(os.path.dirname(__file__), "..", "models", "randomforest_model.joblib")
    rep_json = os.path.join(base_dir, "error_analysis_report.json")

    analyzer = ASLErrorAnalyzer(t_csv, m_path, rep_json)
    res = analyzer.run_analysis()
    print("\n--- Top Confused Gesture Pairs ---")
    for pair in res.get("top_confused_pairs", [])[:5]:
        print(f"True: {pair['true_label']} -> Pred: {pair['predicted_label']} | Errors: {pair['error_count']} ({pair['error_percentage']}%)")
        print(f"   Explanation: {pair['anatomical_explanation']}")
