"""
Threat Classifier — Rule-based classification layer on top of ML anomaly scores.

Rules:
  - BRUTE_FORCE: >10 failed auths from same IP within 60s
  - PORT_SCAN: >5 unique ports accessed from same IP within 30s
  - DATA_EXFIL: response body >1MB outside business hours
  - PATH_TRAVERSAL: ../  or /etc/passwd patterns in URI
  - SCANNER: known bad UA strings or sequential 404 patterns

Build target: Month 1.
"""
# TODO Month 1
