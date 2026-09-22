from enum import Enum


class Urgency(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    URGENT = "urgent"


class Team(str, Enum):
    HARDWARE = "hardware"
    SOFTWARE = "software"
    NETWORK = "network"


class TriageDecision:
    def __init__(self, team: Team, urgency: Urgency):
        self.team = team
        self.urgency = urgency