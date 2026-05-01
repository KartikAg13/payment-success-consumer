from src.models.event import PaymentSuccessEvent
from src.utils.logger import logger


class RestaurantClient:
    """Adapter to trigger Restaurant Service"""

    def trigger_preparation(self, event: PaymentSuccessEvent):
        logger.info(
            "→ Sending PrepareOrder command to Restaurant",
            order_id=event.order_id,
            amount=event.amount,
        )
        print(f"[RESTAURANT] Preparation started for order {event.order_id}")
