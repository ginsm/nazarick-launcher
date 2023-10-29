from modules.components.common import LogBox, ExplorerSearch, UpdateButton
from modules.minecraft import updater

def create(ctk, master):
    frame = ctk.CTkFrame(master=master)
    frame.grid_columnconfigure(0, weight=1)
    frame.grid_rowconfigure(0, weight=1)
    frame.pack(anchor='center', fill='both', expand=True) #TODO swap to grid

    # Create components
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
        update_fn=updater.start
    )

    # Add lockable elements to array
    view.add_lockable([*instance[:-1], *executable[:-1]])

    # Position components
    textbox.grid(row=0, columnspan=2, pady=(20, 5), padx=10, sticky='nsew')
    instance[-1].grid(row=1, sticky='ew', columnspan=2)
    executable[-1].grid(row=2, sticky='ew', columnspan=2)
    update.grid(row=3, padx=10, pady=(14, 15), columnspan=2, sticky='ew')

    return [frame, textbox]