import random

from src.models.event import PaymentSuccessEvent
from src.utils.logger import logger


class DispatchClient:
    """Adapter to trigger Dispatch Service with simulated failures"""

    def trigger_rider_assignment(self, event: PaymentSuccessEvent):
        if random.random() < 0.3:
            logger.error("Dispatch service failed (simulated)", order_id=event.order_id)
            print(f"[DISPATCH] ❌ FAILED (simulated) for order {event.order_id}")
            raise Exception(f"Dispatch service unavailable for order {event.order_id}")

        logger.info(
            "→ Sending StartRiderAssignment command to Dispatch",
            order_id=event.order_id,
        )
        print(f"[DISPATCH] Rider assignment started for order {event.order_id}")
