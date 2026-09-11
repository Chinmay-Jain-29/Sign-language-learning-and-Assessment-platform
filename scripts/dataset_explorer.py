import os
import sys
import csv
import json
from typing import Dict, Any, Optional
from PIL import Image

class DatasetExplorer:
    def __init__(self, base_dir: Optional[str] = None):
        if not base_dir:
            candidate = os.path.abspath(os.path.join(
                os.path.dirname(__file__), "..", "datasets", "asl_alphabet", "asl_alphabet_train", "asl_alphabet_train"
            ))
            if os.path.exists(candidate):
                base_dir = candidate
            else:
                base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "datasets"))
        self.base_dir = os.path.abspath(base_dir)

    def scan_dataset(self) -> Dict[str, Any]:
        report = {
            "base_directory": self.base_dir,
            "total_classes": 0,
            "total_samples": 0,
            "total_images": 0,
            "class_names": [],
            "samples_per_class": {},
            "class_distribution": {},
            "largest_class": {"name": None, "count": 0},
            "smallest_class": {"name": None, "count": 0},
            "is_balanced": True,
            "class_balance_ratio": 1.0,
            "image_dimensions": [],
            "file_formats": {},
            "corrupt_images": [],
            "wlasl_metadata": None
        }

        if not os.path.exists(self.base_dir):
            report["error"] = f"Directory not found: {self.base_dir}"
            return report

        class_counts = {}
        file_formats = {}
        dimensions_set = set()
        corrupt_list = []
        sampled_count = 0

        for root, dirs, files in os.walk(self.base_dir):
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if not ext:
                    continue

                file_formats[ext] = file_formats.get(ext, 0) + 1

                if ext in ['.jpg', '.jpeg', '.png', '.bmp']:
                    file_path = os.path.join(root, file)
                    class_name = os.path.basename(root)
                    
                    class_counts[class_name] = class_counts.get(class_name, 0) + 1
                    report["total_samples"] += 1

                    if sampled_count < 1000 or sampled_count % 50 == 0:
                        try:
                            with Image.open(file_path) as img:
                                dimensions_set.add(f"{img.width}x{img.height} ({img.mode})")
                        except Exception:
                            corrupt_list.append(file_path)
                    sampled_count += 1

        report["total_images"] = report["total_samples"]
        report["total_classes"] = len(class_counts)
        report["class_names"] = sorted(list(class_counts.keys()))
        report["samples_per_class"] = class_counts
        report["class_distribution"] = class_counts
        report["file_formats"] = file_formats
        report["corrupt_images"] = corrupt_list
        report["image_dimensions"] = list(dimensions_set)

        if class_counts:
            sorted_classes = sorted(class_counts.items(), key=lambda x: x[1], reverse=True)
            report["largest_class"] = {"name": sorted_classes[0][0], "count": sorted_classes[0][1]}
            report["smallest_class"] = {"name": sorted_classes[-1][0], "count": sorted_classes[-1][1]}
            
            max_c = sorted_classes[0][1]
            min_c = sorted_classes[-1][1]
            report["class_balance_ratio"] = round(max_c / max(1, min_c), 2)
            report["is_balanced"] = (max_c == min_c)

        wlasl_json = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "datasets", "wlasl", "WLASL_v0.3.json"))
        if os.path.exists(wlasl_json):
            try:
                with open(wlasl_json, "r", encoding="utf-8") as f:
                    wlasl_data = json.load(f)
                    unique_signs = len(wlasl_data)
                    total_instances = sum(len(item.get("instances", [])) for item in wlasl_data)
                    report["wlasl_metadata"] = {
                        "annotation_file": wlasl_json,
                        "unique_signs_count": unique_signs,
                        "total_video_instances": total_instances
                    }
            except Exception:
                pass

        return report

    def save_reports(self, report: Dict[str, Any], json_path: str, csv_path: str):
        os.makedirs(os.path.dirname(json_path), exist_ok=True)
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        os.makedirs(os.path.dirname(csv_path), exist_ok=True)
        with open(csv_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["class_name", "sample_count"])
            for class_name, count in report.get("samples_per_class", {}).items():
                writer.writerow([class_name, count])

        print(f"Dataset Report JSON saved to: {json_path}")
        print(f"Dataset Report CSV saved to: {csv_path}")

if __name__ == "__main__":
    explorer = DatasetExplorer()
    rep = explorer.scan_dataset()
    print("--- ASL Dataset Audit Summary ---")
    print(f"Directory: {rep['base_directory']}")
    print(f"Total Samples: {rep['total_samples']}")
    print(f"Total Classes: {rep['total_classes']}")
    print(f"Largest Class: {rep['largest_class']}")
    print(f"Smallest Class: {rep['smallest_class']}")
    print(f"Is Balanced: {rep['is_balanced']} (Ratio: {rep['class_balance_ratio']})")
    print(f"Corrupt Images Count: {len(rep['corrupt_images'])}")

    base_out = os.path.join(os.path.dirname(__file__), "..", "datasets")
    json_out = os.path.join(base_out, "dataset_report.json")
    csv_out = os.path.join(base_out, "dataset_report.csv")
    explorer.save_reports(rep, json_out, csv_out)
