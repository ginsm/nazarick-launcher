from modules import view

def create(ctk, master, textbox, pool, update_fn):
    update = ctk.CTkButton(
        master=master,
        text='Start Game',
        height=36,
        command=lambda: pool.submit(update_fn, master, ctk, textbox, pool)
    )

    view.add_lockable(update)

    return update