from modules import constants, state_manager
import logging

logs = {}
broadcasts = []

logger = logging.getLogger(constants.LOGGER_NAME)

def create(ctk, master, game):
    # Configure textbox
    textbox = ctk.CTkTextbox(
        master=master,
        border_width=0,
        border_spacing=16,
        state='disabled'
    )

    textbox.tag_config('error', foreground='red')
    textbox.tag_config('warning', foreground='yellow')

    # This represents the name of the textbox logger in logs
    name = f'{game}-{state_manager.get_selected_pack(game)}'


    # Create textbox logger in logs
    if not logs.get(name):
        logs[name] = [[message, '', True] for message in broadcasts]
        
    # Create LogBoxLogger
    LogBox = TextboxLogger(textbox, name)

    # Restore previous logs
    if len(logs.get(name)):
        for stored_log in logs.get(name):
            message, tag, broadcast = stored_log
            LogBox.log(message, tag=tag, store_message=False, broadcast=broadcast)

    return LogBox


class TextboxLogger():
    def __init__(self, textbox, name):
        self.textbox = textbox
        self.name = name


    def log(self, message, tag = '', store_message = True, broadcast = False):
        textbox_message = ''

        if message:
            textbox_message = f'[{tag.upper() if tag else 'INFO'}] {message}'

        self.textbox.configure(state='normal')
        self.textbox.insert(index='end', text=textbox_message + '\n', tags=tag)
        self.textbox.configure(state='disabled')
        self.textbox.see('end')

        if not broadcast:
            log_message = getattr(logger, tag) if tag else logger.info
            log_message(message)

        # NOTE - This could be improved by adding the broadcast to all
        # non-active logs.
        if broadcast:
            # Add message to broadcasts
            if message not in broadcasts:
                broadcasts.append(message)

        if store_message:
            logs[self.name].append([message, tag, broadcast])