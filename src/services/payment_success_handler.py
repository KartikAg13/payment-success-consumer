from src.models.event import PaymentSuccessEvent
from src.models.order_state import OrderState
from src.repository.event_store import EventStore
from src.repository.order_repository import OrderRepository
from src.services.dispatch_client import DispatchClient
from src.services.restaurant_client import RestaurantClient
from src.utils.logger import logger


class PaymentSuccessHandler:
    def __init__(self):
        self.event_store = EventStore()
        self.order_repo = OrderRepository()
        self.restaurant_client = RestaurantClient()
        self.dispatch_client = DispatchClient()

    def process(self, event: PaymentSuccessEvent):
        try:
            # === IDEMPOTENCY CHECK ===
            if self.event_store.is_already_processed(event.event_id):
                logger.info(
                    "Duplicate event detected and skipped",
                    event_id=event.event_id,
                    order_id=event.order_id,
                )
                return

            logger.info(
                "Starting processing of new event",
                event_id=event.event_id,
                order_id=event.order_id,
            )

            # Mark as in progress
            self.event_store.mark_in_progress(event.event_id, event.order_id)
            self.order_repo.update_order_state(
                event.order_id, OrderState.PAYMENT_SUCCESS_RECEIVED
            )

            # Trigger downstream services independently
            rest_ok = self._trigger_restaurant(event)
            disp_ok = self._trigger_dispatch(event)

            if rest_ok and disp_ok:
                self.event_store.mark_completed(event.event_id)
            else:
                self.event_store.mark_failed(event.event_id, "Partial failure occurred")

            logger.info(
                "Processing completed",
                event_id=event.event_id,
                order_id=event.order_id,
                restaurant_ok=rest_ok,
                dispatch_ok=disp_ok,
            )

        except Exception as e:
            logger.error(
                "Critical failure in handler", event_id=event.event_id, error=str(e)
            )
            self.event_store.mark_failed(event.event_id, str(e))
            raise

    def _trigger_restaurant(self, event: PaymentSuccessEvent) -> bool:
        try:
            self.restaurant_client.trigger_preparation(event)
            self.order_repo.update_order_state(
                event.order_id, OrderState.RESTAURANT_TRIGGERED
            )
            return True
        except Exception as e:
            logger.warning(
                "Restaurant trigger failed", order_id=event.order_id, error=str(e)
            )
            return False

    def _trigger_dispatch(self, event: PaymentSuccessEvent) -> bool:
        try:
            self.dispatch_client.trigger_rider_assignment(event)
            self.order_repo.update_order_state(
                event.order_id, OrderState.DISPATCH_TRIGGERED
            )
            return True
        except Exception as e:
            logger.warning(
                "Dispatch trigger failed", order_id=event.order_id, error=str(e)
            )
            return False
