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
import json
import random
from datetime import datetime, timedelta
from pathlib import Path

from faker import Faker

fake = Faker()

# ── time helpers ──────────────────────────────────────────────────────────────


def rand_time(start: datetime, end: datetime) -> datetime:
    span = int((end - start).total_seconds())
    return start + timedelta(seconds=random.randint(0, span))


def weighted_choice(options: dict):
    keys, weights = zip(*options.items())
    return random.choices(keys, weights=weights, k=1)[0]


# ── normal traffic ────────────────────────────────────────────────────────────


def normal_apache(n: int, start: datetime, end: datetime) -> list[dict]:
    endpoints = {
        "/": 20,
        "/index.html": 15,
        "/about": 10,
        "/products": 12,
        "/contact": 8,
        "/login": 10,
        "/api/v1/status": 7,
        "/static/main.css": 10,
        "/static/app.js": 8,
    }
    status_codes = {200: 75, 304: 10, 301: 5, 404: 7, 403: 3}
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15",
    ]

    rows = []
    for _ in range(n):
        rows.append(
            {
                "timestamp": rand_time(start, end).isoformat(),
                "event_type": "http_request",
                "src_ip": fake.ipv4_public(),
                "method": weighted_choice(
                    {"GET": 80, "POST": 15, "PUT": 3, "DELETE": 2}
                ),
                "endpoint": weighted_choice(endpoints),
                "status_code": weighted_choice(status_codes),
                "bytes_sent": random.randint(200, 15_000),
                "response_time_ms": random.randint(50, 800),
                "user_agent": random.choice(user_agents),
                "label": "normal",
            }
        )
    return rows


# ── anomaly: brute-force ssh ──────────────────────────────────────────────────


def brute_force_ssh(n: int, start: datetime) -> list[dict]:
    """
    Carves `n` total events across a pool of attacker IPs.
    Each attacker fires tight sequential bursts — mirrors Hydra/Medusa behaviour.
    """
    common_users = [
        "root",
        "admin",
        "ubuntu",
        "ec2-user",
        "pi",
        "test",
        "guest",
        "oracle",
    ]
    target_ip = "192.168.1.10"

    # Distribute n events across 2–4 attacker IPs
    n_attackers = min(random.randint(2, 4), n)
    budget = _split_budget(n, n_attackers)

    rows = []
    for attempts in budget:
        attacker_ip = fake.ipv4_public()
        current_ts = start + timedelta(seconds=random.randint(0, 180))

        for i in range(attempts):
            success = (i == attempts - 1) and random.random() < 0.2
            rows.append(
                {
                    "timestamp": current_ts.isoformat(),
                    "event_type": "ssh_auth",
                    "src_ip": attacker_ip,
                    "dst_ip": target_ip,
                    "port": 22,
                    "protocol": "TCP",
                    "username": random.choice(common_users),
                    "auth_success": success,
                    "bytes_sent": random.randint(40, 120),
                    "response_time_ms": random.randint(20, 200),
                    "label": "brute_force_ssh",
                }
            )
            current_ts += timedelta(milliseconds=random.randint(100, 600))

    return rows


# ── anomaly: directory traversal ──────────────────────────────────────────────


def directory_traversal(n: int, start: datetime, end: datetime) -> list[dict]:
    """
    Simulates an attacker probing for sensitive files via path traversal.
    Patterns include classic ../ sequences and known sensitive paths.
    One source IP, many rapid requests — similar timing profile to brute force
    but on HTTP instead of SSH.
    """
    traversal_paths = [
        "/../../../etc/passwd",
        "/../../../etc/shadow",
        "/../../../windows/system32/config/sam",
        "/../../../proc/self/environ",
        "/.git/config",
        "/.env",
        "/wp-config.php",
        "/admin/config.php",
        "/../../../var/log/auth.log",
        "/../../../../boot.ini",
        "/%2e%2e%2f%2e%2e%2fetc%2fpasswd",  # URL-encoded variant
        "/..%2F..%2F..%2Fetc%2Fpasswd",
    ]

    attacker_ip = fake.ipv4_public()
    current_ts = rand_time(start, end)

    rows = []
    for _ in range(n):
        # Server correctly rejects most — 400/403/404, occasionally 200 (misconfigured server)
        status = weighted_choice({400: 40, 403: 35, 404: 20, 200: 5})
        rows.append(
            {
                "timestamp": current_ts.isoformat(),
                "event_type": "http_request",
                "src_ip": attacker_ip,
                "method": "GET",
                "endpoint": random.choice(traversal_paths),
                "status_code": status,
                "bytes_sent": random.randint(100, 500),
                "response_time_ms": random.randint(10, 100),
                "user_agent": "curl/7.88.1",  # scanners rarely fake UA convincingly
                "label": "directory_traversal",
            }
        )
        current_ts += timedelta(milliseconds=random.randint(80, 400))

    return rows


# ── anomaly: data exfiltration ────────────────────────────────────────────────


def data_exfiltration(n: int, start: datetime) -> list[dict]:
    """
    Models a compromised internal host slowly beaconing data outward.
    Key signals: large bytes_sent, consistent destination, low-but-steady frequency,
    odd hours (not business hours), and POST/PUT methods carrying payload.
    This is harder to detect than brute force — it's designed to blend in.
    """
    internal_src = f"192.168.1.{random.randint(50, 200)}"
    c2_server = fake.ipv4_public()  # command-and-control destination
    # Exfil often uses legitimate-looking ports to bypass egress filtering
    egress_port = random.choice([80, 443, 8080, 53])
    current_ts = start + timedelta(hours=random.randint(0, 2))  # starts early morning

    rows = []
    for _ in range(n):
        rows.append(
            {
                "timestamp": current_ts.isoformat(),
                "event_type": "outbound_transfer",
                "src_ip": internal_src,
                "dst_ip": c2_server,
                "port": egress_port,
                "protocol": "TCP",
                "method": random.choice(["POST", "PUT"]),
                "endpoint": random.choice(
                    ["/update", "/api/sync", "/metrics", "/beacon"]
                ),
                "status_code": 200,
                "bytes_sent": random.randint(
                    50_000, 500_000
                ),  # large payloads — flag this
                "response_time_ms": random.randint(200, 2_000),
                "user_agent": "python-requests/2.31.0",
                "label": "data_exfiltration",
            }
        )
        # Slow drip — every 3 to 10 minutes. Designed to stay under rate-limit thresholds.
        current_ts += timedelta(seconds=random.randint(180, 600))

    return rows


# ── budget splitter ───────────────────────────────────────────────────────────


def _split_budget(total: int, buckets: int) -> list[int]:
    """Randomly distributes `total` across `buckets`, each getting at least 1."""
    cuts = sorted(random.sample(range(1, total), buckets - 1))
    boundaries = [0] + cuts + [total]
    return [boundaries[i + 1] - boundaries[i] for i in range(buckets)]


# ── anomaly dispatcher ────────────────────────────────────────────────────────

# Registry maps label → generator function signature
# Each function receives (n, start, [end]) — end is optional for time-anchored attacks
ANOMALY_GENERATORS = {
    "brute_force_ssh": lambda n, s, e: brute_force_ssh(n, s),
    "directory_traversal": lambda n, s, e: directory_traversal(n, s, e),
    "data_exfiltration": lambda n, s, e: data_exfiltration(n, s),
}

ANOMALY_WEIGHTS = {
    "brute_force_ssh": 40,
    "directory_traversal": 35,
    "data_exfiltration": 25,
}


def sample_anomalies(n: int, start: datetime, end: datetime) -> list[dict]:
    """
    Distributes `n` anomalous events across attack types using ANOMALY_WEIGHTS.
    Each type gets a proportional slice of the budget.
    """
    types = list(ANOMALY_WEIGHTS.keys())
    weights = list(ANOMALY_WEIGHTS.values())
    counts = random.choices(types, weights=weights, k=n)

    # Tally how many of each type we need
    from collections import Counter

    budget = Counter(counts)

    rows = []
    for attack_type, count in budget.items():
        generator = ANOMALY_GENERATORS[attack_type]
        rows.extend(generator(count, start, end))
    return rows


# ── writer ────────────────────────────────────────────────────────────────────


def write_log(records: list[dict], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record) + "\n")


# ── entrypoint ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate synthetic security log data for ML training and SIEM testing."
    )
    parser.add_argument(
        "--entries",
        type=int,
        default=10_000,
        help="Total number of log entries to generate.",
    )
    parser.add_argument(
        "--anomaly-rate",
        type=float,
        default=0.05,
        help="Fraction of entries that are anomalous (0.0–1.0).",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="analytics/data/sample_logs/synthetic.log",
        help="Output file path (.log, JSONL format).",
    )
    parser.add_argument(
        "--seed", type=int, default=None, help="Random seed for reproducibility."
    )
    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)
        Faker.seed(args.seed)

    # Validate anomaly rate
    if not 0.0 <= args.anomaly_rate <= 1.0:
        raise ValueError(
            f"--anomaly-rate must be between 0 and 1, got {args.anomaly_rate}"
        )

    # Time window: simulate a full 24-hour day
    day_start = datetime(2024, 6, 1, 0, 0, 0)
    day_end = datetime(2024, 6, 1, 23, 59, 59)

    n_anomalous = int(args.entries * args.anomaly_rate)
    n_normal = args.entries - n_anomalous

    print(
        f"[*] Generating {n_normal:,} normal records and {n_anomalous:,} anomalous records..."
    )

    normal_records = normal_apache(n_normal, day_start, day_end)
    anomalous_records = sample_anomalies(n_anomalous, day_start, day_end)

    # Merge and sort chronologically — realistic interleaving of events
    all_records = normal_records + anomalous_records
    all_records.sort(key=lambda r: r["timestamp"])

    output_path = Path(args.output)
    write_log(all_records, output_path)

    # Summary
    from collections import Counter

    label_counts = Counter(r["label"] for r in all_records)
    print(f"[+] Written {len(all_records):,} records to {output_path}")
    print("[+] Label distribution:")
    for label, count in sorted(label_counts.items()):
        pct = count / len(all_records) * 100
        print(f"    {label:<25} {count:>6,}  ({pct:.1f}%)")
