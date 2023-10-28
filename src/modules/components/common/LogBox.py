def create(ctk, master):
    textbox = ctk.CTkTextbox(master=master)
    textbox.configure(state='disabled')

    return textbox