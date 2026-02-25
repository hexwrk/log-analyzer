# SecureFlow API Reference

Base URL: `http://localhost:8000/api/v1`
Auth: All endpoints (except `/health`) require `X-API-Key` header.

---

## POST /logs/ingest

Ingest a batch of raw log entries for processing.

**Request Body**
```json
{
  "format": "apache_clf | auth_log | json",
  "entries": [
    "192.168.1.1 - - [25/Feb/2025:10:23:01 +0000] \"GET /admin HTTP/1.1\" 403 512"
  ]
}
```

**Response 200**
```json
{
  "processed": 1,
  "anomalies_detected": 0,
  "alerts_generated": 0,
  "processing_time_ms": 47
}
```

---

## GET /anomalies

Returns paginated list of detected anomalies.

**Query Params**: `page`, `per_page`, `severity`, `from_ts`, `to_ts`

---

## GET /anomalies/{id}

Full detail for a single anomaly including feature values and triggered rules.

---

## GET /health

No auth required. Returns service status and model load state.
