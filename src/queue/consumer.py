from celery import shared_task
from pydantic import ValidationError

from src.models.event import PaymentSuccessEvent
from src.utils.logger import logger


@shared_task(
    name="consume_payment_success", bind=True, max_retries=5, default_retry_delay=30
)
def consume_payment_success(self, event_data: dict):
    """Main entry point for processing PaymentSuccess events"""
    try:
        logger.info(
            "Received PaymentSuccess event",
            event_id=event_data.get("event_id"),
            order_id=event_data.get("order_id"),
        )

        event = PaymentSuccessEvent.model_validate(event_data)

        logger.info(
            "Event validated successfully",
            event_id=event.event_id,
            order_id=event.order_id,
        )

        logger.info(
            "PaymentSuccess event processed (placeholder)",
            event_id=event.event_id,
            order_id=event.order_id,
        )

    except ValidationError as e:
        logger.error(
            "Invalid event payload - rejecting", errors=e.errors(), raw_event=event_data
        )
        return

    except Exception as e:
        logger.error(
            "Unexpected error processing event",
            event_id=event_data.get("event_id"),
            error=str(e),
        )
        raise self.retry(exc=e, countdown=30 * (2 ** min(self.request.retries, 4)))
