import os
import sys
import csv
import json
import random
from typing import Dict, Any, List

class StratifiedDatasetSplitter:
    def __init__(
        self,
        input_csv: str,
        train_csv: str,
        val_csv: str,
        test_csv: str,
        report_json: str,
        train_ratio: float = 0.70,
        val_ratio: float = 0.15,
        test_ratio: float = 0.15,
        seed: int = 42
    ):
        self.input_csv = os.path.abspath(input_csv)
        self.train_csv = os.path.abspath(train_csv)
        self.val_csv = os.path.abspath(val_csv)
        self.test_csv = os.path.abspath(test_csv)
        self.report_json = os.path.abspath(report_json)
        self.train_ratio = train_ratio
        self.val_ratio = val_ratio
        self.test_ratio = test_ratio
        self.seed = seed

    def process_and_split(self) -> Dict[str, Any]:
        random.seed(self.seed)

        report = {
            "input_csv": self.input_csv,
            "total_samples": 0,
            "train_count": 0,
            "val_count": 0,
            "test_count": 0,
            "train_ratio_achieved": 0.0,
            "val_ratio_achieved": 0.0,
            "test_ratio_achieved": 0.0,
            "class_distribution": {},
            "seed": self.seed
        }

        if not os.path.exists(self.input_csv):
            report["error"] = f"Input CSV file not found: {self.input_csv}"
            return report

        # Read CSV rows grouped by class label
        header = None
        class_samples: Dict[str, List[List[str]]] = {}

        with open(self.input_csv, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            try:
                header = next(reader)
            except StopIteration:
                report["error"] = "Input CSV is empty"
                return report

            for row in reader:
                if len(row) < 2:
                    continue
                label = row[0]
                if label not in class_samples:
                    class_samples[label] = []
                class_samples[label].append(row)
                report["total_samples"] += 1

        train_rows = [header]
        val_rows = [header]
        test_rows = [header]

        for label, samples in class_samples.items():
            # Shuffle deterministically per class
            random.shuffle(samples)
            n_total = len(samples)

            n_train = int(round(n_total * self.train_ratio))
            n_val = int(round(n_total * self.val_ratio))
            # Put remaining into test set to guarantee exact count
            n_test = n_total - (n_train + n_val)

            c_train = samples[:n_train]
            c_val = samples[n_train:n_train + n_val]
            c_test = samples[n_train + n_val:]

            train_rows.extend(c_train)
            val_rows.extend(c_val)
            test_rows.extend(c_test)

            report["class_distribution"][label] = {
                "total": n_total,
                "train": len(c_train),
                "val": len(c_val),
                "test": len(c_test)
            }

        report["train_count"] = len(train_rows) - 1
        report["val_count"] = len(val_rows) - 1
        report["test_count"] = len(test_rows) - 1

        if report["total_samples"] > 0:
            report["train_ratio_achieved"] = round((report["train_count"] / report["total_samples"]) * 100.0, 2)
            report["val_ratio_achieved"] = round((report["val_count"] / report["total_samples"]) * 100.0, 2)
            report["test_ratio_achieved"] = round((report["test_count"] / report["total_samples"]) * 100.0, 2)

        # Write split CSV files
        os.makedirs(os.path.dirname(self.train_csv), exist_ok=True)
        with open(self.train_csv, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerows(train_rows)

        with open(self.val_csv, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerows(val_rows)

        with open(self.test_csv, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerows(test_rows)

        # Write JSON split report
        with open(self.report_json, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        print(f"Train split saved to: {self.train_csv} ({report['train_count']} samples)")
        print(f"Val split saved to: {self.val_csv} ({report['val_count']} samples)")
        print(f"Test split saved to: {self.test_csv} ({report['test_count']} samples)")
        print(f"Split metadata JSON saved to: {self.report_json}")

        return report

if __name__ == "__main__":
    base_dir = os.path.join(os.path.dirname(__file__), "..", "datasets")
    in_csv = os.path.join(base_dir, "landmarks_normalized.csv")
    tr_csv = os.path.join(base_dir, "train.csv")
    va_csv = os.path.join(base_dir, "val.csv")
    te_csv = os.path.join(base_dir, "test.csv")
    rep_json = os.path.join(base_dir, "dataset_split_report.json")

    splitter = StratifiedDatasetSplitter(in_csv, tr_csv, va_csv, te_csv, rep_json)
    res = splitter.process_and_split()
    print("--- Stratified Dataset Splitting Complete ---")
    print(f"Total Samples: {res['total_samples']}")
    print(f"Train (70%): {res['train_count']} ({res.get('train_ratio_achieved', 0.0)}%)")
    print(f"Val (15%): {res['val_count']} ({res.get('val_ratio_achieved', 0.0)}%)")
    print(f"Test (15%): {res['test_count']} ({res.get('test_ratio_achieved', 0.0)}%)")
