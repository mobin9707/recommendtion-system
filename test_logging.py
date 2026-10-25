
from config.logging_config import setup_logging


logger = setup_logging()

logger.debug("Debug message.")
logger.info("Movie recommendation app started.")
logger.warning("Some IMDb ratings may be missing.")
logger.error("Example error message.")
