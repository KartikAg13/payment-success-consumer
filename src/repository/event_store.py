from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError

from src.repository.database import AsyncSessionLocal
from src.repository.models import ProcessedEvent


class EventStore:
    """Idempotency store"""

    async def is_already_processed(self, event_id: str) -> bool:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(ProcessedEvent).where(ProcessedEvent.event_id == event_id)
            )
            event = result.scalar_one_or_none()
            return event is not None and event.status == "COMPLETED"

    async def mark_in_progress(self, event_id: str, order_id: str):
        async with AsyncSessionLocal() as session:
            event = ProcessedEvent(
                event_id=event_id, order_id=order_id, status="IN_PROGRESS"
            )
            session.add(event)
            try:
                await session.commit()
            except IntegrityError:
                await session.rollback()  # already exists

    async def mark_completed(self, event_id: str):
        async with AsyncSessionLocal() as session:
            await session.execute(
                update(ProcessedEvent)
                .where(ProcessedEvent.event_id == event_id)
                .values(status="COMPLETED", processed_at=datetime.utcnow())
            )
            await session.commit()

    async def mark_failed(self, event_id: str, error_message: str = None):
        async with AsyncSessionLocal() as session:
            await session.execute(
                update(ProcessedEvent)
                .where(ProcessedEvent.event_id == event_id)
                .values(status="FAILED", error_message=error_message)
            )
            await session.commit()
