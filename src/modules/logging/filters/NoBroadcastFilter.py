import logging
from typing import override


class Filter(logging.Filter):
    @override
    def filter(self, record: logging.LogRecord) -> bool | logging.LogRecord:
        return not hasattr(record, 'broadcast')