import atexit
import logging.config
import os
from modules import constants
from modules.logging import logging_config

def setup_logging():
    root = constants.APP_BASE_DIR

    # Create logs directory
    os.makedirs(os.path.join(root, 'logs'), exist_ok=True)

    # Load config
    logging.config.dictConfig(logging_config.CONFIG)

    # Create a queue handler
    queue_handler = logging.getHandlerByName('queue_handler')
    if queue_handler is not None:
        queue_handler.listener.start()
        atexit.register(queue_handler.listener.stop)


def init():
    # Set up logger
    setup_logging()
    logging.basicConfig(level="INFO")

    logger_blocklist = [
        'PIL',
        'urllib3'
    ]

    # Block other loggers from showing up
    for module in logger_blocklist:
        logging.getLogger(module).setLevel(logging.WARNING)