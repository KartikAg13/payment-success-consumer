from datetime import datetime

from sqlalchemy import select

from src.repository.database import AsyncSessionLocal
from src.repository.models import Order, OrderState
from src.utils.logger import logger


class OrderRepository:
    """Order state management"""

    async def update_order_state(self, order_id: str, new_state: OrderState):
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Order).where(Order.order_id == order_id)
            )
            order = result.scalar_one_or_none()

            if not order:
                order = Order(order_id=order_id, current_state=new_state)
                session.add(order)
            else:
                order.current_state = new_state
                if new_state == OrderState.RESTAURANT_TRIGGERED:
                    order.restaurant_triggered_at = datetime.utcnow()
                elif new_state == OrderState.DISPATCH_TRIGGERED:
                    order.dispatch_triggered_at = datetime.utcnow()
                elif new_state == OrderState.RIDER_ASSIGNED:
                    order.rider_assigned_at = datetime.utcnow()

            await session.commit()
            logger.info("Order state updated", order_id=order_id, state=new_state.value)
