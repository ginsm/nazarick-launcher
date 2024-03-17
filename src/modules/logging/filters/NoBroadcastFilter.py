import logging
from typing import override


class Filter(logging.Filter):
    @override
    def filter(self, record: logging.logRecord) -> bool | logging.LogRecord:
        return not hasattr(record, 'broadcast')