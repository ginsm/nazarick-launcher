def create(ctk, master, game):
    frame = ctk.CTkFrame(master=master, fg_color='transparent')
    frame.grid_rowconfigure(0, weight=1)

    font = ctk.CTkFont(size=28)
    label = ctk.CTkLabel(master=frame, text=game, font=font)
    label.grid(row=0, column=0, padx=10, pady=(15, 0), sticky='w')

    # TODO Add option menu

    return [frame]