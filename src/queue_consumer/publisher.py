import uuid
from datetime import datetime

from celery_app import app
from src.models.event import PaymentSuccessEvent
from src.utils.logger import logger


def publish_payment_success(order_id: str, amount: float = 450.0):
    event = PaymentSuccessEvent(
        event_id=str(uuid.uuid4()),
        order_id=order_id,
        payment_id=f"pay_{uuid.uuid4().hex[:8]}",
        transaction_id=f"txn_{uuid.uuid4().hex[:8]}",
        amount=amount,
        currency="INR",
        timestamp=datetime.utcnow(),
        correlation_id=str(uuid.uuid4()),
    )

    task = app.send_task("consume_payment_success", args=[event.model_dump()])

    logger.info(
        "Published PaymentSuccess event", event_id=event.event_id, order_id=order_id
    )
    print(f"✅ Published event for order {order_id} | Task: {task.id}")
    return event


def publish_duplicate_event(order_id: str):
    """Helper to test idempotency"""
    event_id = "test_duplicate_event_001"

    event = PaymentSuccessEvent(
        event_id=event_id,
        order_id=order_id,
        payment_id=f"pay_dup_{event_id}",
        transaction_id=f"txn_dup_{event_id}",
        amount=520.0,
        currency="INR",
        timestamp=datetime.utcnow(),
        correlation_id="test-correlation-duplicate",
    )

    task = app.send_task("consume_payment_success", args=[event.model_dump()])
    print(f"✅ Published DUPLICATE event for order {order_id} | Event ID: {event_id}")
    return event
