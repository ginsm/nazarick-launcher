import atexit
import json
import logging.config
import os
from modules import constants

logger = logging.getLogger(constants.LOGGER_NAME)
logger_blocklist = [
    "PIL",
    "urllib3"
]


def setup_logging():
    root = constants.APP_BASE_DIR

    # Create logs directory
    os.makedirs(os.path.join(root, 'logs'), exist_ok=True)

    # Get config file contents
    config_file = os.path.join(root, 'modules', 'logging', 'config.json')
    with open(config_file) as f_in:
        config = json.load(f_in)

    # Load config
    logging.config.dictConfig(config)

    # Create a queue handler
    queue_handler = logging.getHandlerByName("queue_handler")
    if queue_handler is not None:
        queue_handler.listener.start()
        atexit.register(queue_handler.listener.stop)


def init():
    # Set up logger
    setup_logging()
    logging.basicConfig(level="INFO")

    # Block other loggers from showing up
    for module in logger_blocklist:
        logging.getLogger(module).setLevel(logging.WARNING)