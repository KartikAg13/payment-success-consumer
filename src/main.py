import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.repository.database import init_db
from src.utils.logger import setup_logging


async def main():
    setup_logging()
    await init_db()
    print("Database tables created successfully")
    print("Logging setup complete")


if __name__ == "__main__":
    asyncio.run(main())
