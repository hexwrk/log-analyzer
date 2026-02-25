# SecureFlow — Threat Model

> Status: Planning draft. Will be updated as implementation progresses using findings from TryHackMe SOC Level 1 and HTB labs.

## Scope

This threat model covers the SecureFlow application itself — not the systems whose logs it monitors.

## Assets

| Asset | Sensitivity | Why It Matters |
|---|---|---|
| Ingested log data | HIGH | May contain PII, internal IPs, credentials in URLs |
| API keys | CRITICAL | Full ingest + read access if compromised |
| ML model artifact | MEDIUM | Model inversion could reveal training data patterns |
| PostgreSQL database | HIGH | Contains all parsed logs and anomaly decisions |
| Backend process | HIGH | Compromise = visibility into all monitored systems |

## Threat Actors

**External attacker** — wants to poison the log ingestion pipeline or exfiltrate log data.
**Malicious insider** — has API key, wants to suppress detection of their own activity.
**Automated scanner** — hammers the ingest endpoint to cause DoS.

## Attack Surface Analysis

### Ingest Endpoint (`POST /ingest`)
- **Threat**: Log injection / prompt injection if logs are ever rendered as HTML
- **Control**: Pydantic input validation, parameterized ORM queries, output encoding in frontend
- **Threat**: DoS via high-volume ingestion
- **Control**: Rate limiting (60 req/min default), request size cap

### API Authentication
- **Threat**: API key brute force
- **Control**: Rate limiting + key length (256-bit entropy minimum)
- **Threat**: Key leakage via logs
- **Control**: Keys never logged; masked in error output

### ML Model
- **Threat**: Adversarial log crafting to evade IsolationForest detection
- **Control**: Rule-based classifier layer as second detection stage; model retrained periodically
- **Threat**: Model file tampering if filesystem is compromised
- **Control**: Model hash verified on load; read-only volume mount in Docker

### Database
- **Threat**: SQL injection
- **Control**: SQLAlchemy ORM — no raw SQL queries anywhere in codebase
- **Threat**: Credential exposure
- **Control**: Connection string via environment variable only, never hardcoded

## Residual Risks (Accepted for MVP)

- No mutual TLS between services (docker internal network)
- No log signing (can't detect tampered historical logs)
- No RBAC (single API key for all operations)

These are documented for future sprints, not ignored.

## References
- OWASP API Security Top 10
- MITRE ATT&CK: Defense Evasion > Indicator Removal
- TryHackMe SOC Level 1 — Log Analysis module
