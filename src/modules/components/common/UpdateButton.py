from modules import store, view
from modules.game_list import get_modpack

def create(ctk, parent, pool, update_fn, widgets, game):
    update = ctk.CTkButton(
        master=parent,
        text='Play',
        height=46,
        width=180,
        command=lambda: pool.submit(update_fn, ctk, parent, pool, widgets, get_modpack(game, store.get_selected_pack())),
        border_width=0
    )

    view.add_lockable(update)

    return update