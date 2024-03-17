logs = {}
broadcasts = []

def create(ctk, master):
    # Configure textbox
    textbox = ctk.CTkTextbox(
        master=master,
        border_width=0,
        border_spacing=16,
        state='disabled'
    )

    textbox.tag_config('ERROR', foreground='red')
    textbox.tag_config('WARNING', foreground='yellow')

    return textbox