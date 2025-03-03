from utils import AppLogger
from datetime import timedelta
from api.rate_limiter import RateLimiter
from api.nerdgraph_client import NerdGraphClient

# Initialize the logger
logger = AppLogger.get_instance(__name__).get_logger()

def main():

    logger.info("**********Starting the NerdGraph API Application**********")
    rate_limiter = RateLimiter(1000, timedelta(minutes=1))
    nerdgraph_client = NerdGraphClient()



    logger.info("**********Ending the NerdGraph API Application**********")

if __name__ == '__main__':
    main()
