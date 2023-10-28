from modules import view
from modules import store

def create(ctk, master, instance, executable, textbox, update_fn):
    update = ctk.CTkButton(
        master=master,
        text="Start Game",
        height=36,
        command=lambda: update_fn(
            app=master,
            ctk=ctk,
            textbox=textbox,
            options=store.getState(),
            lockable=[*instance[:-1], *executable[:-1], update],
        )
    )

    return update