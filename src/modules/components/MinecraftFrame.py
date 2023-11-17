from modules.components.common import LogBox, ExplorerSearch, UpdateButton
from modules.minecraft import updater
from modules import view

def create(ctk, master, pool):
    frame = ctk.CTkFrame(master=master, corner_radius=0, border_width=0)
    frame.grid_columnconfigure(0, weight=1)
    frame.grid_rowconfigure(1, weight=1)

    textbox = LogBox.create(
        ctk=ctk,
        master=frame
    )

    instance = ExplorerSearch.create(
        ctk=ctk,
        master=frame,
        game='minecraft',
        label='Instance Path',
        placeholder='Enter the path to your Minecraft instance.',
        name='instance',
        find='directory'
    )

    executable = ExplorerSearch.create(
        ctk=ctk,
        master=frame,
        game='minecraft',
        label="Launcher's Executable Path",
        placeholder="Enter the path to your launcher's executable.",
        name='executable',
        find='file'
    )

    update = UpdateButton.create(
        ctk=ctk,
        master=frame,
        textbox=textbox,
        pool=pool,
        update_fn=updater.start
    )

    # Add lockable elements to array
    view.add_lockable([*instance[:-1], *executable[:-1]])

    # Position components
    textbox.grid(row=1, columnspan=2, pady=(15, 5), padx=10, sticky='nsew')
    instance[-1].grid(row=2, padx=1, sticky='ew', columnspan=2)
    executable[-1].grid(row=3, padx=1, sticky='ew', columnspan=2)
    update.grid(row=4, padx=10, pady=(14, 15), columnspan=2, sticky='ew')

    return [frame, textbox]