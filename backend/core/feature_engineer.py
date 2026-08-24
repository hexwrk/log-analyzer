"""
Feature Engineer — Transforms ParsedLogEntry objects into numeric feature vectors
suitable for IsolationForest.

Key features to extract:
  - Request rate per source IP (rolling window)
  - Hour-of-day (cyclic sin/cos encoding — NOT raw int)
  - HTTP status code category (2xx/3xx/4xx/5xx)
  - Response body size (normalized)
  - Failed auth count per IP in time window
  - User-agent entropy (detect scripted clients)

Build target: Month 1.
Reference: analytics/notebooks/02_feature_engineering.ipynb
"""

# TODO Month 1
