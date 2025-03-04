import logging

import aiohttp
import asyncio
from typing import Optional, Dict, Any, List, Union, Callable
import os
from nerdgraph.utils import AppLogger
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize the logger
logger = AppLogger(
    __name__,
    log_dir="logs",
    log_level=logging.INFO,
    enable_console=True,
    max_file_size=10 * 1024 * 1024,  # 10 MB
    backup_count=5
).get_logger()

class AsyncNerdGraphClient:
    """
    Asynchronous client for interacting with New Relic's NerdGraph GraphQL API.

    Handles authentication, rate limiting, and execution of GraphQL queries against
    the New Relic API using asyncio for concurrent requests.
    """

    DEFAULT_ENDPOINT = "https://api.newrelic.com/graphql"
    DEFAULT_CONCURRENCY = 25

    def __init__(
            self,
            api_key: Optional[str] = None,
            endpoint: str = DEFAULT_ENDPOINT,
            max_concurrency: int = DEFAULT_CONCURRENCY
    ):
        """
        Initialize the async NerdGraph client with rate limiting.

        Args:
            api_key: New Relic API key (optional, will try to load from environment if not provided)
            endpoint: GraphQL API endpoint URL
            max_concurrency: Maximum number of concurrent requests allowed
        """
        self.endpoint = endpoint
        self.api_key = api_key or self.get_api_key()

        if not self.api_key:
            logger.warning("Missing API key")
            raise ValueError("Missing API key")

        self.headers = {
            "Content-Type": "application/json",
            "API-Key": self.api_key
        }

        # Initialize rate limiter semaphore
        self.rate_limiter = asyncio.Semaphore(max_concurrency)

    @staticmethod
    def get_api_key() -> Optional[str]:
        """
        Load New Relic API key from local environment variables

        Returns:
            API key from environment variable
        """
        return os.getenv('NEW_RELIC_API_KEY')

    def set_api_key(self, api_key: str) -> None:
        """
        Set or update the API key used by the client

        Args:
            api_key: New Relic API key
        """
        self.api_key = api_key
        self.headers["API-Key"] = api_key

    async def execute_query(
            self,
            query: str,
            variables: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a single GraphQL query with rate limiting

        Args:
            query: GraphQL query string
            variables: Optional dictionary of variables for the query

        Returns:
            JSON response from the API

        Raises:
            aiohttp.ClientError: For network errors
            ValueError: For API errors
        """
        if variables is None:
            variables = {}

        # Use the rate limiter to control concurrency
        async with self.rate_limiter:
            try:
                logger.info("Sending GraphQL request.")

                async with aiohttp.ClientSession() as session:
                    async with session.post(
                            self.endpoint,
                            headers=self.headers,
                            json={"query": query, "variables": variables}
                    ) as response:
                        if response.status != 200:
                            error_text = await response.text()
                            logger.error(f"HTTP error {response.status}: {error_text}")
                            raise ValueError(f"HTTP error {response.status}: {error_text}")

                        result = await response.json()

                        # Check for GraphQL-level errors
                        if "errors" in result:
                            error_msg = "; ".join(
                                [err.get("message", "Unknown error") for err in result.get("errors", [])])
                            logger.error(f"GraphQL errors: {error_msg}")
                            raise ValueError(f"GraphQL errors: {error_msg}")

                        return result

            except aiohttp.ClientError as e:
                logger.error(f"Network error: {e}")
                raise
            except ValueError:
                # Re-raise already logged GraphQL errors
                raise
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                raise Exception(f"Query failed to run: {e}")

    async def execute_batch_queries(
            self,
            query_generator: Callable[[Any], asyncio.Task],
            items: List[Any]
    ) -> List[Any]:
        """
        Execute multiple queries concurrently with rate limiting.

        Args:
            query_generator: A function that takes an item and returns a query task
            items: List of items to process with the query generator

        Returns:
            List of results from all queries, preserving the order of input items
        """
        tasks = [query_generator(item) for item in items]
        return await asyncio.gather(*tasks, return_exceptions=True)