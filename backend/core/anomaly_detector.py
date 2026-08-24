"""
Anomaly Detector — IsolationForest inference wrapper.

Loads serialized model from disk (path from config).
Exposes score() method: accepts feature DataFrame, returns (score, is_anomaly).

Training happens OFFLINE in analytics/notebooks/03_model_training.ipynb.
This module is inference-only in production.

Build target: Month 1.
"""

# TODO Month 1
