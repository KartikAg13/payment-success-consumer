import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.queue_consumer.publisher import (
    publish_duplicate_event,
    publish_payment_success,
)
from src.repository.database import init_db
from src.utils.logger import setup_logging


def main():
    setup_logging()
    init_db()
    print("=== PaymentSuccess Consumer Demo ===\n")

    print("1. Happy Path")
    publish_payment_success(order_id="ORD_2001", amount=650.0)
    print("-" * 60)

    print("2. Duplicate Event Test")
    publish_duplicate_event("ORD_2002")
    print("→ Running duplicate again...")
    publish_duplicate_event("ORD_2002")
    print("-" * 60)

    print("3. Partial Failure Simulation")
    print("   (Dispatch has 30% chance to fail)")
    for i in range(3):
        order_id = f"ORD_300{i + 1}"
        print(f"\n→ Testing order {order_id}")
        publish_payment_success(order_id=order_id, amount=480.0)

    print("\n✅ Demo completed!")
    print("Check Celery worker logs to see:")
    print("   • Successful flows")
    print("   • Duplicate skipping")
    print("   • Partial failures (Dispatch failing while Restaurant succeeds)")


if __name__ == "__main__":
    main()
