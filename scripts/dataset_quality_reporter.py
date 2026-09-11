import os
import json
import csv
import numpy as np
from typing import Dict, Any, List, Tuple

class DatasetQualityReporter:
    def __init__(self, input_csv: str, clean_csv: str, invalid_csv: str, report_json: str):
        self.input_csv = os.path.abspath(input_csv)
        self.clean_csv = os.path.abspath(clean_csv)
        self.invalid_csv = os.path.abspath(invalid_csv)
        self.report_json = os.path.abspath(report_json)

    def validate_row(self, row: List[str], header: List[str]) -> Tuple[bool, List[str]]:
        """
        Validates a single CSV landmark row.
        Returns (is_valid, list_of_failure_reasons).
        """
        reasons = []

        # Check total column count (label + 63 coords + sample_path = 65)
        if len(row) < 65:
            reasons.append("incomplete_columns")
            return False, reasons

        label = row[0]
        sample_path = row[-1]
        coords_raw = row[1:-1]

        # 1. Parse floats and check for NaN/Null
        coords = []
        for val in coords_raw:
            try:
                f_val = float(val)
                if np.isnan(f_val) or np.isinf(f_val):
                    reasons.append("nan_or_inf_value")
                    return False, reasons
                coords.append(f_val)
            except ValueError:
                reasons.append("invalid_number_format")
                return False, reasons

        if len(coords) != 63:
            reasons.append("missing_keypoint_coordinates")
            return False, reasons

        # 2. Check X, Y out-of-bounds coordinates (x and y should be [0.0, 1.0])
        # x coordinates are at indices 0, 3, 6 ... 60
        # y coordinates are at indices 1, 4, 7 ... 61
        x_vals = coords[0::3]
        y_vals = coords[1::3]

        for x in x_vals:
            if x < -0.15 or x > 1.15:
                reasons.append("x_out_of_bounds")
                break

        for y in y_vals:
            if y < -0.15 or y > 1.15:
                reasons.append("y_out_of_bounds")
                break

        # 3. Check for degenerate point collapse (e.g., all coordinates identical)
        if len(set(x_vals)) == 1 and len(set(y_vals)) == 1:
            reasons.append("degenerate_point_collapse")

        is_valid = len(reasons) == 0
        return is_valid, reasons

    def process_and_generate_report(self) -> Dict[str, Any]:
        report = {
            "input_csv": self.input_csv,
            "total_samples": 0,
            "valid_samples": 0,
            "invalid_samples": 0,
            "quality_score_percentage": 0.0,
            "failure_reasons_breakdown": {},
            "class_quality": {}
        }

        if not os.path.exists(self.input_csv):
            report["error"] = f"Input CSV file not found: {self.input_csv}"
            return report

        os.makedirs(os.path.dirname(self.clean_csv), exist_ok=True)

        valid_rows = []
        invalid_rows = []

        with open(self.input_csv, "r", encoding="utf-8") as infile:
            reader = csv.reader(infile)
            try:
                header = next(reader)
            except StopIteration:
                report["error"] = "Input CSV file is empty"
                return report

            valid_rows.append(header)
            invalid_rows.append(header + ["failure_reasons"])

            for row in reader:
                report["total_samples"] += 1
                label = row[0] if len(row) > 0 else "UNKNOWN"

                if label not in report["class_quality"]:
                    report["class_quality"][label] = {"total": 0, "valid": 0, "invalid": 0}

                report["class_quality"][label]["total"] += 1

                is_valid, reasons = self.validate_row(row, header)

                if is_valid:
                    report["valid_samples"] += 1
                    report["class_quality"][label]["valid"] += 1
                    valid_rows.append(row)
                else:
                    report["invalid_samples"] += 1
                    report["class_quality"][label]["invalid"] += 1
                    invalid_rows.append(row + [",".join(reasons)])

                    for r in reasons:
                        report["failure_reasons_breakdown"][r] = report["failure_reasons_breakdown"].get(r, 0) + 1

        # Write clean CSV
        with open(self.clean_csv, "w", newline="", encoding="utf-8") as f_clean:
            writer = csv.writer(f_clean)
            writer.writerows(valid_rows)

        # Write invalid CSV
        with open(self.invalid_csv, "w", newline="", encoding="utf-8") as f_inv:
            writer = csv.writer(f_inv)
            writer.writerows(invalid_rows)

        # Compute Quality Score Percentage
        if report["total_samples"] > 0:
            report["quality_score_percentage"] = round((report["valid_samples"] / report["total_samples"]) * 100.0, 2)
        else:
            report["quality_score_percentage"] = 100.0

        # Save JSON Quality Report
        with open(self.report_json, "w", encoding="utf-8") as f_json:
            json.dump(report, f_json, indent=2)

        print(f"Clean dataset saved to: {self.clean_csv}")
        print(f"Quarantined dataset saved to: {self.invalid_csv}")
        print(f"Quality report JSON saved to: {self.report_json}")

        return report

if __name__ == "__main__":
    base_dir = os.path.join(os.path.dirname(__file__), "..", "datasets")
    in_csv = os.path.join(base_dir, "landmarks.csv")
    cl_csv = os.path.join(base_dir, "landmarks_clean.csv")
    inv_csv = os.path.join(base_dir, "landmarks_invalid.csv")
    rep_json = os.path.join(base_dir, "dataset_quality_report.json")

    reporter = DatasetQualityReporter(in_csv, cl_csv, inv_csv, rep_json)
    res = reporter.process_and_generate_report()

    print("--- Dataset Quality Audit Complete ---")
    print(f"Total Samples: {res.get('total_samples', 0)}")
    print(f"Valid Samples: {res.get('valid_samples', 0)}")
    print(f"Invalid Samples: {res.get('invalid_samples', 0)}")
    print(f"Dataset Quality Score: {res.get('quality_score_percentage', 0.0)}%")
