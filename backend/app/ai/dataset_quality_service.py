import os
import sys
from typing import Dict, Any, Optional

# Add root to sys.path for scripts import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))
from scripts.dataset_quality_reporter import DatasetQualityReporter

def audit_dataset_quality(
    input_csv: Optional[str] = None,
    clean_csv: Optional[str] = None,
    invalid_csv: Optional[str] = None,
    report_json: Optional[str] = None
) -> Dict[str, Any]:
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "datasets"))

    if not input_csv:
        input_csv = os.path.join(base_dir, "landmarks.csv")
    if not clean_csv:
        clean_csv = os.path.join(base_dir, "landmarks_clean.csv")
    if not invalid_csv:
        invalid_csv = os.path.join(base_dir, "landmarks_invalid.csv")
    if not report_json:
        report_json = os.path.join(base_dir, "dataset_quality_report.json")

    reporter = DatasetQualityReporter(input_csv, clean_csv, invalid_csv, report_json)
    return reporter.process_and_generate_report()
