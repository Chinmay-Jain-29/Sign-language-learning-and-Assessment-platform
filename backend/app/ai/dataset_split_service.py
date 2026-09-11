import os
import sys
from typing import Dict, Any, Optional

# Add root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))
from scripts.split_dataset import StratifiedDatasetSplitter

def run_dataset_split(
    input_csv: Optional[str] = None,
    train_csv: Optional[str] = None,
    val_csv: Optional[str] = None,
    test_csv: Optional[str] = None,
    report_json: Optional[str] = None,
    train_ratio: float = 0.70,
    val_ratio: float = 0.15,
    test_ratio: float = 0.15,
    seed: int = 42
) -> Dict[str, Any]:
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "datasets"))

    if not input_csv:
        input_csv = os.path.join(base_dir, "landmarks_normalized.csv")
    if not train_csv:
        train_csv = os.path.join(base_dir, "train.csv")
    if not val_csv:
        val_csv = os.path.join(base_dir, "val.csv")
    if not test_csv:
        test_csv = os.path.join(base_dir, "test.csv")
    if not report_json:
        report_json = os.path.join(base_dir, "dataset_split_report.json")

    splitter = StratifiedDatasetSplitter(
        input_csv=input_csv,
        train_csv=train_csv,
        val_csv=val_csv,
        test_csv=test_csv,
        report_json=report_json,
        train_ratio=train_ratio,
        val_ratio=val_ratio,
        test_ratio=test_ratio,
        seed=seed
    )
    return splitter.process_and_split()
