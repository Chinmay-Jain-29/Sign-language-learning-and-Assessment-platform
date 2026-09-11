import os
import sys
import csv
import json
import time
import joblib
import numpy as np
from typing import Dict, Any, Tuple

from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

class ClassifierExperimentRunner:
    def __init__(
        self,
        train_csv: str,
        val_csv: str,
        models_dir: str,
        report_json: str,
        report_csv: str = None,
        seed: int = 42
    ):
        self.train_csv = os.path.abspath(train_csv)
        self.val_csv = os.path.abspath(val_csv)
        self.models_dir = os.path.abspath(models_dir)
        self.report_json = os.path.abspath(report_json)
        self.report_csv = os.path.abspath(report_csv) if report_csv else os.path.join(os.path.dirname(self.report_json), "comparison_report.csv")
        self.seed = seed

    def _load_data(self, csv_path: str) -> Tuple[np.ndarray, np.ndarray]:
        X, y = [], []
        with open(csv_path, "r", encoding="utf-8") as f:
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

    def run_experiments(self) -> Dict[str, Any]:
        report = {
            "train_csv": self.train_csv,
            "val_csv": self.val_csv,
            "models_directory": self.models_dir,
            "classifiers": {},
            "best_model": None,
            "best_accuracy": 0.0
        }

        if not os.path.exists(self.train_csv) or not os.path.exists(self.val_csv):
            report["error"] = f"Training or validation CSV missing. Train: {self.train_csv}, Val: {self.val_csv}"
            return report

        X_train, y_train = self._load_data(self.train_csv)
        X_val, y_val = self._load_data(self.val_csv)

        report["training_samples"] = len(X_train)
        report["validation_samples"] = len(X_val)
        report["feature_dim"] = X_train.shape[1] if len(X_train) > 0 else 0

        classifiers = {
            "RandomForest": RandomForestClassifier(n_estimators=100, random_state=self.seed, n_jobs=-1),
            "DecisionTree": DecisionTreeClassifier(random_state=self.seed),
            "SVM": SVC(kernel="rbf", C=1.0, probability=True, random_state=self.seed),
            "KNN": KNeighborsClassifier(n_neighbors=5)
        }

        os.makedirs(self.models_dir, exist_ok=True)

        for name, clf in classifiers.items():
            t0 = time.time()
            clf.fit(X_train, y_train)
            t_train = time.time() - t0

            t1 = time.time()
            y_pred = clf.predict(X_val)
            t_infer = time.time() - t1

            acc = float(accuracy_score(y_val, y_pred))
            precision_macro, recall_macro, f1_macro, _ = precision_recall_fscore_support(y_val, y_pred, average="macro", zero_division=0)
            precision_weighted, recall_weighted, f1_weighted, _ = precision_recall_fscore_support(y_val, y_pred, average="weighted", zero_division=0)

            model_path = os.path.join(self.models_dir, f"{name.lower()}_model.joblib")
            joblib.dump(clf, model_path)

            report["classifiers"][name] = {
                "accuracy": round(acc, 4),
                "precision_macro": round(float(precision_macro), 4),
                "recall_macro": round(float(recall_macro), 4),
                "f1_macro": round(float(f1_macro), 4),
                "precision_weighted": round(float(precision_weighted), 4),
                "recall_weighted": round(float(recall_weighted), 4),
                "f1_weighted": round(float(f1_weighted), 4),
                "training_time_sec": round(t_train, 4),
                "inference_time_sec": round(t_infer, 4),
                "inference_ms_per_sample": round((t_infer / max(1, len(X_val))) * 1000.0, 4),
                "model_artifact": model_path
            }

            if acc > report["best_accuracy"]:
                report["best_accuracy"] = round(acc, 4)
                report["best_model"] = name

        # Save JSON report
        os.makedirs(os.path.dirname(self.report_json), exist_ok=True)
        with open(self.report_json, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        # Save CSV report
        os.makedirs(os.path.dirname(self.report_csv), exist_ok=True)
        with open(self.report_csv, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["model_name", "accuracy", "precision_macro", "recall_macro", "f1_macro", "training_time_seconds", "p50_latency_ms"])
            for name, metrics in report["classifiers"].items():
                writer.writerow([
                    name,
                    metrics["accuracy"],
                    metrics["precision_macro"],
                    metrics["recall_macro"],
                    metrics["f1_macro"],
                    metrics["training_time_sec"],
                    metrics["inference_ms_per_sample"]
                ])

        print(f"Classifier comparison completed. Best Model: {report['best_model']} ({report['best_accuracy']*100:.2f}% Accuracy)")
        print(f"JSON report saved to: {self.report_json}")
        print(f"CSV report saved to: {self.report_csv}")
        return report

if __name__ == "__main__":
    base_dir = os.path.join(os.path.dirname(__file__), "..", "datasets")
    tr_csv = os.path.join(base_dir, "train.csv")
    va_csv = os.path.join(base_dir, "val.csv")
    m_dir = os.path.join(os.path.dirname(__file__), "..", "models")
    rep_json = os.path.join(base_dir, "classifier_experiments_report.json")
    rep_csv = os.path.join(base_dir, "comparison_report.csv")

    runner = ClassifierExperimentRunner(tr_csv, va_csv, m_dir, rep_json, rep_csv)
    res = runner.run_experiments()
    print("\n--- Classifier Benchmark Results ---")
    for clf_name, metrics in res.get("classifiers", {}).items():
        print(f"{clf_name:15s} | Accuracy: {metrics['accuracy']*100:6.2f}% | Macro F1: {metrics['f1_macro']:6.4f} | Train Time: {metrics['training_time_sec']:6.4f}s")
