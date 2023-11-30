def create(ctk, text, buttons, title, justify="center"):
    modal = ctk.CTkToplevel()
    modal.title(title)
    modal.grid_rowconfigure(0, weight=1)
    modal.grid_columnconfigure(0, weight=1)
    modal.grab_set()

    pady = 20
    padx = 15

    label = ctk.CTkLabel(
        master=modal, 
        text=text,
        justify=justify
    )
    label.grid(row=0, column=0, columnspan=len(buttons), pady=(pady, 0), padx=padx, sticky="nsew")

    for index, btn in enumerate(buttons):
        def callback_factory(button):
            return lambda: button.get('command')(modal)
        
        button = ctk.CTkButton(
            master=modal,
            text=btn.get('text'),
            command=callback_factory(btn)
        )

        if btn.get('border'):
            button.configure(border_color=btn.get('border'))
            button.configure(border_width=1)

        if (index == 0):
            button_padx = (padx, 5)
        elif (index == len(buttons) - 1):
            button_padx = (5, padx)
        else:
            button_padx = 5

        button.grid(row=1, column=index, padx=button_padx, pady=pady, sticky="we")
