import os
import sys
from typing import Dict, Any, Optional

# Add root directory to sys.path for scripts import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))
from scripts.extract_landmarks import BatchLandmarkExtractor
from scripts.dataset_audit_pipeline import DatasetAuditPipeline
import json

def run_landmark_extraction(
    dataset_dir: Optional[str] = None,
    output_csv: Optional[str] = None,
    max_samples_per_class: Optional[int] = None
) -> Dict[str, Any]:
    if not dataset_dir:
        dataset_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "datasets", "asl_alphabet", "asl_alphabet_train", "asl_alphabet_train"))
    if not output_csv:
        output_csv = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "datasets", "landmarks.csv"))

    extractor = BatchLandmarkExtractor(dataset_dir=dataset_dir, output_csv=output_csv)
    stats = extractor.extract_landmarks_batch(max_samples_per_class=max_samples_per_class)
    return stats

def get_dataset_audit_report(audit_json_path: Optional[str] = None) -> Dict[str, Any]:
    if not audit_json_path:
        audit_json_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "datasets", "dataset_audit.json"))

    if os.path.exists(audit_json_path):
        with open(audit_json_path, "r", encoding="utf-8") as f:
            return json.load(f)

    # If audit file does not exist yet, run pipeline
    pipeline = DatasetAuditPipeline(audit_json=audit_json_path)
    return pipeline.run_pipeline()

