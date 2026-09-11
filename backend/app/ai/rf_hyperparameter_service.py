import os
import sys
import json
from typing import Dict, Any, Optional, List

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))
from scripts.study_rf_hyperparameters import RFHyperparameterStudier

def run_rf_hyperparameter_study(
    train_csv: Optional[str] = None,
    val_csv: Optional[str] = None,
    models_dir: Optional[str] = None,
    report_json: Optional[str] = None,
    n_estimators_grid: Optional[List[int]] = None,
    max_depth_grid: Optional[List[Optional[int]]] = None,
    min_samples_leaf_grid: Optional[List[int]] = None,
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
        report_json = os.path.join(base_dir, "rf_hyperparameter_study.json")

    studier = RFHyperparameterStudier(
        train_csv=train_csv,
        val_csv=val_csv,
        models_dir=models_dir,
        report_json=report_json,
        seed=seed
    )
    return studier.run_study(
        n_estimators_grid=n_estimators_grid,
        max_depth_grid=max_depth_grid,
        min_samples_leaf_grid=min_samples_leaf_grid
    )

def get_rf_hyperparameter_report(report_json: Optional[str] = None) -> Dict[str, Any]:
    if not report_json:
        report_json = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "datasets", "rf_hyperparameter_study.json"))

    if not os.path.exists(report_json):
        return run_rf_hyperparameter_study()

    with open(report_json, "r", encoding="utf-8") as f:
        return json.load(f)
