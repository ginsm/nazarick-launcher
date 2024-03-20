CONFIG = {
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
            'level': 'DEBUG',
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