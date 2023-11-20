def create(ctk, text, buttons, title):
    modal = ctk.CTkToplevel()
    modal.title(title)
    modal.grid_rowconfigure(0, weight=1)
    modal.grid_columnconfigure(0, weight=1)
    modal.grab_set()

    pady = 20
    padx = 15

    label = ctk.CTkLabel(
        master=modal, 
        text=text
    )
    label.grid(row=0, column=0, pady=(pady, 0), padx=padx, sticky="nsew")

    for index, btn in enumerate(buttons):
        button = ctk.CTkButton(
            master=modal,
            text=btn.get('text'),
            command=lambda: btn.get('command')(modal)
        )

        button.grid(row=1, column=index, padx=padx, pady=pady, sticky="we")
