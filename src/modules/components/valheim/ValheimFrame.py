from modules.components.common import GameTitleBar, LogBox, ExplorerSearch, UpdateButton
from modules import view

def create(ctk, master):
    frame = ctk.CTkFrame(master=master)
    frame.grid_columnconfigure(0, weight=1)
    frame.grid_rowconfigure(1, weight=1)

    # Create components
    [title] = GameTitleBar.create(ctk=ctk, master=frame, game='Valheim')

    textbox = LogBox.create(
        ctk=ctk,
        master=frame
    )

    install = ExplorerSearch.create(
        ctk=ctk,
        master=frame,
        game='valheim',
        label='Install Path',
        placeholder='Enter the path to your Valheim install.',
        name='install',
        find='directory'
    )

    update = UpdateButton.create(
        ctk=ctk,
        master=frame,
        textbox=textbox,
        update_fn=lambda app, ctk, textbox, options: view.log("[INFO] That feature has not been implemented yet.", textbox)
    )

    # Add lockable elements to array
    view.add_lockable([*install[:-1]])

    # Position components
    title.grid(row=0, sticky='w')
    textbox.grid(row=1, columnspan=2, pady=(10, 5), padx=10, sticky='nsew')
    install[-1].grid(row=2, sticky='ew', columnspan=2)
    update.grid(row=3, padx=10, pady=(14, 15), columnspan=2, sticky='ew')

    return [frame, textbox]