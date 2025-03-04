import asyncio
from typing import List, Dict, Any, Optional
from nerdgraph.api.nerdgraph_client import AsyncNerdGraphClient


class NrqlQueries:
    """Class containing NRQL-related queries"""

    @staticmethod
    async def run_account_query(
            client: AsyncNerdGraphClient,
            account_id: int,
            nrql: str,
            timeout: int = 90
    ) -> Dict[str, Any]:
        """
        Run an NRQL query for a specific account.

        Args:
            client: An initialized AsyncNerdGraphClient
            account_id: The New Relic account ID
            nrql: The NRQL query string
            timeout: Query timeout in seconds

        Returns:
            Query results
        """
        gql = f"""
        {{
          actor {{
            account(id: {account_id}) {{
              nrql(query: "{nrql}", timeout: {timeout}) {{
                results
              }}
            }}
          }}
        }}
        """

        result = await client.execute_query(gql)
        return {
            "account_id": account_id,
            "results": result["data"]["actor"]["account"]["nrql"]["results"]
        }

    @staticmethod
    async def run_query_across_accounts(
            client: AsyncNerdGraphClient,
            nrql: str,
            accounts: Optional[List[Dict[str, Any]]] = None,
            timeout: int = 90
    ) -> List[Dict[str, Any]]:
        """
        Run an NRQL query across multiple accounts.

        Args:
            client: An initialized AsyncNerdGraphClient
            nrql: The NRQL query to run
            accounts: List of account objects (if None, will fetch all accounts)
            timeout: Query timeout in seconds

        Returns:
            List of results, one per account
        """
        if accounts is None:
            accounts = await AccountQueries.get_all_accounts(client)

        async def query_account(account):
            try:
                return await NrqlQueries.run_account_query(
                    client=client,
                    account_id=account['id'],
                    nrql=nrql,
                    timeout=timeout
                )
            except Exception as e:
                return {
                    "account_id": account["id"],
                    "error": str(e)
                }

        return await client.execute_batch_queries(query_account, accounts)


