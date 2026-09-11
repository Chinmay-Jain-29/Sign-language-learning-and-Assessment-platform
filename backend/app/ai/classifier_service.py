import os
import sys
import json
from typing import Dict, Any, Optional

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))
from scripts.train_classifiers import ClassifierExperimentRunner

def run_classifier_experiments(
    train_csv: Optional[str] = None,
    val_csv: Optional[str] = None,
    models_dir: Optional[str] = None,
    report_json: Optional[str] = None,
    seed: int = 42
) -> Dict[str, Any]:
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "datasets"))

    if not train_csv:
        train_csv = os.path.join(base_dir, "train.csv")
    if not val_csv:
        val_csv = os.path.join(base_dir, "val.csv")
    if not models_dir:
        models_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "models"))
    if not report_json:
        report_json = os.path.join(base_dir, "classifier_experiments_report.json")

    runner = ClassifierExperimentRunner(
        train_csv=train_csv,
        val_csv=val_csv,
        models_dir=models_dir,
        report_json=report_json,
        seed=seed
    )
    return runner.run_experiments()

def get_classifier_report(report_json: Optional[str] = None) -> Dict[str, Any]:
    if not report_json:
        report_json = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "datasets", "classifier_experiments_report.json"))

    if not os.path.exists(report_json):
        # Auto-train if report doesn't exist yet
        return run_classifier_experiments()

    with open(report_json, "r", encoding="utf-8") as f:
        return json.load(f)
