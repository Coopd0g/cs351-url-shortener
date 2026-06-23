"""
CS 351 Final Project — Performance Evaluation Script
Measures cold start vs. warm Lambda invocation latency.

Usage:
  pip install requests
  python test_performance.py

Replace BASE_URL with your actual API Gateway endpoint before running.
"""

import requests
import time
import statistics
import json

# Replace with your actual API Gateway URL
BASE_URL = "https://zvdd1g4bbl.execute-api.us-east-2.amazonaws.com/prod"
SHORTEN_URL = f"{BASE_URL}/shorten"

TEST_URL = "https://www.example.com/a-very-long-path/that-needs-shortening"
NUM_REQUESTS = 20
DELAY_BETWEEN = 0.2  # seconds between requests


def run_performance_test():
    latencies = []
    results = []

    print(f"Running {NUM_REQUESTS} sequential requests to {SHORTEN_URL}\n")
    print(f"{'Request':<10} {'Latency (ms)':<15} {'Status':<10} {'Note'}")
    print("-" * 55)

    for i in range(1, NUM_REQUESTS + 1):
        start = time.time()
        try:
            r = requests.post(
                SHORTEN_URL,
                json={"url": TEST_URL},
                timeout=10
            )
            elapsed_ms = (time.time() - start) * 1000
            status = r.status_code
        except requests.RequestException as e:
            elapsed_ms = (time.time() - start) * 1000
            status = "ERR"

        latencies.append(elapsed_ms)
        note = "← COLD START" if i == 1 else ""
        print(f"{i:<10} {elapsed_ms:<15.2f} {str(status):<10} {note}")
        results.append({"request": i, "latency_ms": round(elapsed_ms, 2), "status": status})
        time.sleep(DELAY_BETWEEN)

    print("\n" + "=" * 55)
    print("RESULTS SUMMARY")
    print("=" * 55)
    print(f"  Cold Start (request 1):  {latencies[0]:.2f} ms")
    warm = latencies[1:]
    print(f"  Warm Average (2–{NUM_REQUESTS}):    {statistics.mean(warm):.2f} ms")
    print(f"  Warm Median:             {statistics.median(warm):.2f} ms")
    print(f"  Warm Min:                {min(warm):.2f} ms")
    print(f"  Warm Max:                {max(warm):.2f} ms")
    print(f"  Warm Std Dev:            {statistics.stdev(warm):.2f} ms")
    print(f"\n  Cold/Warm Speedup:       {latencies[0] / statistics.mean(warm):.1f}x faster when warm")

    # Save raw data for reporting
    with open("performance_results.json", "w") as f:
        json.dump({
            "cold_start_ms": round(latencies[0], 2),
            "warm_average_ms": round(statistics.mean(warm), 2),
            "warm_median_ms": round(statistics.median(warm), 2),
            "warm_min_ms": round(min(warm), 2),
            "warm_max_ms": round(max(warm), 2),
            "all_latencies": [round(l, 2) for l in latencies]
        }, f, indent=2)
    print("\n  Full results saved to: performance_results.json")


if __name__ == "__main__":
    run_performance_test()
