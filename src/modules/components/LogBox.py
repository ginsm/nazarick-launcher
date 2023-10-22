from modules import view

def create(ctk, master):
    textbox = ctk.CTkTextbox(master=master)
    textbox.configure(state="disabled")
    textbox.grid(row=0, column=0, columnspan=2, pady=(20, 14), padx=10, sticky="nsew")

    return textbox