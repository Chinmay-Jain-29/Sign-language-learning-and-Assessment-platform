import os
import sys
import json
from typing import Dict, Any, Optional

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))
from scripts.error_analysis import ASLErrorAnalyzer

def run_error_analysis(
    test_csv: Optional[str] = None,
    model_path: Optional[str] = None,
    report_json: Optional[str] = None
) -> Dict[str, Any]:
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "datasets"))

    if not test_csv:
        test_csv = os.path.join(base_dir, "test.csv")
    if not model_path:
        model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "models", "randomforest_tuned.joblib"))
        if not os.path.exists(model_path):
            model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "models", "randomforest_model.joblib"))
    if not report_json:
        report_json = os.path.join(base_dir, "error_analysis_report.json")

    analyzer = ASLErrorAnalyzer(
        test_csv=test_csv,
        model_path=model_path,
        report_json=report_json
    )
    return analyzer.run_analysis()

def get_error_analysis_report(report_json: Optional[str] = None) -> Dict[str, Any]:
    if not report_json:
        report_json = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "datasets", "error_analysis_report.json"))

    if not os.path.exists(report_json):
        return run_error_analysis()

    with open(report_json, "r", encoding="utf-8") as f:
        return json.load(f)
