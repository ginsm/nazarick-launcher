logs = {}

def create(ctk, master, game):
    textbox = ctk.CTkTextbox(
        master=master,
        border_width=0,
        state='disabled'
    )

    # Add game to logs
    if not logs.get(game):
        logs[game] = []

    # Methods to return
    def log(message, store = True):
        textbox.configure(state='normal')
        textbox.insert(index='end', text=message + '\n')
        textbox.configure(state='disabled')
        textbox.see('end')
        if store:
            logs[game].append(message)

    def get():
        return textbox

    # Restore previous logs
    if len(logs.get(game)):
        content = '\n'.join(logs.get(game))
        log(content, store=False)

    return {
        'log': log,
        'get': get
    }