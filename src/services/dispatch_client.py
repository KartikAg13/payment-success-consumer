from src.models.event import PaymentSuccessEvent
from src.utils.logger import logger


class DispatchClient:
    """Adapter to trigger Dispatch Service"""

    def trigger_rider_assignment(self, event: PaymentSuccessEvent):
        logger.info(
            "→ Sending StartRiderAssignment command to Dispatch",
            order_id=event.order_id,
        )
        print(f"[DISPATCH] Rider assignment started for order {event.order_id}")
