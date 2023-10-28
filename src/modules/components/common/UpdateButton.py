from modules import store

def create(ctk, master, lockable, textbox, update_fn):
    update = ctk.CTkButton(
        master=master,
        text='Start Game',
        height=36,
        command=lambda: update_fn(
            app=master,
            ctk=ctk,
            textbox=textbox,
            options=store.get_state(),
            lockable=[*lockable, update],
        )
    )

    return update