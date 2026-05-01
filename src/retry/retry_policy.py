from src.utils.logger import logger


class RetryPolicy:
    """Simple retry configuration"""

    MAX_RETRIES = 3
    BASE_DELAY = 30  # seconds

    def get_delay(self, attempt: int) -> int:
        """Exponential backoff with jitter simulation"""
        delay = self.BASE_DELAY * (2 ** (attempt - 1))
        logger.info("Retry scheduled", attempt=attempt, delay_seconds=delay)
        return delay
