# SecureFlow — System Architecture

## Design Philosophy

Three principles drove every architectural decision here:

1. **Separation of concerns** — parsing, feature extraction, detection, and alerting are distinct modules. Swapping IsolationForest for a neural network should require touching exactly one file.
2. **Fail-safe ingestion** — malformed logs should never crash the pipeline; they get logged and skipped.
3. **Observable behavior** — every detection decision should be explainable (anomaly score, triggered rule, feature values). Black-box outputs are useless to analysts.

---

## Component Breakdown

### Ingestion → `backend/api/routes/logs.py`
Entry point for all log data. Accepts batches of raw log strings or pre-parsed JSON. Validates via Pydantic before anything else touches it. Auth middleware runs first; rate limiter second.

### Parsing → `backend/core/log_parser.py`
Format-specific regex parsers for Apache CLF, Linux auth.log, and generic JSON. Outputs a normalized `ParsedLogEntry` dataclass. New formats = new parser method, nothing else changes.

### Feature Engineering → `backend/core/feature_engineer.py`
Transforms parsed entries into numeric feature vectors:
- Request rate per IP (rolling 5-min window)
- Hour-of-day (cyclic encoding — sin/cos, not raw int)
- Response code category
- Payload size z-score
- Geographic distance from baseline (if IP geolocation available)
- Failed auth attempt count per source IP

### Anomaly Detection → `backend/core/anomaly_detector.py`
Wraps scikit-learn's `IsolationForest`. Inference only in production — model trained offline in `analytics/notebooks/03_model_training.ipynb`. Returns raw anomaly score and boolean flag per log entry.

### Threat Classification → `backend/core/threat_classifier.py`
Rule engine layered on top of ML scores. Catches patterns IsolationForest might miss in low-volume scenarios:
- Brute force: >10 failed auths from same IP in 60s
- Scanner: sequential port access pattern
- Exfil indicator: unusually large outbound response body

### Alert Manager → `backend/core/alert_manager.py`
Converts flagged entries into structured alerts with severity scores (LOW/MEDIUM/HIGH/CRITICAL). Deduplicates repeat offenders within configurable time windows.

---

## Data Flow

```
HTTP POST /ingest
    → Pydantic validation
    → LogParser.parse()
    → FeatureEngineer.extract()
    → AnomalyDetector.score()
    → [if anomalous] ThreatClassifier.classify()
    → AlertManager.generate()
    → Persist to PostgreSQL
    → Return 200 + summary
```

---

## Database Schema (Planning)

```
log_entries       anomalies          alerts
───────────       ─────────          ──────
id (UUID)         id (UUID)          id (UUID)
raw_text          log_entry_id FK    anomaly_id FK
source_ip         anomaly_score      severity
timestamp         is_anomaly         alert_type
log_format        detected_at        triggered_rule
parsed_at         features_json      created_at
                                     acknowledged
```

---

## Scalability Notes (Future)

Current design is single-process synchronous. Paths to scale when needed:
- Replace synchronous ingestion with a Kafka/Redis queue consumer
- Move anomaly detection to a background worker (Celery or ARQ)
- Add read replicas for the dashboard query path
- Cache frequent IP reputation lookups in Redis

None of this is premature optimization for an MVP — document it to show you've thought about it.
