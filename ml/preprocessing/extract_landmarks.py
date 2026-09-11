import os
import sys
import csv
import time
import cv2
import numpy as np
from typing import Dict, Any, List, Optional

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from backend.app.ai.hand_tracking.hand_tracker import HandTracker

class BatchLandmarkExtractor:
    def __init__(self, dataset_dir: Optional[str] = None, output_csv: Optional[str] = None):
        if not dataset_dir:
            # Explicitly target training dataset folder: datasets/asl_alphabet/asl_alphabet_train/asl_alphabet_train
            dataset_dir = os.path.join(
                os.path.dirname(__file__), "..", "datasets", "asl_alphabet", "asl_alphabet_train", "asl_alphabet_train"
            )
        if not output_csv:
            output_csv = os.path.join(os.path.dirname(__file__), "..", "datasets", "landmarks.csv")

        self.dataset_dir = os.path.abspath(dataset_dir)
        self.output_csv = os.path.abspath(output_csv)
        self.tracker = HandTracker(static_image_mode=True, max_num_hands=1)

    def extract_landmarks_batch(self, max_samples_per_class: Optional[int] = None) -> Dict[str, Any]:
        """
        Iterates specifically over asl_alphabet_train training image directories (3,000 images per class A-Z),
        extracts 21 3D landmarks (63 coordinates) per hand, and writes rows into landmarks.csv.
        """
        stats = {
            "dataset_dir": self.dataset_dir,
            "output_csv": self.output_csv,
            "total_images_scanned": 0,
            "successful_extractions": 0,
            "failed_extractions": 0,
            "duration_seconds": 0.0,
            "throughput_fps": 0.0,
            "class_counts": {}
        }

        if not os.path.exists(self.dataset_dir):
            # Fallback to general datasets directory if full training set folder does not exist
            fallback = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "datasets"))
            if os.path.exists(fallback):
                self.dataset_dir = fallback
                stats["dataset_dir"] = self.dataset_dir
            else:
                stats["error"] = f"Training dataset directory not found: {self.dataset_dir}"
                return stats

        os.makedirs(os.path.dirname(self.output_csv), exist_ok=True)

        # Prepare CSV Header: label, x0, y0, z0 ... x20, y20, z20, sample_path
        header = ["label"]
        for i in range(21):
            header.extend([f"x{i}", f"y{i}", f"z{i}"])
        header.append("sample_path")

        start_time = time.time()

        with open(self.output_csv, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(header)

            expected_alphabet = [chr(c) for c in range(ord('A'), ord('Z') + 1)]
            
            for root, dirs, files in os.walk(self.dataset_dir):
                folder_name = os.path.basename(root).upper()
                if folder_name not in expected_alphabet:
                    continue

                print(f"Extracting landmarks for Class '{folder_name}'...")
                samples_processed = 0
                for file in sorted(files):
                    ext = os.path.splitext(file)[1].lower()
                    if ext in ['.jpg', '.jpeg', '.png', '.bmp']:
                        if max_samples_per_class and samples_processed >= max_samples_per_class:
                            break

                        img_path = os.path.join(root, file)
                        stats["total_images_scanned"] += 1
                        samples_processed += 1

                        try:
                            img_bgr = cv2.imread(img_path)
                            if img_bgr is None:
                                stats["failed_extractions"] += 1
                                continue

                            detections = self.tracker.detect(img_bgr)
                            if detections and len(detections[0].landmarks) == 21:
                                row = [folder_name]
                                for lm in detections[0].landmarks:
                                    row.extend([round(lm.x, 6), round(lm.y, 6), round(lm.z, 6)])
                                rel_path = os.path.relpath(img_path, self.dataset_dir)
                                row.append(rel_path)

                                writer.writerow(row)
                                stats["successful_extractions"] += 1
                                stats["class_counts"][folder_name] = stats["class_counts"].get(folder_name, 0) + 1
                            else:
                                stats["failed_extractions"] += 1
                        except Exception as e:
                            stats["failed_extractions"] += 1

                print(f"Class '{folder_name}' complete: {stats['class_counts'].get(folder_name, 0)} landmarks extracted.")

        elapsed = time.time() - start_time
        stats["duration_seconds"] = round(elapsed, 2)
        stats["throughput_fps"] = round(stats["total_images_scanned"] / elapsed, 2) if elapsed > 0 else 0.0

        return stats

if __name__ == "__main__":
    extractor = BatchLandmarkExtractor()
    # Extract ALL training images for all classes A-Z
    res = extractor.extract_landmarks_batch(max_samples_per_class=None)

    print("\n--- Batch Training Landmark Extraction Complete ---")
    print(f"Dataset Directory: {res['dataset_dir']}")
    print(f"Total Scanned: {res['total_images_scanned']}")
    print(f"Successful Extractions: {res['successful_extractions']}")
    print(f"Failed / No Hand Detected: {res['failed_extractions']}")
    print(f"Duration: {res['duration_seconds']} seconds ({res['throughput_fps']} FPS)")
    print(f"Saved CSV: {res['output_csv']}")
