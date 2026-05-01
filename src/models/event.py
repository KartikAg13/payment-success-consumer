import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class PaymentSuccessEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    order_id: str
    payment_id: str
    transaction_id: str
    amount: float
    currency: str = "INR"
    status: Literal["SUCCESS"] = "SUCCESS"
    timestamp: datetime
    version: int = 1
    correlation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Amount must be positive")
        return v

    @field_validator("order_id", "payment_id", "transaction_id")
    @classmethod
    def fields_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty")
        return v.strip()
