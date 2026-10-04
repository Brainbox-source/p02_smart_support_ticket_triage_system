import logging
from uuid import UUID

import asyncpg
from fastapi import APIRouter, HTTPException, Request, status

from ..db.tickets import fetch_ticket, insert_ticket, modify_ticket_status
from ..errors.llm import InvalidLLMResponseError, LLMUnavailableError
from ..schemas.ticket import LLMResponse, Ticket, TicketClosure, TicketEntry
from ..services.llm import structure_ticket
from .dependencies import get_db_pool

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/tickets", tags=["Tickets"])

POSTGRES_ERROR = asyncpg.PostgresError


@router.post("/", response_model=Ticket, status_code=status.HTTP_201_CREATED)
async def create_ticket(ticket_data: TicketEntry, request: Request):
    """create a ticket"""

    pool = get_db_pool(request)

    try:
        llm_response: LLMResponse = await structure_ticket(ticket_data.description)
    except LLMUnavailableError as error:
        logger.exception("llm unavailable")

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="service unavailable. please try again shortly.",
        ) from error
    except InvalidLLMResponseError as error:
        logger.exception("llm returned invalid output")

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="we could not process your ticket. please try again",
        ) from error

    try:
        record = await insert_ticket(pool, ticket_data, llm_response)

        return dict(record)
    except POSTGRES_ERROR:
        logger.exception("database insert failed")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="we could not store your ticket. please try again.",
        )


@router.get("/{ticket_id}", response_model=Ticket)
async def get_ticket(ticket_id: UUID, request: Request):
    """retrieve a specific ticket by its id"""

    pool = get_db_pool(request)

    try:
        record = await fetch_ticket(pool, ticket_id)

        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="ticket not found"
            )

        return dict(record)
    except POSTGRES_ERROR:
        logger.exception("ticket retrieval failed")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="failed to fetch ticket",
        )


@router.patch("/{ticket_id}", response_model=Ticket)
async def update_ticket_status(
    ticket_id: UUID, new_data: TicketClosure, request: Request
):
    """update a specific ticket status"""

    pool = get_db_pool(request)

    try:
        record = await modify_ticket_status(pool, ticket_id, new_data)

        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="ticket not found"
            )

        return dict(record)
    except POSTGRES_ERROR:
        logger.exception("ticket closure failed")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="failed to close ticket",
        )
