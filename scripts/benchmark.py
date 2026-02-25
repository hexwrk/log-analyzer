"""
Throughput and latency benchmarks.

Measures:
  - Log parsing: entries/second
  - Feature extraction: entries/second
  - End-to-end ingest API: requests/second, p50/p95/p99 latency
  - Anomaly detection: batch scoring throughput

Results printed to stdout and optionally written to docs/benchmark_results.json.
Build target: Month 4 — run this to get real numbers for your README.

Usage:
    python scripts/benchmark.py --entries 50000
"""
# TODO Month 4
