from uuid import UUID

import asyncpg

from ..schemas.ticket import TicketAnalysis, TicketClosure, TicketEntry

POOL = asyncpg.Pool
RECORD = asyncpg.Record


async def insert_ticket(
    pool: POOL, ticket_data: TicketEntry, llm_response: TicketAnalysis
) -> RECORD:
    """inserts a new ticket and returns the record"""

    query = """
        INSERT INTO tickets (
            email,
            description,
            subject,
            category,
            nature_of_case,
            urgency,
            urgency_reason
        )
        VALUES (
            $1, $2, $3, $4, $5, $6, $7
        )
        RETURNING
            id,
            email,
            description,
            subject,
            category,
            nature_of_case,
            urgency,
            urgency_reason,
            status,
            created_at,
            updated_at;
    """

    async with pool.acquire() as connection:
        record = await connection.fetchrow(
            query,
            ticket_data.email,
            ticket_data.description,
            llm_response.subject,
            llm_response.category,
            llm_response.nature_of_case,
            llm_response.urgency,
            llm_response.urgency_reason,
        )

        return record


async def fetch_all_tickets(pool: POOL) -> list[RECORD]:
    """fetch all tickets, ordered by urgency"""

    query = """
        SELECT * FROM tickets
        WHERE status = 'open'
        ORDER BY
            CASE urgency
                WHEN 'critical' THEN 1
                WHEN 'high' THEN 2
                WHEN 'medium' THEN 3
                WHEN 'low' THEN 4
            END;
    """

    async with pool.acquire() as connection:
        records = await connection.fetch(query)

        return records


async def fetch_ticket(pool: POOL, ticket_id: UUID) -> RECORD | None:
    """fetches a single ticket by its id. returns None if not found"""

    query = """
        SELECT * FROM tickets
        WHERE id = $1;
    """

    async with pool.acquire() as connection:
        record = await connection.fetchrow(query, ticket_id)

        return record


async def modify_ticket_status(
    pool: POOL, ticket_id: UUID, new_data: TicketClosure
) -> RECORD | None:
    """modifies a ticket status and returns the updated ticket record. returns None if ticket to be modified not found"""

    query = """
        UPDATE tickets
        SET status = COALESCE($1, status)
        WHERE id = $2
        RETURNING
            id,
            email,
            description,
            subject,
            category,
            nature_of_case,
            urgency,
            urgency_reason,
            status,
            created_at,
            updated_at;
    """

    status = dict(new_data)

    async with pool.acquire() as connection:
        record = await connection.fetchrow(
            query,
            status.get("status"),
            ticket_id,
        )

        return record
