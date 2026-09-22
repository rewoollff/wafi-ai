import json
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from wafi.adapters.model import SklearnTriageModel
from wafi.config import settings
from wafi.domain.models import Ticket
from wafi.service.triage import TriageService


service: TriageService | None = None


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_data: dict[str, str] = {
            "level": record.levelname,
            "message": record.getMessage(),
        }

        trace_id = getattr(record, "trace_id", None)
        if trace_id:
            log_data["trace_id"] = str(trace_id)

        return json.dumps(log_data)


logger = logging.getLogger("wafi")
logger.setLevel(logging.INFO)

handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())

logger.handlers.clear()
logger.addHandler(handler)
logger.propagate = False


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    global service

    model = SklearnTriageModel(settings.model_path)

    warmup_ticket = Ticket(
        ticket_text="warmup test ticket",
        affected_users=1,
        category="software",
    )
    model.predict(warmup_ticket)

    service = TriageService(model)

    logger.info("Wafi service started")

    yield

    service = None

    logger.info("Wafi service stopped")


app = FastAPI(
    title="Wafi AI Ticket Triage",
    lifespan=lifespan,
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    trace_id = str(uuid4())

    logger.warning(
        "Request validation failed",
        extra={"trace_id": trace_id},
    )

    return JSONResponse(
        status_code=422,
        content={
            "status": "error",
            "trace_id": trace_id,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid request data",
            },
        },
    )


@app.get("/health")
def health() -> dict[str, object]:
    trace_id = str(uuid4())

    logger.info(
        "Health check",
        extra={"trace_id": trace_id},
    )

    return {
        "status": "success",
        "trace_id": trace_id,
        "data": {"status": "ok"},
    }


@app.get("/ready", response_model=None)
def ready() -> dict[str, object] | JSONResponse:
    trace_id = str(uuid4())

    if service is None:
        logger.warning(
            "Readiness check failed",
            extra={"trace_id": trace_id},
        )

        return JSONResponse(
            status_code=503,
            content={
                "status": "error",
                "trace_id": trace_id,
                "error": {
                    "code": "NOT_READY",
                    "message": "Service is not ready",
                },
            },
        )

    logger.info(
        "Readiness check",
        extra={"trace_id": trace_id},
    )

    return {
        "status": "success",
        "trace_id": trace_id,
        "data": {"status": "ready"},
    }


@app.post("/v1/predict", response_model=None)
def predict(ticket: Ticket) -> dict[str, object] | JSONResponse:
    trace_id = str(uuid4())

    if service is None:
        logger.warning(
            "Prediction requested while service is not ready",
            extra={"trace_id": trace_id},
        )

        return JSONResponse(
            status_code=503,
            content={
                "status": "error",
                "trace_id": trace_id,
                "error": {
                    "code": "NOT_READY",
                    "message": "Service is not ready",
                },
            },
        )

    decision = service.predict(ticket)

    logger.info(
        "Ticket prediction completed",
        extra={"trace_id": trace_id},
    )

    return {
        "status": "success",
        "trace_id": trace_id,
        "data": {
            "team": decision.team.value,
            "urgency": decision.urgency.value,
        },
    }

