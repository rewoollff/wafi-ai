from wafi.domain.decision import TriageDecision, Urgency
from wafi.domain.interfaces import TriageModel
from wafi.domain.models import Ticket


class TriageService:
    def __init__(self, model: TriageModel):
        self._model = model

    def predict(self, ticket: Ticket) -> TriageDecision:
        decision = self._model.predict(ticket)

        outage_keywords = (
            "full service outage",
            "entire department cannot access",
            "whole application is down",
            "service is unavailable for everyone",
            "network is unavailable for the whole department",
            "all employees cannot access",
        )

        text = ticket.ticket_text.lower()

        if any(keyword in text for keyword in outage_keywords):
            decision.urgency = Urgency.URGENT

        return decision