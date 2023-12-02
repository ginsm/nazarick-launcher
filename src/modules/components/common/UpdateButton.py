from modules import view

def create(ctk, master, textbox, pool, progress, update_fn):
    update = ctk.CTkButton(
        master=master,
        text='Play',
        height=46,
        width=180,
        command=lambda: pool.submit(update_fn, master, ctk, textbox, pool, progress),
        border_width=0
    )

    view.add_lockable(update)

    return update