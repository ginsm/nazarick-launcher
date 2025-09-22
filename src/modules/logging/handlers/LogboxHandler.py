import logging, copy
from operator import itemgetter

from modules import constants
from modules.components.common import Logbox

LOG_RECORD_BUILTIN_ATTRS = {
    "args",
    "asctime",
    "created",
    "exc_info",
    "exc_text",
    "filename",
    "funcName",
    "levelname",
    "levelno",
    "lineno",
    "module",
    "msecs",
    "message",
    "msg",
    "name",
    "pathname",
    "process",
    "processName",
    "relativeCreated",
    "stack_info",
    "thread",
    "threadName",
    "taskName",
}

logger = logging.getLogger(constants.LOGGER_NAME)


class LogboxSender:
    def __init__(self) -> None:
        self.logboxes = {}
        self.broadcasts = set()

    
    def get_logbox(self, ctk, parent, game, pack):
        logger = f'{constants.LOGGER_NAME}.{game.lower()}.{pack.lower()}'

        # Return existing logbox
        if logger in self.logboxes.keys():
            logbox, contents = itemgetter('logbox', 'contents')(self.logboxes.get(logger))

            # Ensure the parent exists and return the logbox
            if logbox.master.winfo_exists():
                return logbox
            
            # Otherwise recreate it, populate its content, and return
            else:
                return self.recreate_logbox(ctk, parent, logger, contents)
        
        # Create new logbox and populate it with broadcasts
        logbox = Logbox.create(ctk, parent)
        self.logboxes[logger] = {
            'logbox': logbox,
            'contents': ''
        }

        if self.broadcasts:
            for message in self.broadcasts:
                self.write_to_logbox(logger, 'INFO', message)
        
        return logbox
    

    # Not really happy with this.. but it's necessary as the parent widget gets destroyed
    # when reloading widgets/frames.
    def recreate_logbox(self, ctk, parent, logger, contents):
        # Create new logbox widget and populate with contents
        new_logbox = Logbox.create(ctk, parent)
        new_logbox.configure(state='normal')
        new_logbox.insert(index='end', text=contents)
        new_logbox.configure(state='disabled')
        new_logbox.see('end')

        # Store new logbox and return
        self.logboxes[logger].update({'logbox': new_logbox}) 
        return new_logbox


    def write_to_logbox(self, logger, level, message):
        logbox, contents = itemgetter('logbox', 'contents')(self.logboxes.get(logger))

        # Format message
        if message:
            message = f'[{level}] {message}\n'
        else:
            message = '\n'

        # Add message to contents
        self.logboxes.get(logger).update({'contents': contents + message})

        # Add message to logbox
        logbox.configure(state='normal')
        logbox.insert(index='end', text=message, tags=level)
        logbox.configure(state='disabled')
        logbox.see('end')


    def write_record(self, record: logging.LogRecord) -> None:
        # Store broadcast messages in a set and emit to all loggers
        if hasattr(record, 'broadcast'):
            self.broadcasts.add(record.message)
            for logger in self.logboxes.keys():
                self.write_to_logbox(logger, record.levelname, record.message)
            return

        # Only write log if a logbox exists for the logger
        if record.name in self.logboxes.keys():
            self.write_to_logbox(record.name, record.levelname, record.message)


class Handler(logging.Handler):
    def __init__(self) -> None:
        self.sender = LogboxSender()
        super().__init__()

    def get_logbox(self, ctk, parent, game, pack):
        return self.sender.get_logbox(ctk, parent, game, pack)

    def emit(self, record: logging.LogRecord):
        if record.exc_info or record.stack_info:
            return

        msg = record.getMessage()

        trace_message = "Traceback (most recent call last)"
        if trace_message in msg:
            msg = msg.split(trace_message)[0].strip()

        if msg.startswith("Stack Trace:"):
            return
        
        rec = copy.copy(record)
        rec.message = msg
        self.sender.write_record(rec)