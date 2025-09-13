import logging

class OnlyDebugFilter(logging.Filter):
    def filter(self, record):
        return record.levelno == logging.DEBUG