import os
import sys
import csv
import json
import time
import joblib
try:
    import psutil
except ImportError:
    psutil = None
import numpy as np
from typing import Dict, Any, List, Tuple, Optional

class AIInferenceBenchmarker:
    def __init__(
        self,
        test_csv: str,
        model_path: str,
        report_json: str,
        iterations: int = 1000
    ):
        self.test_csv = os.path.abspath(test_csv)
        self.model_path = os.path.abspath(model_path)
        self.report_json = os.path.abspath(report_json)
        self.iterations = iterations

    def _load_data(self) -> Tuple[np.ndarray, np.ndarray]:
        X, y = [], []
        with open(self.test_csv, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader)
            for row in reader:
                if len(row) < 65:
                    continue
                label = row[0]
                coords = [float(v) for v in row[1:64]]
                X.append(coords)
                y.append(label)
        return np.array(X, dtype=np.float32), np.array(y)

    def run_benchmark(self) -> Dict[str, Any]:
        report = {
            "test_csv": self.test_csv,
            "model_path": self.model_path,
            "benchmark_iterations": self.iterations,
            "model_size_mb": 0.0,
            "memory_usage_mb": 0.0,
            "single_sample_latency": {},
            "batch_latencies": {},
            "fps_throughput": 0.0
        }

        if not os.path.exists(self.test_csv) or not os.path.exists(self.model_path):
            report["error"] = f"Test dataset or model missing. Test: {self.test_csv}, Model: {self.model_path}"
            return report

        # Measure initial process memory
        if psutil:
            process = psutil.Process(os.getpid())
            mem_before = process.memory_info().rss / (1024.0 * 1024.0)
        else:
            mem_before = 0.0

        # Load model and measure size
        clf = joblib.load(self.model_path)
        model_size_mb = os.path.getsize(self.model_path) / (1024.0 * 1024.0)
        
        if psutil:
            mem_after = process.memory_info().rss / (1024.0 * 1024.0)
        else:
            mem_after = mem_before

        report["model_size_mb"] = round(model_size_mb, 2)
        report["memory_usage_mb"] = round(max(0.0, mem_after - mem_before), 2)

        X_test, _ = self._load_data()
        num_samples = len(X_test)

        if num_samples == 0:
            report["error"] = "No test samples loaded."
            return report

        # Single sample latency distribution benchmarking
        single_latencies_ms = []
        indices = np.random.choice(num_samples, size=min(self.iterations, num_samples), replace=True)

        # Warm-up run
        _ = clf.predict(X_test[:10])

        for idx in indices:
            sample = X_test[idx:idx+1]
            t0 = time.perf_counter()
            _ = clf.predict(sample)
            t_ms = (time.perf_counter() - t0) * 1000.0
            single_latencies_ms.append(t_ms)

        single_arr = np.array(single_latencies_ms)
        report["single_sample_latency"] = {
            "mean_ms": round(float(np.mean(single_arr)), 4),
            "std_ms": round(float(np.std(single_arr)), 4),
            "min_ms": round(float(np.min(single_arr)), 4),
            "p50_ms": round(float(np.percentile(single_arr, 50)), 4),
            "p95_ms": round(float(np.percentile(single_arr, 95)), 4),
            "p99_ms": round(float(np.percentile(single_arr, 99)), 4),
            "max_ms": round(float(np.max(single_arr)), 4)
        }

        # Calculate FPS throughput for real-time webcam frame processing
        mean_ms = report["single_sample_latency"]["mean_ms"]
        report["fps_throughput"] = round(1000.0 / max(0.0001, mean_ms), 2)

        # Batch size benchmarking (1, 8, 16, 32, 64)
        batch_sizes = [1, 8, 16, 32, 64]
        for b_size in batch_sizes:
            if b_size <= num_samples:
                batch_data = X_test[:b_size]
                b_latencies = []
                for _ in range(50):
                    t0 = time.perf_counter()
                    _ = clf.predict(batch_data)
                    b_latencies.append((time.perf_counter() - t0) * 1000.0)

                b_arr = np.array(b_latencies)
                report["batch_latencies"][f"batch_{b_size}"] = {
                    "total_batch_mean_ms": round(float(np.mean(b_arr)), 4),
                    "per_sample_mean_ms": round(float(np.mean(b_arr) / b_size), 4),
                    "p95_ms": round(float(np.percentile(b_arr, 95)), 4),
                    "throughput_fps": round(1000.0 / max(0.0001, float(np.mean(b_arr) / b_size)), 2)
                }

        os.makedirs(os.path.dirname(self.report_json), exist_ok=True)
        with open(self.report_json, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        print(f"Inference Latency Benchmark Completed.")
        print(f"Single Sample P50: {report['single_sample_latency']['p50_ms']} ms | P95: {report['single_sample_latency']['p95_ms']} ms | FPS: {report['fps_throughput']}")
        print(f"Report saved to: {self.report_json}")
        return report

if __name__ == "__main__":
    base_dir = os.path.join(os.path.dirname(__file__), "..", "datasets")
    t_csv = os.path.join(base_dir, "test.csv")
    m_path = os.path.join(os.path.dirname(__file__), "..", "models", "randomforest_tuned.joblib")
    if not os.path.exists(m_path):
        m_path = os.path.join(os.path.dirname(__file__), "..", "models", "randomforest_model.joblib")
    rep_json = os.path.join(base_dir, "benchmark_report.json")

    benchmarker = AIInferenceBenchmarker(t_csv, m_path, rep_json, iterations=500)
    benchmarker.run_benchmark()
