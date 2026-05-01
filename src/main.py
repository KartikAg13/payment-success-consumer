import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.queue_consumer.publisher import publish_payment_success
from src.repository.database import init_db
from src.utils.logger import setup_logging


async def main():
    setup_logging()
    init_db()
    print("✅ Database initialized")

    print("\nSending test PaymentSuccess event...")
    publish_payment_success(order_id="ORD_1001", amount=520.0)
    print("\nTest event published. Check Celery worker logs.")


if __name__ == "__main__":
    asyncio.run(main())
