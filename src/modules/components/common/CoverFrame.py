def create(ctk, app):
    cover_frame = ctk.CTkFrame(master=app, corner_radius=0, border_width=0)
    cover_frame.grid_columnconfigure(0, weight=1)
    cover_frame.grid_rowconfigure(0, weight=1)

    loading_label = ctk.CTkLabel(master=cover_frame, text='Loading theme...')
    loading_label.grid(row=0, column=0, sticky='nsew')

    return cover_frame