from typing import Optional, Dict, Any, Union
import requests
import os
from nerdgraph.utils import Logger
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Create logger for the module
logger = Logger(__name__).get_logger()


class NerdGraphClient:
    """
    Client for interacting with New Relic's NerdGraph GraphQL API.

    Handles authentication and execution of GraphQL queries against the New Relic API.
    """

    DEFAULT_ENDPOINT = "https://api.newrelic.com/graphql"

    def __init__(self, api_key: Optional[str] = None, endpoint: str = DEFAULT_ENDPOINT):
        self.endpoint = endpoint
        self.api_key = api_key or self.get_api_key()

        if not self.api_key:
            logger.warning("Missing API key")
            raise ValueError("Missing API key")

        self.headers = {
            "Content-Type": "application/json",
            "API-Key": self.api_key
        }

    @staticmethod
    def get_api_key() -> Optional[str]:
        """
        Load New Relic API key from local environment variables

        :return: API key from environment variable
        """
        return os.getenv('NEW_RELIC_API_KEY')

    def set_api_key(self, api_key: str) -> None:
        """
        Set or update the API key used by the client

        :param api_key: New Relic API key
        """
        self.api_key = api_key
        self.headers["API-Key"] = api_key

    def execute_query(self, query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a single GraphQL query

        :param query: GraphQL query string
        :param variables: Optional dictionary of variables for the query
        :return: JSON response from the API
        :raises: requests.RequestException for network errors
        :raises: ValueError for API errors
        """
        try:
            logger.info("Sending GraphQL request.")
            response = requests.post(
                self.endpoint,
                headers=self.headers,
                json={"query": query, "variables": variables}
            )

            response.raise_for_status()
            result = response.json()

            # Check for GraphQL-level errors
            if "errors" in result:
                error_msg = "; ".join([err.get("message", "Unknown error") for err in result["errors"]])
                logger.error(f"GraphQL errors: {error_msg}")
                raise ValueError(f"GraphQL errors: {error_msg}")

            return result

        except requests.RequestException as e:
            logger.error(f"Network error: {e}")
            raise
        except ValueError:
            # Re-raise already logged GraphQL errors
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise Exception(f"Query failed to run: {e}")
