import os
import sys
import csv
import numpy as np
from typing import Dict, Any

# Add root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from backend.app.ai.preprocessing.normalize_landmarks import LandmarkNormalizer

class DatasetNormalizer:
    def __init__(self, input_csv: str, output_csv: str):
        self.input_csv = os.path.abspath(input_csv)
        self.output_csv = os.path.abspath(output_csv)

    def process(self) -> Dict[str, Any]:
        stats = {
            "input_csv": self.input_csv,
            "output_csv": self.output_csv,
            "total_rows_normalized": 0,
            "error": None
        }

        if not os.path.exists(self.input_csv):
            stats["error"] = f"Input CSV file not found: {self.input_csv}"
            return stats

        os.makedirs(os.path.dirname(self.output_csv), exist_ok=True)

        normalized_rows = []

        with open(self.input_csv, "r", encoding="utf-8") as infile:
            reader = csv.reader(infile)
            try:
                header = next(reader)
                normalized_rows.append(header)
            except StopIteration:
                stats["error"] = "Input CSV file is empty"
                return stats

            for row in reader:
                if len(row) < 65:
                    continue

                label = row[0]
                sample_path = row[-1]
                raw_coords = np.array([float(x) for x in row[1:-1]], dtype=np.float32)

                # Normalize 63 coordinates
                norm_coords = LandmarkNormalizer.normalize_array(raw_coords)

                out_row = [label] + [round(float(val), 6) for val in norm_coords] + [sample_path]
                normalized_rows.append(out_row)
                stats["total_rows_normalized"] += 1

        with open(self.output_csv, "w", newline="", encoding="utf-8") as outfile:
            writer = csv.writer(outfile)
            writer.writerows(normalized_rows)

        print(f"Normalized dataset saved to: {self.output_csv} ({stats['total_rows_normalized']} rows)")
        return stats

if __name__ == "__main__":
    base_dir = os.path.join(os.path.dirname(__file__), "..", "datasets")
    in_file = os.path.join(base_dir, "landmarks_clean.csv")
    out_file = os.path.join(base_dir, "landmarks_normalized.csv")

    normalizer = DatasetNormalizer(in_file, out_file)
    res = normalizer.process()
    print("--- Landmark Dataset Normalization Complete ---")
    print(f"Rows Normalized: {res['total_rows_normalized']}")
