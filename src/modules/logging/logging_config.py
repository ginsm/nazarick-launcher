from modules import state_manager

# These are imported here so that pyinstaller bundles them
from modules.logging.handlers import LogboxHandler
from modules.logging.filters import NoBroadcastFilter

# This is a function as the config relies on state_manager's database having
# been created.
def get_config():
    std_out_level = 'INFO'

    if state_manager.get_state('debug')[0]:
        std_out_level = 'DEBUG'

    return {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'simple': {
                'format': '[%(levelname)s - %(asctime)s] %(message)s',
                'datefmt': '%m-%d-%YT%H:%M:%S'
            }
        },
        'filters': {
            'no_broadcasts': {
                'class': 'modules.logging.filters.NoBroadcastFilter.Filter'
            }
        },
        'handlers': {
            'logbox': {
                'class': 'modules.logging.handlers.LogboxHandler.Handler',
                'level': 'INFO',
                'formatter': 'simple'
            },
            'stderr': {
                'class': 'logging.StreamHandler',
                'level': 'WARNING',
                'formatter': 'simple',
                'stream': 'ext://sys.stderr'
            },
            'stdout': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': std_out_level,
                'formatter': 'simple',
                'filename': 'logs/launcher.log',
                'maxBytes': 10485760,
                'backupCount': 3,
                'filters': ['no_broadcasts']
            },
            'queue_handler': {
                'class': 'logging.handlers.QueueHandler',
                'handlers': ['stderr', 'stdout', 'logbox'],
                'respect_handler_level': True
            }
        },
        'loggers': {
            'root': {
                'level': 'DEBUG',
                'handlers': ['queue_handler']
            }
        }
    }