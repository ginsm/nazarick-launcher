from modules import gui_manager, state_manager
from modules.utility import get_modpack_data

def create(ctk, parent, pool, update_fn, widgets, game):
    modpack_data = get_modpack_data(game, state_manager.get_selected_pack())

    update = ctk.CTkButton(
        master=parent,
        text='Play',
        height=46,
        width=180,
        command=lambda: pool.submit(update_fn, ctk, parent, pool, widgets, modpack_data),
        border_width=0
    )

    gui_manager.add_lockable(update)

    return update