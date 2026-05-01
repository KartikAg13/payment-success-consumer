from celery import shared_task
from pydantic import ValidationError

from src.models.event import PaymentSuccessEvent
from src.services.payment_success_handler import PaymentSuccessHandler
from src.utils.logger import logger


@shared_task(
    name="consume_payment_success", bind=True, max_retries=5, default_retry_delay=30
)
def consume_payment_success(self, event_data: dict):
    try:
        logger.info(
            "Received PaymentSuccess event",
            event_id=event_data.get("event_id"),
            order_id=event_data.get("order_id"),
        )

        event = PaymentSuccessEvent.model_validate(event_data)

        handler = PaymentSuccessHandler()
        handler.process(event)

        logger.info(
            "PaymentSuccess event processed successfully",
            event_id=event.event_id,
            order_id=event.order_id,
        )

    except ValidationError as e:
        logger.error("Invalid event payload - rejecting", errors=e.errors())
        return
    except Exception as e:
        logger.error("Task failed, retrying...", error=str(e))
        raise self.retry(exc=e, countdown=30 * (2 ** min(self.request.retries, 4)))
