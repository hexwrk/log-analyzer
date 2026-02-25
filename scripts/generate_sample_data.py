"""
Synthetic log generator — produces realistic log data for testing and model training.

Usage:
    python scripts/generate_sample_data.py --entries 10000 --anomaly-rate 0.05

Generates a mix of normal and anomalous patterns:
  - Legitimate browsing traffic (normal)
  - Brute force SSH attempts (anomalous)
  - Directory traversal scans (anomalous)
  - Data exfiltration pattern (anomalous)

Build target: Month 1 — you need data before you can train anything.
"""
import argparse
import random
from datetime import datetime, timedelta
from pathlib import Path

# TODO Month 1: Implement generator
# Hint: Build separate generators for normal_apache(), brute_force_ssh(),
#       scanner_pattern(), and sample from them at the configured anomaly_rate.

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--entries", type=int, default=10000)
    parser.add_argument("--anomaly-rate", type=float, default=0.05)
    parser.add_argument("--output", type=str, default="analytics/data/sample_logs/synthetic.log")
    args = parser.parse_args()
    print(f"[TODO] Generate {args.entries} entries with {args.anomaly_rate:.0%} anomaly rate")
