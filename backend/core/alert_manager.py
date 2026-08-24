"""
Alert Manager — Converts classified anomalies into structured Alert objects.

Severity mapping:
  CRITICAL  — BRUTE_FORCE + successful auth within 5min window
  HIGH      — BRUTE_FORCE or DATA_EXFIL or PATH_TRAVERSAL
  MEDIUM    — PORT_SCAN or SCANNER
  LOW       — Isolated anomaly score, no rule match

Deduplication: same source IP + same rule within 10min = single alert.

Build target: Month 1 (basic version) → Month 2 (DB persistence).
"""

# TODO Month 1/2
