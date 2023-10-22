def create(ctk, master):
    main_frame = ctk.CTkFrame(master=master)
    main_frame.grid_columnconfigure(0, weight=1)
    main_frame.grid_rowconfigure(0, weight=1)
    main_frame.pack(anchor="center", fill="both", expand=True)
    return main_frame