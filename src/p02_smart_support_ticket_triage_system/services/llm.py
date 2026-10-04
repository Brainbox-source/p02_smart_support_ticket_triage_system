from ..schemas.ticket import LLMResponse


async def structure_ticket(description: str) -> LLMResponse:
    return LLMResponse(
        subject="Mock subject",
        category="student account management",
        nature_of_case="incident",
        urgency="critical",
        urgency_reason="Mock classification used during development.",
    )
