from ..schemas.ticket import LLMResponse


async def structure_ticket(description: str) -> LLMResponse:
    return LLMResponse(
        subject="Mock subject",
        category="lms and classroom support",
        nature_of_case="incident",
        urgency="critical",
        urgency_reason="Mock classification used during development.",
    )
