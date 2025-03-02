import time
from collections import deque
from datetime import timedelta
from nerdgraph.utils import Logger

# Create logger for the module
logger = Logger(__name__).get_logger()


class RateLimiter:
    """
    Rate limiter to control the number of calls within a specified time window.

    Uses a sliding window approach to track calls and enforce rate limits.
    """

    def __init__(self, max_calls: int, time_window: timedelta = timedelta(minutes=1)):
        """
        Initialize the rate limiter.

        Args:
            max_calls: Maximum number of calls allowed within the time window
            time_window: Time period for the rate limit (default: 1 minute)

        Raises:
            ValueError: If max_calls or time_window are not positive
        """
        if max_calls <= 0:
            raise ValueError("max_calls must be positive")
        if time_window.total_seconds() <= 0:
            raise ValueError("time_window must be positive")

        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = deque()
        self.time_func = time.monotonic
        self.start_time = self.time_func()

    def wait_if_needed(self) -> dict:
        """
        Wait if the rate limit has been reached.

        Removes expired calls from the tracking deque, then waits if necessary
        to stay within the rate limit.

        Returns:
            dict: Statistics about the call and any wait time
        """
        now = self.time_func()
        time_window_seconds = self.time_window.total_seconds()
        waited = 0

        # Log current state
        if self.calls:
            oldest = self.calls[0]
            newest = self.calls[-1]
            logger.info(
                f"Checking calls: {len(self.calls)} calls from {oldest - self.start_time:.2f}s to {newest - self.start_time:.2f}s")
        else:
            logger.info("Checking calls: 0 calls")

        # Remove calls older than the time window
        while self.calls and (now - self.calls[0]) > time_window_seconds:
            self.calls.popleft()

        # If at limit, wait until oldest call is outside the time window
        if len(self.calls) >= self.max_calls:
            wait_time = (self.calls[0] + time_window_seconds) - now
            if wait_time > 0:
                logger.info(f"Rate limit reached. Waiting for {wait_time:.2f} seconds.")
                try:
                    time.sleep(wait_time)
                    waited = wait_time
                except Exception as e:
                    logger.error(f"Error during sleep: {e}")

        # Record this call
        self.calls.append(self.time_func())

        return {
            "waited_seconds": waited,
            "remaining_calls": self.max_calls - len(self.calls),
            "queue_size": len(self.calls)
        }

    def reset(self):
        """
        Reset the rate limiter by clearing all tracked calls.
        """
        self.calls.clear()
        logger.info("Rate limiter reset")