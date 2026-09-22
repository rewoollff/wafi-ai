from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from wafi.adapters.model import SklearnTriageModel
from wafi.api.main import app
from wafi.domain.decision import Team, Urgency
from wafi.domain.models import Ticket
from wafi.service.triage import TriageService


class FakeModel:
    def predict(self, ticket):
        return type(
            "Decision",
            (),
            {
                "team": Team.NETWORK,
                "urgency": Urgency.URGENT,
            },
        )()


def test_triage_service_returns_model_decision():
    service = TriageService(FakeModel())

    ticket = Ticket(
        ticket_text="The network is down",
        affected_users=100,
        category="network",
    )

    decision = service.predict(ticket)

    assert decision.team == Team.NETWORK
    assert decision.urgency == Urgency.URGENT


def test_full_service_outage_is_urgent():
    model_path = Path("models/wafi_model.joblib")
    model = SklearnTriageModel(model_path)
    service = TriageService(model)

    ticket = Ticket(
        ticket_text="Full service outage affecting all users",
        affected_users=500,
        category="software",
    )

    decision = service.predict(ticket)

    assert decision.urgency == Urgency.URGENT


def test_ticket_validation_rejects_invalid_users():
    with pytest.raises(ValueError):
        Ticket(
            ticket_text="Network issue",
            affected_users=0,
            category="network",
        )


def test_ticket_validation_rejects_unknown_fields():
    with pytest.raises(ValueError):
        Ticket(
            ticket_text="Network issue",
            affected_users=5,
            category="network",
            extra_field="not allowed",
        )


def test_sklearn_model_predicts():
    model_path = Path("models/wafi_model.joblib")
    model = SklearnTriageModel(model_path)

    ticket = Ticket(
        ticket_text="My laptop will not turn on",
        affected_users=1,
        category="hardware",
    )

    decision = model.predict(ticket)

    assert decision.team in Team
    assert decision.urgency in Urgency


def test_health_endpoint():
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "success"
    assert "trace_id" in body
    assert body["data"]["status"] == "ok"


def test_ready_endpoint():
    with TestClient(app) as client:
        response = client.get("/ready")

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "success"
    assert "trace_id" in body
    assert body["data"]["status"] == "ready"


def test_predict_endpoint():
    with TestClient(app) as client:
        response = client.post(
            "/v1/predict",
            json={
                "ticket_text": "My laptop will not turn on",
                "affected_users": 1,
                "category": "hardware",
            },
        )

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "success"
    assert "trace_id" in body
    assert "team" in body["data"]
    assert "urgency" in body["data"]

    
def test_golden_network_outage_is_urgent():
    model = SklearnTriageModel(Path("models/wafi_model.joblib"))
    service = TriageService(model)

    ticket = Ticket(
        ticket_text="Network is unavailable for the whole department",
        affected_users=50,
        category="network",
    )

    decision = service.predict(ticket)

    assert decision.team == Team.NETWORK
    assert decision.urgency == Urgency.URGENT


def test_invariance_outage_case_does_not_change_urgency():
    model = SklearnTriageModel(Path("models/wafi_model.joblib"))
    service = TriageService(model)

    ticket_lower = Ticket(
        ticket_text="full service outage affecting all users",
        affected_users=500,
        category="software",
    )

    ticket_upper = Ticket(
        ticket_text="FULL SERVICE OUTAGE AFFECTING ALL USERS",
        affected_users=500,
        category="software",
    )

    decision_lower = service.predict(ticket_lower)
    decision_upper = service.predict(ticket_upper)

    assert decision_lower.urgency == decision_upper.urgency


def test_directional_more_affected_users_does_not_reduce_urgency():
    model = SklearnTriageModel(Path("models/wafi_model.joblib"))
    service = TriageService(model)

    small = Ticket(
        ticket_text="The application is slow",
        affected_users=1,
        category="software",
    )

    large = Ticket(
        ticket_text="The application is slow",
        affected_users=100,
        category="software",
    )

    small_decision = service.predict(small)
    large_decision = service.predict(large)

    urgency_rank = {
        Urgency.LOW: 1,
        Urgency.MEDIUM: 2,
        Urgency.URGENT: 3,
    }

    assert urgency_rank[large_decision.urgency] >= urgency_rank[
        small_decision.urgency
    ]