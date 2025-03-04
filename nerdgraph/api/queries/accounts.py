import asyncio
from typing import List, Dict, Any, Optional
from nerdgraph.api.nerdgraph_client import AsyncNerdGraphClient


class AccountQueries:
    """Class containing queries related to New Relic accounts"""

    @staticmethod
    async def get_all_accounts(client: AsyncNerdGraphClient) -> List[Dict[str, Any]]:
        """
        Get all accounts accessible with the current API key.

        Args:
            client: An initialized AsyncNerdGraphClient

        Returns:
            List of account objects with id and name
        """
        query = """
        {
          actor {
            accounts {
              id
              name
            }
          }
        }
        """

        result = await client.execute_query(query)
        return result["data"]["actor"]["accounts"]
