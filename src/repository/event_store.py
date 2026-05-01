from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError

from src.repository.database import SessionLocal
from src.repository.models import ProcessedEvent


class EventStore:
    """Synchronous idempotency store"""

    def is_already_processed(self, event_id: str) -> bool:
        with SessionLocal() as session:
            result = session.execute(
                select(ProcessedEvent).where(ProcessedEvent.event_id == event_id)
            )
            event = result.scalar_one_or_none()
            return event is not None and event.status == "COMPLETED"

    def mark_in_progress(self, event_id: str, order_id: str):
        with SessionLocal() as session:
            event = ProcessedEvent(
                event_id=event_id, order_id=order_id, status="IN_PROGRESS"
            )
            session.add(event)
            try:
                session.commit()
            except IntegrityError:
                session.rollback()

    def mark_completed(self, event_id: str):
        with SessionLocal() as session:
            session.execute(
                update(ProcessedEvent)
                .where(ProcessedEvent.event_id == event_id)
                .values(status="COMPLETED", processed_at=datetime.utcnow())
            )
            session.commit()

    def mark_failed(self, event_id: str, error_message: str = None):
        with SessionLocal() as session:
            session.execute(
                update(ProcessedEvent)
                .where(ProcessedEvent.event_id == event_id)
                .values(status="FAILED", error_message=error_message)
            )
            session.commit()
