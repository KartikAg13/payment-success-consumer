import enum

from sqlalchemy import Column, DateTime, Enum, Integer, String, Text, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class OrderState(str, enum.Enum):
    PAYMENT_SUCCESS_RECEIVED = "PAYMENT_SUCCESS_RECEIVED"
    RESTAURANT_TRIGGERED = "RESTAURANT_TRIGGERED"
    DISPATCH_TRIGGERED = "DISPATCH_TRIGGERED"
    RIDER_ASSIGNED = "RIDER_ASSIGNED"
    PARTIALLY_FAILED = "PARTIALLY_FAILED"
    FAILED = "FAILED"


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(String, unique=True, nullable=False, index=True)
    current_state = Column(
        Enum(OrderState), nullable=False, default=OrderState.PAYMENT_SUCCESS_RECEIVED
    )
    restaurant_triggered_at = Column(DateTime, nullable=True)
    dispatch_triggered_at = Column(DateTime, nullable=True)
    rider_assigned_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class ProcessedEvent(Base):
    __tablename__ = "processed_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(String, unique=True, nullable=False, index=True)
    order_id = Column(String, nullable=False)
    status = Column(String, nullable=False)  # "COMPLETED", "IN_PROGRESS", "FAILED"
    processed_at = Column(DateTime, server_default=func.now())
    error_message = Column(Text, nullable=True)
