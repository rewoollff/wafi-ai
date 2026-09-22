# Wafi AI — IT Helpdesk Ticket Triage

Wafi is a lightweight AI service that classifies IT helpdesk tickets into a support team and urgency level.

## Decision

* **Team:** hardware, software, or network
* **Urgency:** low, medium, or urgent

A full service outage is always treated as **urgent** through a deterministic business rule.

## Architecture

```text
API → Service → Model Adapter
          ↓
       Domain
```

The model is hidden behind a `Protocol`, allowing the implementation to be replaced without changing the service layer.

## Requirements

* Python 3.13+
* Docker Desktop

## Run locally

Create and activate a virtual environment:

```bash
python -m venv .venv
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the API:

```bash
uvicorn wafi.api.main:app --host 0.0.0.0 --port 8000
```

## Run with Docker Compose

```bash
docker compose up -d --build
```

Check readiness:

```text
GET http://localhost:8000/ready
```

Stop the services:

```bash
docker compose down
```

## API

### Health

```text
GET /health
```

Returns the liveness status.

### Readiness

```text
GET /ready
```

Returns ready only after the model has been loaded and warmed up.

### Predict

```text
POST /v1/predict
```

Example:

```json
{
  "ticket_text": "The entire department cannot access the system",
  "affected_users": 50,
  "category": "system"
}
```

Example response:

```json
{
  "status": "success",
  "trace_id": "example-trace-id",
  "data": {
    "team": "software",
    "urgency": "urgent"
  }
}
```

### Batch prediction

```text
POST /v1/predict/batch
```

Accepts multiple tickets in one request.

## Validation

Requests reject:

* unknown fields
* missing required fields
* invalid ranges
* invalid ticket data

Validation errors use the same response envelope and include a trace ID.

## Testing

Run the test suite:

```bash
pytest -q
```

Run tests with coverage:

```bash
pytest -q --cov=src/wafi --cov-report=term-missing
```

Run lint and type checks:

```bash
ruff check src tests
mypy src
lint-imports
```

## Docker image

The application uses a multi-stage Docker build, runs as a non-root user, and exposes a `/ready` healthcheck.

The Docker Compose setup includes Redis as a supporting service and starts Wafi only after Redis reports healthy.

## Project structure

```text
src/wafi/
├── api/
├── domain/
├── service/
├── adapters/
└── config.py

tests/
models/
docs/
```

## Demo flow

1. Start the application with Docker Compose.
2. Check `/ready`.
3. Send a valid ticket to `/v1/predict`.
4. Send a malformed request and verify the validation error envelope.
5. Send a full-outage ticket and verify that urgency is `urgent`.
6. Run the test and coverage commands.

## Engineering documents

* `BENCHMARKS.md` — measured performance and resource results.
* `DECISIONS.md` — key engineering decisions and rationale.
