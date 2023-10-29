from modules import store
from modules import view

def create(ctk, master, textbox, update_fn):
    update = ctk.CTkButton(
        master=master,
        text='Start Game',
        height=36,
        command=lambda: update_fn(
            app=master,
            ctk=ctk,
            textbox=textbox,
            options=store.get_state(),
        )
    )

    view.add_lockable(update)

    return update