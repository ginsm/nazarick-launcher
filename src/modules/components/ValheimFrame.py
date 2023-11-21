from modules.components.common import LogBox, ExplorerSearch, UpdateButton
from modules.valheim import updater
from modules import view

def create(ctk, master, pool):
    frame = ctk.CTkFrame(master=master, corner_radius=0, border_width=0)
    frame.grid_columnconfigure(0, weight=1)
    frame.grid_rowconfigure(1, weight=1)

    # Create components
    textbox = LogBox.create(
        ctk=ctk,
        master=frame,
        game='Valheim'
    )

    install = ExplorerSearch.create(
        ctk=ctk,
        master=frame,
        game='valheim',
        app=master,
        label='Install Path',
        placeholder='Enter the path to your Valheim install.',
        name='install',
        find='directory'
    )

    update = UpdateButton.create(
        ctk=ctk,
        master=frame,
        textbox=textbox,
        pool=pool,
        update_fn=updater.start
    )

    # Add lockable elements to array
    view.add_lockable([*install[:-1]])

    # Position components
    textbox['get']().grid(row=1, columnspan=2, pady=(15, 5), padx=10, sticky='nsew')
    install[-1].grid(row=2, padx=1, sticky='ew', columnspan=2)
    update.grid(row=3, padx=10, pady=(14, 15), columnspan=2, sticky='ew')

    return [frame, textbox]