# NerdGraph API

This folder contains the implementation of the NerdGraph API client and related utilities.

## Files

### `nerdgraph_client.py`
This file contains the `NerdGraphClient` class, which is responsible for interacting with the NerdGraph API.

### `rate_limiter.py`
This file contains the `RateLimiter` class, which is used to control the number of API calls within a specified time window. It uses a sliding window approach to track calls and enforce rate limits.

### `queries/`
This folder is for holding any GraphQL queries and supporting logic.

## Usage

### RateLimiter

The `RateLimiter` class can be used to ensure that the number of API calls does not exceed a specified limit within a given time window.

#### Example

```python
from nerdgraph.api.rate_limiter import RateLimiter
from datetime import timedelta

# Initialize rate limiter to allow 10 calls per minute
rate_limiter = RateLimiter(max_calls=10, time_window=timedelta(minutes=1))

# Use the rate limiter before making an API call
rate_limiter.wait_if_needed()
# Make your API call here