import os
import sys
from typing import Dict, Any

# Import DatasetExplorer from scripts
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))
from scripts.dataset_explorer import DatasetExplorer
from scripts.camera_test import CameraVerifier

def get_dataset_summary() -> Dict[str, Any]:
    dataset_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "datasets"))
    explorer = DatasetExplorer(dataset_dir)
    report = explorer.scan_dataset()
    return report

def get_camera_status() -> Dict[str, Any]:
    verifier = CameraVerifier(camera_index=0)
    return verifier.verify_camera()
