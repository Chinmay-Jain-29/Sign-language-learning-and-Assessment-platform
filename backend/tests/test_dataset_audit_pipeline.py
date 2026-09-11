import sys
import os
import csv
import json
import unittest
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts.dataset_audit_pipeline import DatasetAuditPipeline

class TestDatasetAuditPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        cls.temp_dir = os.path.join(cls.base_dir, "datasets", "temp_audit_test")
        os.makedirs(cls.temp_dir, exist_ok=True)

        cls.mock_dataset_dir = os.path.join(cls.temp_dir, "asl_mock")
        cls.audit_json = os.path.join(cls.temp_dir, "dataset_audit.json")
        cls.features_csv = os.path.join(cls.temp_dir, "landmarks_raw.csv")

        # Create mock classes with asymmetrical class counts (A=5, B=3) to verify no 3000 limit or truncations
        cls.class_a_dir = os.path.join(cls.mock_dataset_dir, "A")
        cls.class_b_dir = os.path.join(cls.mock_dataset_dir, "B")
        os.makedirs(cls.class_a_dir, exist_ok=True)
        os.makedirs(cls.class_b_dir, exist_ok=True)

        # Create dummy image files
        import cv2
        dummy_img = np.zeros((100, 100, 3), dtype=np.uint8)

        for i in range(5):
            cv2.imwrite(os.path.join(cls.class_a_dir, f"sample_a_{i}.jpg"), dummy_img)
        for i in range(3):
            cv2.imwrite(os.path.join(cls.class_b_dir, f"sample_b_{i}.jpg"), dummy_img)

        # Add 1 corrupt file and 1 unsupported format file to Class A
        with open(os.path.join(cls.class_a_dir, "corrupt.jpg"), "w") as f:
            f.write("NOT_AN_IMAGE")
        with open(os.path.join(cls.class_a_dir, "unsupported.txt"), "w") as f:
            f.write("UNSUPPORTED_FORMAT")

        # Run pipeline on mock dataset
        cls.pipeline = DatasetAuditPipeline(
            dataset_dir=cls.mock_dataset_dir,
            audit_json=cls.audit_json,
            features_csv=cls.features_csv
        )
        cls.audit_res = cls.pipeline.run_pipeline()

    @classmethod
    def tearDownClass(cls):
        # Cleanup mock files
        import shutil
        if os.path.exists(cls.temp_dir):
            try:
                shutil.rmtree(cls.temp_dir)
            except Exception:
                pass

    def test_01_actual_class_counts_preserved(self):
        # Rule 1: Actual class counts are preserved (Class A total=7, Class B total=3)
        self.assertEqual(self.audit_res["classes"]["A"]["total_items"], 7)  # 5 valid + 1 corrupt + 1 txt
        self.assertEqual(self.audit_res["classes"]["B"]["total_items"], 3)  # 3 valid

    def test_02_no_hidden_3000_limit(self):
        # Rule 2: No hidden 3000 limit or class truncations applied
        for c, metrics in self.audit_res["classes"].items():
            self.assertNotEqual(metrics["total_items"], 3000)

    def test_03_total_count_equals_sum_of_class_counts(self):
        # Rule 3: Total count equals sum of class counts
        sum_classes = sum(m["total_items"] for m in self.audit_res["classes"].values())
        self.assertEqual(self.audit_res["summary"]["total_items"], sum_classes)
        self.assertEqual(self.audit_res["summary"]["total_items"], 10)

    def test_04_valid_plus_invalid_equals_total(self):
        # Rule 4: Valid + invalid = total count
        val = self.audit_res["summary"]["valid_items"]
        inv = self.audit_res["summary"]["invalid_items"]
        tot = self.audit_res["summary"]["total_items"]
        self.assertEqual(val + inv, tot)

    def test_05_all_valid_samples_attempted_for_feature_extraction(self):
        # Rule 5: All valid samples are attempted for feature extraction
        self.assertEqual(
            self.audit_res["feature_extraction"]["attempted"],
            self.audit_res["summary"]["valid_items"]
        )

    def test_06_successful_plus_failed_equals_attempted(self):
        # Rule 6: Successful + failed extraction = attempted
        succ = self.audit_res["feature_extraction"]["successful"]
        fail = self.audit_res["feature_extraction"]["failed"]
        att = self.audit_res["feature_extraction"]["attempted"]
        self.assertEqual(succ + fail, att)

    def test_07_feature_dimension_equals_63(self):
        # Rule 7: Feature dimension = 63
        self.assertEqual(self.audit_res["feature_extraction"]["feature_dimension"], 63)

    def test_08_class_wise_counts_reconcile_with_global(self):
        # Rule 8: Class-wise counts reconcile with global counts
        sum_succ = sum(m["successful"] for m in self.audit_res["feature_extraction_by_class"].values())
        self.assertEqual(self.audit_res["feature_extraction"]["successful"], sum_succ)

    def test_09_invalid_samples_have_recorded_reasons(self):
        # Rule 9: Invalid samples have a recorded reason
        reasons_a = self.audit_res["classes"]["A"]["invalid_reasons"]
        self.assertEqual(reasons_a["corrupt_image"], 1)
        self.assertEqual(reasons_a["unsupported_format"], 1)

    def test_10_feature_csv_contains_extracted_samples(self):
        # Rule 10: Feature CSV contains header and output structure
        self.assertTrue(os.path.exists(self.features_csv))
        with open(self.features_csv, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader)
            self.assertEqual(header[0], "sample_id")
            self.assertEqual(header[2], "class")
            self.assertEqual(len(header), 68)  # sample_id + image_path + class + 63 coords + status + version

    def test_11_no_duplicate_sample_ids(self):
        # Rule 11: Duplicate sample IDs are not present
        sample_ids = []
        with open(self.features_csv, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                sample_ids.append(row[0])
        self.assertEqual(len(sample_ids), len(set(sample_ids)))

    def test_12_13_14_missing_nan_inf_detection(self):
        # Rule 12, 13, 14: Check for missing, NaN, Inf values
        with open(self.features_csv, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                coords_str = row[3:66]
                self.assertEqual(len(coords_str), 63)
                for val in coords_str:
                    f_val = float(val)
                    self.assertFalse(np.isnan(f_val))
                    self.assertFalse(np.isinf(f_val))

    def test_15_original_dataset_files_never_modified(self):
        # Rule 15: Original files preserved intact
        self.assertTrue(os.path.exists(os.path.join(self.class_a_dir, "sample_a_0.jpg")))
        self.assertTrue(os.path.exists(os.path.join(self.class_b_dir, "sample_b_0.jpg")))

if __name__ == "__main__":
    unittest.main()
