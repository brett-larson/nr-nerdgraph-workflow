import asyncio
import logging

from utils import AppLogger
from api.queries.accounts import AccountQueries
from api.queries.nrql_queries import NrqlQueries
from api.nerdgraph_client import AsyncNerdGraphClient

# Initialize the logger
logger = AppLogger(
    __name__,
    log_dir="logs",
    log_level=logging.INFO,
    enable_console=True,
    max_file_size=10 * 1024 * 1024,  # 10 MB
    backup_count=5
).get_logger()

# Example of how to use these components together
async def main():
    # Initialize the client with rate limiting
    client = AsyncNerdGraphClient(max_concurrency=25)

    # Get all accounts
    accounts = await AccountQueries.get_all_accounts(client)
    print(f"Found {len(accounts)} accounts")

    # Run a query across all accounts
    results = await NrqlQueries.run_query_across_accounts(
        client=client,
        nrql="SELECT count(*) FROM Transaction SINCE 1 day ago",
        accounts=accounts
    )

    # Process results
    for result in results:
        account_id = result['account_id']
        if "error" in result:
            print(f"Error for account {account_id}: {result['error']}")
        else:
            count = result['results'][0].get('count', 'N/A') if result['results'] else 'No data'
            print(f"Account {account_id}: {count} transactions")


if __name__ == "__main__":
    asyncio.run(main())
