import os
import sys
import csv
import json
import time
import joblib
import numpy as np
from typing import Dict, Any, List, Tuple, Optional

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

class RFHyperparameterStudier:
    def __init__(
        self,
        train_csv: str,
        val_csv: str,
        models_dir: str,
        report_json: str,
        seed: int = 42
    ):
        self.train_csv = os.path.abspath(train_csv)
        self.val_csv = os.path.abspath(val_csv)
        self.models_dir = os.path.abspath(models_dir)
        self.report_json = os.path.abspath(report_json)
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

    def run_study(
        self,
        n_estimators_grid: Optional[List[int]] = None,
        max_depth_grid: Optional[List[Optional[int]]] = None,
        min_samples_leaf_grid: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        if n_estimators_grid is None:
            n_estimators_grid = [50, 100, 200]
        if max_depth_grid is None:
            max_depth_grid = [10, 20, None]
        if min_samples_leaf_grid is None:
            min_samples_leaf_grid = [1, 2]

        report = {
            "train_csv": self.train_csv,
            "val_csv": self.val_csv,
            "grid": {
                "n_estimators": n_estimators_grid,
                "max_depth": [str(d) if d is not None else "None" for d in max_depth_grid],
                "min_samples_leaf": min_samples_leaf_grid
            },
            "experiments": [],
            "best_config": None,
            "best_accuracy": 0.0,
            "best_f1_macro": 0.0,
            "selection_rationale": ""
        }

        if not os.path.exists(self.train_csv) or not os.path.exists(self.val_csv):
            report["error"] = f"Training or validation CSV missing. Train: {self.train_csv}, Val: {self.val_csv}"
            return report

        X_train, y_train = self._load_data(self.train_csv)
        X_val, y_val = self._load_data(self.val_csv)

        report["training_samples"] = len(X_train)
        report["validation_samples"] = len(X_val)
        report["feature_dim"] = X_train.shape[1] if len(X_train) > 0 else 0

        os.makedirs(self.models_dir, exist_ok=True)
        temp_model_dir = os.path.join(self.models_dir, "study_temp")
        os.makedirs(temp_model_dir, exist_ok=True)

        best_score = -1.0
        best_clf = None
        best_exp_data = None

        exp_id = 1
        for n_est in n_estimators_grid:
            for depth in max_depth_grid:
                for min_leaf in min_samples_leaf_grid:
                    clf = RandomForestClassifier(
                        n_estimators=n_est,
                        max_depth=depth,
                        min_samples_leaf=min_leaf,
                        random_state=self.seed,
                        n_jobs=-1
                    )

                    t0 = time.time()
                    clf.fit(X_train, y_train)
                    t_train = time.time() - t0

                    t1 = time.time()
                    y_pred = clf.predict(X_val)
                    t_infer = time.time() - t1

                    acc = float(accuracy_score(y_val, y_pred))
                    p_macro, r_macro, f1_macro, _ = precision_recall_fscore_support(
                        y_val, y_pred, average="macro", zero_division=0
                    )
                    p_w, r_w, f1_w, _ = precision_recall_fscore_support(
                        y_val, y_pred, average="weighted", zero_division=0
                    )

                    # Estimate temporary model size
                    temp_path = os.path.join(temp_model_dir, f"rf_exp_{exp_id}.joblib")
                    joblib.dump(clf, temp_path)
                    model_size_mb = os.path.getsize(temp_path) / (1024.0 * 1024.0)

                    exp_res = {
                        "exp_id": exp_id,
                        "n_estimators": n_est,
                        "max_depth": depth if depth is not None else "None",
                        "min_samples_leaf": min_leaf,
                        "accuracy": round(acc, 4),
                        "precision_macro": round(float(p_macro), 4),
                        "recall_macro": round(float(r_macro), 4),
                        "f1_macro": round(float(f1_macro), 4),
                        "precision_weighted": round(float(p_w), 4),
                        "f1_weighted": round(float(f1_w), 4),
                        "training_time_sec": round(t_train, 4),
                        "inference_time_sec": round(t_infer, 4),
                        "inference_ms_per_sample": round((t_infer / max(1, len(X_val))) * 1000.0, 4),
                        "model_size_mb": round(model_size_mb, 2)
                    }

                    report["experiments"].append(exp_res)

                    # Score favors high accuracy while considering model size efficiency
                    combined_score = acc * 0.8 + f1_macro * 0.2
                    if combined_score > best_score:
                        best_score = combined_score
                        best_clf = clf
                        best_exp_data = exp_res

                    exp_id += 1

        # Clean up temp study models
        for f in os.listdir(temp_model_dir):
            try:
                os.remove(os.path.join(temp_model_dir, f))
            except Exception:
                pass
        try:
            os.rmdir(temp_model_dir)
        except Exception:
            pass

        if best_clf is not None and best_exp_data is not None:
            tuned_model_path = os.path.join(self.models_dir, "randomforest_tuned.joblib")
            joblib.dump(best_clf, tuned_model_path)

            report["best_config"] = {
                "n_estimators": best_exp_data["n_estimators"],
                "max_depth": best_exp_data["max_depth"],
                "min_samples_leaf": best_exp_data["min_samples_leaf"]
            }
            report["best_accuracy"] = best_exp_data["accuracy"]
            report["best_f1_macro"] = best_exp_data["f1_macro"]
            report["tuned_model_artifact"] = tuned_model_path
            report["selection_rationale"] = (
                f"Selected Random Forest with n_estimators={best_exp_data['n_estimators']}, "
                f"max_depth={best_exp_data['max_depth']}, min_samples_leaf={best_exp_data['min_samples_leaf']} "
                f"achieving peak validation accuracy of {best_exp_data['accuracy']*100:.2f}% and macro F1 of {best_exp_data['f1_macro']:.4f} "
                f"with an inference latency of {best_exp_data['inference_ms_per_sample']:.4f} ms/sample "
                f"and model size of {best_exp_data['model_size_mb']:.2f} MB."
            )

        os.makedirs(os.path.dirname(self.report_json), exist_ok=True)
        with open(self.report_json, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        print(f"Hyperparameter Study Completed. Best Config: {report['best_config']} ({report['best_accuracy']*100:.2f}% Accuracy)")
        print(f"Tuned model saved to: {report.get('tuned_model_artifact')}")
        print(f"Full study report saved to: {self.report_json}")
        return report

if __name__ == "__main__":
    base_dir = os.path.join(os.path.dirname(__file__), "..", "datasets")
    tr_csv = os.path.join(base_dir, "train.csv")
    va_csv = os.path.join(base_dir, "val.csv")
    m_dir = os.path.join(os.path.dirname(__file__), "..", "models")
    rep_json = os.path.join(base_dir, "rf_hyperparameter_study.json")

    studier = RFHyperparameterStudier(tr_csv, va_csv, m_dir, rep_json)
    res = studier.run_study()
