# SecureFlow — Threat Intelligence Dashboard

> Real-time log anomaly detection engine with ML backend and interactive SOC dashboard.

[![Python](https://img.shields.io/badge/Python-3.11+-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green)](https://fastapi.tiangolo.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-In%20Development-orange)](.)

---

## Problem

Security teams process hundreds of thousands of log events daily with no automated triage layer. Manual review at scale is operationally unsustainable — anomalous behavior patterns get buried in noise, and high-severity events surface hours after they should.

SecureFlow addresses this by building an automated pipeline that ingests raw logs, extracts behavioral features, and applies unsupervised ML to surface outliers before a human analyst ever needs to look.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         SecureFlow System                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Log Sources          Ingestion Layer        Processing Core        │
│  ─────────────        ──────────────         ───────────────        │
│  Apache logs    ──►   POST /ingest    ──►    log_parser.py          │
│  auth.log       ──►   Rate limiter    ──►    feature_engineer.py    │
│  syslog         ──►   API key auth    ──►    anomaly_detector.py    │
│  JSON events    ──►                   ──►    threat_classifier.py   │
│                                              ↓                      │
│  Storage Layer        API Layer         Alert Engine                │
│  ─────────────        ─────────         ────────────                │
│  PostgreSQL     ◄──   FastAPI    ◄──    alert_manager.py            │
│  (ORM models)         REST API          Severity scoring            │
│                        ↓                                            │
│  Frontend                                                           │
│  ────────                                                           │
│  React Dashboard ◄── Axios polling ◄── GET /anomalies              │
│  Chart.js viz         useAnomalies()    GET /alerts                 │
│  GeoIP map            WebSocket (v2)                                │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

  ML Pipeline (Offline Training → Online Inference)
  ──────────────────────────────────────────────────
  Raw Logs → Feature Matrix → IsolationForest.fit() → .pkl artifact
                                    ↓
             Production: IsolationForest.predict() per ingested batch
```

---

## What This Does

- **Ingests** Apache access logs, Linux auth logs, and structured JSON events via REST API
- **Parses and normalizes** heterogeneous log formats into a unified feature space
- **Detects anomalies** using Isolation Forest — an unsupervised algorithm suited to high-dimensional security telemetry with no labeled attack data required
- **Classifies threats** via a rule-based layer on top of ML scores (brute force, port scan patterns, geo-anomalies)
- **Exposes findings** through a typed REST API consumed by a React SOC dashboard

---

## Performance Targets

> ⚠️ Numbers below are planning targets. Actual benchmarks will be recorded in `scripts/benchmark.py` and updated here post-implementation.

| Metric | Target |
|---|---|
| Log throughput | 10,000 entries / ~2.3s |
| API response time (p95) | < 120ms |
| Anomaly detection precision | ≥ 89% |
| Anomaly detection recall | ≥ 84% |
| F1 score on test set | ≥ 0.87 |
| Rule-based classifier accuracy | ~92% on labeled samples |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11, FastAPI, SQLAlchemy 2.0 |
| ML | scikit-learn (IsolationForest), Pandas, NumPy |
| Database | PostgreSQL 16 |
| Frontend | React 18, Chart.js, Axios |
| Auth | API key middleware, rate limiting (slowapi) |
| Deployment | Docker, docker-compose, Nginx |
| Testing | pytest, pytest-asyncio, factory-boy |

---

## Quick Start

```bash
git clone https://github.com/hexwrk/secureflow
cd secureflow

# Environment setup
cp .env.example .env
# Edit .env with your credentials

# Run with Docker (recommended)
docker-compose up --build

# Or run backend locally
pip install -r requirements.txt
uvicorn backend.main:app --reload

# Access
# API docs:   http://localhost:8000/docs
# Dashboard:  http://localhost:3000
```

---

## Project Structure

See full structure in [`docs/architecture.md`](docs/architecture.md).

---

## Security Considerations

- All log ingestion requires API key authentication
- Rate limiting on ingest endpoint (configurable, default 60 req/min)
- Input validation via Pydantic schemas — no raw SQL, ORM only
- `.env` never committed — secrets via environment injection
- Threat model documented in [`docs/threat_model.md`](docs/threat_model.md)

---

## Development Roadmap

| Month | Focus | Deliverable |
|---|---|---|
| 1 | Core ML pipeline | Log parser + IsolationForest + notebooks |
| 2 | API + data layer | FastAPI routes + PostgreSQL ORM |
| 3 | Frontend | React dashboard + deployment |
| 4 | Production hardening | Docker + benchmarks + threat model |

---

## Author

**hexwrk** — BSc IT | Cybersecurity & Data Analytics  
Built as a flagship portfolio project demonstrating full-stack security engineering.
