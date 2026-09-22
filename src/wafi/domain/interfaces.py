from typing import Protocol

from wafi.domain.decision import TriageDecision
from wafi.domain.models import Ticket


class TriageModel(Protocol):
    def predict(self, ticket: Ticket) -> TriageDecision:
        ...