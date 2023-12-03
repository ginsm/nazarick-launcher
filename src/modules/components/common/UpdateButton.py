from modules import view

def create(ctk, parent, textbox, pool, progress, tabs, changes, html_frame, update_fn):
    update = ctk.CTkButton(
        master=parent,
        text='Play',
        height=46,
        width=180,
        command=lambda: pool.submit(update_fn, parent, ctk, textbox, pool, tabs, changes, html_frame, progress),
        border_width=0
    )

    view.add_lockable(update)

    return update