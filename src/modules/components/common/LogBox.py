from modules import state_manager

logs = {}
broadcasts = []

def create(ctk, master, game):
    textbox = ctk.CTkTextbox(
        master=master,
        border_width=0,
        border_spacing=16,
        state='disabled'
    )

    textbox.tag_config('error', foreground='red')
    textbox.tag_config('warning', foreground='yellow')

    # Add game & pack to logs
    name = f'{game}-{state_manager.get_selected_pack(game)}'

    if not logs.get(name):
        logs[name] = [[message, ''] for message in broadcasts]

    # Methods to return
    def log(message, tag = '', store_message = True, broadcast = False):
        textbox.configure(state='normal')
        textbox.insert(index='end', text=message + '\n', tags=tag)
        textbox.configure(state='disabled')
        textbox.see('end')

        # NOTE - This could be improved by adding the broadcast to all
        # non-active logs.
        if broadcast:
            # Add message to broadcasts
            if message not in broadcasts:
                broadcasts.append(message)

        if store_message:
            logs[name].append([message, tag])




    def get():
        return textbox

    # Restore previous logs
    if len(logs.get(name)):
        for stored_log in logs.get(name):
            message, tag = stored_log
            log(message, tag=tag, store_message=False)

    return {
        'log': log,
        'get': get
    }