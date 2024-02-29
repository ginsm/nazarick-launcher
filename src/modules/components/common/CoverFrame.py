def create(ctk, app):
    cover_frame = ctk.CTkFrame(master=app, corner_radius=0, border_width=0)
    cover_frame.grid_columnconfigure(0, weight=1)
    cover_frame.grid_rowconfigure(0, weight=1)

    loading_label = ctk.CTkLabel(master=cover_frame, text='Loading...')
    loading_label.grid(row=0, column=0, sticky='nsew')

    cover_frame.grid(row=0, column=0, rowspan=5, columnspan=5, sticky='nsew')

    return cover_frame