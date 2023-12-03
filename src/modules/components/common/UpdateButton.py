from modules import view

def create(ctk, parent, pool, update_fn, widgets):
    update = ctk.CTkButton(
        master=parent,
        text='Play',
        height=46,
        width=180,
        command=lambda: pool.submit(update_fn, ctk, parent, pool, widgets),
        border_width=0
    )

    view.add_lockable(update)

    return update