import asyncio

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
        """Synchronous entry point (called from Celery)"""
        try:
            asyncio.run(self._process_async(event))
        except Exception as e:
            logger.error("Handler failed", event_id=event.event_id, error=str(e))
            raise

    async def _process_async(self, event: PaymentSuccessEvent):
        """Actual async logic"""
        # Idempotency
        if await self.event_store.is_already_processed(event.event_id):
            logger.info("Duplicate event skipped", event_id=event.event_id)
            return

        await self.event_store.mark_in_progress(event.event_id, event.order_id)
        await self.order_repo.update_order_state(
            event.order_id, OrderState.PAYMENT_SUCCESS_RECEIVED
        )

        # Trigger independently
        rest_ok = await self._trigger_restaurant(event)
        disp_ok = await self._trigger_dispatch(event)

        if rest_ok and disp_ok:
            await self.event_store.mark_completed(event.event_id)
        else:
            await self.event_store.mark_failed(event.event_id, "Partial failure")

        logger.info(
            "PaymentSuccess processing finished",
            event_id=event.event_id,
            order_id=event.order_id,
            restaurant=rest_ok,
            dispatch=disp_ok,
        )

    async def _trigger_restaurant(self, event: PaymentSuccessEvent) -> bool:
        try:
            self.restaurant_client.trigger_preparation(event)
            await self.order_repo.update_order_state(
                event.order_id, OrderState.RESTAURANT_TRIGGERED
            )
            return True
        except Exception as e:
            logger.warning("Restaurant failed", order_id=event.order_id, error=str(e))
            return False

    async def _trigger_dispatch(self, event: PaymentSuccessEvent) -> bool:
        try:
            self.dispatch_client.trigger_rider_assignment(event)
            await self.order_repo.update_order_state(
                event.order_id, OrderState.DISPATCH_TRIGGERED
            )
            return True
        except Exception as e:
            logger.warning("Dispatch failed", order_id=event.order_id, error=str(e))
            return False
