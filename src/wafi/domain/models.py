from pydantic import BaseModel, ConfigDict, Field


class Ticket(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ticket_text: str = Field(min_length=5, max_length=1000)
    affected_users: int = Field(ge=1, le=10000)
    category: str = Field(min_length=1, max_length=50)