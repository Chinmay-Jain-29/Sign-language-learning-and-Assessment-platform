import os
import sys
import csv
import json
import time
import datetime
import cv2
import numpy as np
from typing import Dict, Any, List, Optional, Tuple

# Ensure project root & backend are in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from backend.app.ai.hand_tracking.hand_tracker import HandTracker

class DatasetAuditPipeline:
    def __init__(
        self,
        dataset_dir: Optional[str] = None,
        audit_json: Optional[str] = None,
        features_csv: Optional[str] = None
    ):
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        if not dataset_dir:
            dataset_dir = os.path.join(
                base_dir, "datasets", "asl_alphabet", "asl_alphabet_train", "asl_alphabet_train"
            )
        if not audit_json:
            audit_json = os.path.join(base_dir, "datasets", "dataset_audit.json")
        if not features_csv:
            features_csv = os.path.join(base_dir, "datasets", "features", "landmarks_raw.csv")

        self.dataset_dir = os.path.abspath(dataset_dir)
        self.audit_json = os.path.abspath(audit_json)
        self.features_csv = os.path.abspath(features_csv)

        # Fallback check for dataset directory
        if not os.path.exists(self.dataset_dir):
            fallback = os.path.join(base_dir, "datasets")
            if os.path.exists(fallback):
                self.dataset_dir = fallback

        self.tracker = HandTracker(static_image_mode=True, max_num_hands=1)

    def run_pipeline(self) -> Dict[str, Any]:
        print("==================================================")
        print("  STARTING FULL DATASET AUDIT & FEATURE PIPELINE  ")
        print("==================================================")
        print(f"Target Directory: {self.dataset_dir}")
        print(f"Audit JSON: {self.audit_json}")
        print(f"Features CSV: {self.features_csv}\n")

        os.makedirs(os.path.dirname(self.audit_json), exist_ok=True)
        os.makedirs(os.path.dirname(self.features_csv), exist_ok=True)

        start_time = time.time()

        # Audit Data Structure
        audit_data = {
            "dataset_name": os.path.basename(self.dataset_dir),
            "dataset_version": "1.0.0",
            "generated_at": datetime.datetime.utcnow().isoformat() + "Z",
            "summary": {
                "total_items": 0,
                "valid_items": 0,
                "invalid_items": 0,
                "valid_percentage": 0.0,
                "invalid_percentage": 0.0,
                "total_classes": 0
            },
            "classes": {},
            "validation": {
                "total_scanned": 0,
                "corrupt_images": 0,
                "unsupported_formats": 0,
                "valid_images": 0
            },
            "feature_extraction": {
                "attempted": 0,
                "successful": 0,
                "failed": 0,
                "feature_dimension": 63,
                "success_percentage": 0.0,
                "failure_percentage": 0.0
            },
            "feature_extraction_by_class": {}
        }

        # Prepare CSV Header
        header = ["sample_id", "image_path", "class"]
        for i in range(21):
            header.extend([f"x{i}", f"y{i}", f"z{i}"])
        header.extend(["extraction_status", "feature_version"])

        valid_extensions = {".jpg", ".jpeg", ".png", ".bmp"}
        sample_counter = 0

        with open(self.features_csv, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(header)

            # Discover all subdirectories (classes) dynamically without hardcoding limits or class names
            class_directories = []
            for item in sorted(os.listdir(self.dataset_dir)):
                item_path = os.path.join(self.dataset_dir, item)
                if os.path.isdir(item_path):
                    class_directories.append((item.upper(), item_path))

            if not class_directories:
                # Root itself might contain images
                class_directories.append(("ALL", self.dataset_dir))

            audit_data["summary"]["total_classes"] = len(class_directories)

            for class_name, class_path in class_directories:
                print(f"Scanning & Extracting Class: '{class_name}' from {class_path}...")

                # Initialize per-class metrics
                if class_name not in audit_data["classes"]:
                    audit_data["classes"][class_name] = {
                        "total_items": 0,
                        "valid_items": 0,
                        "invalid_items": 0,
                        "valid_percentage": 0.0,
                        "invalid_percentage": 0.0,
                        "invalid_reasons": {
                            "corrupt_image": 0,
                            "unsupported_format": 0,
                            "no_hand_detected": 0,
                            "multiple_hands": 0,
                            "invalid_landmarks": 0,
                            "feature_extraction_failed": 0,
                            "other": 0
                        }
                    }

                if class_name not in audit_data["feature_extraction_by_class"]:
                    audit_data["feature_extraction_by_class"][class_name] = {
                        "valid_samples": 0,
                        "attempted": 0,
                        "successful": 0,
                        "failed": 0
                    }

                class_files = sorted([
                    f for f in os.listdir(class_path) 
                    if os.path.isfile(os.path.join(class_path, f))
                ])

                for filename in class_files:
                    img_path = os.path.join(class_path, filename)
                    ext = os.path.splitext(filename)[1].lower()

                    audit_data["summary"]["total_items"] += 1
                    audit_data["validation"]["total_scanned"] += 1
                    audit_data["classes"][class_name]["total_items"] += 1

                    # 1. Format Check
                    if ext not in valid_extensions:
                        audit_data["summary"]["invalid_items"] += 1
                        audit_data["validation"]["unsupported_formats"] += 1
                        audit_data["classes"][class_name]["invalid_items"] += 1
                        audit_data["classes"][class_name]["invalid_reasons"]["unsupported_format"] += 1
                        continue

                    # 2. Image Load Check
                    try:
                        img_bgr = cv2.imread(img_path)
                        if img_bgr is None:
                            audit_data["summary"]["invalid_items"] += 1
                            audit_data["validation"]["corrupt_images"] += 1
                            audit_data["classes"][class_name]["invalid_items"] += 1
                            audit_data["classes"][class_name]["invalid_reasons"]["corrupt_image"] += 1
                            continue
                    except Exception:
                        audit_data["summary"]["invalid_items"] += 1
                        audit_data["validation"]["corrupt_images"] += 1
                        audit_data["classes"][class_name]["invalid_items"] += 1
                        audit_data["classes"][class_name]["invalid_reasons"]["corrupt_image"] += 1
                        continue

                    # Valid image file confirmed
                    audit_data["summary"]["valid_items"] += 1
                    audit_data["validation"]["valid_images"] += 1
                    audit_data["classes"][class_name]["valid_items"] += 1
                    audit_data["feature_extraction_by_class"][class_name]["valid_samples"] += 1

                    # 3. Feature Extraction Attempt
                    audit_data["feature_extraction"]["attempted"] += 1
                    audit_data["feature_extraction_by_class"][class_name]["attempted"] += 1

                    try:
                        detections = self.tracker.detect(img_bgr)

                        if not detections or len(detections) == 0:
                            audit_data["feature_extraction"]["failed"] += 1
                            audit_data["feature_extraction_by_class"][class_name]["failed"] += 1
                            audit_data["classes"][class_name]["invalid_reasons"]["no_hand_detected"] += 1
                            continue

                        if len(detections) > 1:
                            audit_data["feature_extraction"]["failed"] += 1
                            audit_data["feature_extraction_by_class"][class_name]["failed"] += 1
                            audit_data["classes"][class_name]["invalid_reasons"]["multiple_hands"] += 1
                            continue

                        landmarks = detections[0].landmarks
                        if len(landmarks) != 21:
                            audit_data["feature_extraction"]["failed"] += 1
                            audit_data["feature_extraction_by_class"][class_name]["failed"] += 1
                            audit_data["classes"][class_name]["invalid_reasons"]["invalid_landmarks"] += 1
                            continue

                        # Extract x, y, z coordinates
                        coords = []
                        is_coords_valid = True
                        for lm in landmarks:
                            if np.isnan(lm.x) or np.isnan(lm.y) or np.isnan(lm.z) or \
                               np.isinf(lm.x) or np.isinf(lm.y) or np.isinf(lm.z):
                                is_coords_valid = False
                                break
                            coords.extend([round(lm.x, 6), round(lm.y, 6), round(lm.z, 6)])

                        if not is_coords_valid or len(coords) != 63:
                            audit_data["feature_extraction"]["failed"] += 1
                            audit_data["feature_extraction_by_class"][class_name]["failed"] += 1
                            audit_data["classes"][class_name]["invalid_reasons"]["invalid_landmarks"] += 1
                            continue

                        # Feature extraction success
                        sample_counter += 1
                        sample_id = f"SMP_{sample_counter:06d}"
                        rel_path = os.path.relpath(img_path, self.dataset_dir)

                        row = [sample_id, rel_path, class_name] + coords + ["SUCCESS", "v1.0"]
                        writer.writerow(row)

                        audit_data["feature_extraction"]["successful"] += 1
                        audit_data["feature_extraction_by_class"][class_name]["successful"] += 1

                    except Exception as e:
                        audit_data["feature_extraction"]["failed"] += 1
                        audit_data["feature_extraction_by_class"][class_name]["failed"] += 1
                        audit_data["classes"][class_name]["invalid_reasons"]["feature_extraction_failed"] += 1

                print(
                    f"Class '{class_name}' Complete: Total={audit_data['classes'][class_name]['total_items']}, "
                    f"Valid={audit_data['classes'][class_name]['valid_items']}, "
                    f"Extracted={audit_data['feature_extraction_by_class'][class_name]['successful']}"
                )

        # Compute Percentages & Accounting Reconciliation
        tot_items = audit_data["summary"]["total_items"]
        val_items = audit_data["summary"]["valid_items"]
        inv_items = audit_data["summary"]["invalid_items"]

        audit_data["summary"]["valid_percentage"] = round((val_items / tot_items * 100.0), 2) if tot_items > 0 else 0.0
        audit_data["summary"]["invalid_percentage"] = round((inv_items / tot_items * 100.0), 2) if tot_items > 0 else 0.0

        fe_attempted = audit_data["feature_extraction"]["attempted"]
        fe_success = audit_data["feature_extraction"]["successful"]
        fe_failed = audit_data["feature_extraction"]["failed"]

        audit_data["feature_extraction"]["success_percentage"] = round((fe_success / fe_attempted * 100.0), 2) if fe_attempted > 0 else 0.0
        audit_data["feature_extraction"]["failure_percentage"] = round((fe_failed / fe_attempted * 100.0), 2) if fe_attempted > 0 else 0.0

        # Compute Class Percentages
        for c in audit_data["classes"]:
            c_tot = audit_data["classes"][c]["total_items"]
            c_val = audit_data["classes"][c]["valid_items"]
            c_inv = audit_data["classes"][c]["invalid_items"]
            audit_data["classes"][c]["valid_percentage"] = round((c_val / c_tot * 100.0), 2) if c_tot > 0 else 0.0
            audit_data["classes"][c]["invalid_percentage"] = round((c_inv / c_tot * 100.0), 2) if c_tot > 0 else 0.0

        # Mathematical Accounting Verification Assertions
        assert tot_items == val_items + inv_items, f"Accounting Error: {tot_items} != {val_items} + {inv_items}"
        assert tot_items == sum(audit_data["classes"][c]["total_items"] for c in audit_data["classes"])
        assert val_items == sum(audit_data["classes"][c]["valid_items"] for c in audit_data["classes"])
        assert inv_items == sum(audit_data["classes"][c]["invalid_items"] for c in audit_data["classes"])

        assert fe_attempted == val_items, f"Accounting Error: FE Attempted ({fe_attempted}) != Valid Images ({val_items})"
        assert fe_attempted == fe_success + fe_failed, f"Accounting Error: FE Attempted ({fe_attempted}) != Success ({fe_success}) + Failed ({fe_failed})"
        assert fe_success == sum(audit_data["feature_extraction_by_class"][c]["successful"] for c in audit_data["feature_extraction_by_class"])

        # Save Audit JSON
        with open(self.audit_json, "w", encoding="utf-8") as f_audit:
            json.dump(audit_data, f_audit, indent=2)

        elapsed = round(time.time() - start_time, 2)
        print("\n==================================================")
        print("  DATASET AUDIT & FEATURE PIPELINE COMPLETED     ")
        print("==================================================")
        print(f"Total Scanned Items: {tot_items}")
        print(f"Valid Items: {val_items} ({audit_data['summary']['valid_percentage']}%)")
        print(f"Invalid Items: {inv_items} ({audit_data['summary']['invalid_percentage']}%)")
        print(f"Feature Extraction Attempted: {fe_attempted}")
        print(f"Feature Extraction Successful: {fe_success} ({audit_data['feature_extraction']['success_percentage']}%)")
        print(f"Feature Extraction Failed: {fe_failed} ({audit_data['feature_extraction']['failure_percentage']}%)")
        print(f"Execution Duration: {elapsed} seconds")
        print(f"Audit JSON Saved: {self.audit_json}")
        print(f"Features CSV Saved: {self.features_csv}")

        return audit_data

if __name__ == "__main__":
    pipeline = DatasetAuditPipeline()
    pipeline.run_pipeline()
