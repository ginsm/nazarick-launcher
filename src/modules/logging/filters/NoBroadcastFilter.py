import logging


class NoBroadcastFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool | logging.LogRecord:
        return not hasattr(record, 'broadcast')