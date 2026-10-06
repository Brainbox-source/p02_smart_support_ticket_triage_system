from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

Category = Literal[
    "lms and classroom support",
    "student account management",
    "enrolment and deferments",
    "examinations and results",
    "fees and finances",
    "document services",
    "student community",
]
NatureOfCase = Literal["incident", "service request", "inquiry", "complaint"]
Urgency = Literal["low", "medium", "high", "critical"]
TicketStatus = Literal["open", "closed"]
TicketClosedStatus = Literal["closed"]


class TicketEntry(BaseModel):
    """what a student sends. only two fields are required"""

    # remove spaces at both ends of the email and description, and reject unknown fields
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    email: EmailStr = Field(max_length=254)
    description: str = Field(min_length=10, max_length=5000)


class TicketAnalysis(BaseModel):
    """what the llm returns; exactly this shape"""

    subject: str = Field(min_length=1, max_length=255)
    category: Category
    nature_of_case: NatureOfCase
    urgency: Urgency
    urgency_reason: str = Field(min_length=1, max_length=255)


class Ticket(BaseModel):
    """the full ticket details"""

    id: UUID
    email: EmailStr
    description: str
    subject: str
    category: Category
    nature_of_case: NatureOfCase
    urgency: Urgency
    urgency_reason: str
    status: TicketStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TicketClosure(BaseModel):
    status: TicketClosedStatus = Field(
        default="closed",
        description="the new status of the ticket, can only be 'closed'.",
    )
