def create(ctk, master):
    textbox = ctk.CTkTextbox(
        master=master,
        border_width=0,
        state='disabled'
    )

    return textbox