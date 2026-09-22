from pathlib import Path

import joblib

from wafi.domain.decision import Team, TriageDecision, Urgency
from wafi.domain.models import Ticket


class SklearnTriageModel:
    def __init__(self, model_path: Path):
        self._model = joblib.load(model_path)

    def predict(self, ticket: Ticket) -> TriageDecision:
        text = (
            f"{ticket.ticket_text} "
            f"affected users {ticket.affected_users} "
            f"category {ticket.category}"
        )

        prediction = self._model.predict([text])[0]
        team, urgency = prediction.split("|")

        return TriageDecision(
            team=Team(team),
            urgency=Urgency(urgency),
        )