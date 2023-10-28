from modules.components.common import LogBox, ExplorerSearch, UpdateButton
from modules.components.minecraft import updater

def create(ctk, master):
    frame = ctk.CTkFrame(master=master)
    frame.grid_columnconfigure(0, weight=1)
    frame.grid_rowconfigure(0, weight=1)
    frame.pack(anchor='center', fill='both', expand=True)

    # Create components
    textbox = LogBox.create(ctk, frame)
    instance = ExplorerSearch.create(
        name='instance', label='Instance Path', find='directory',
        placeholder='Enter the path to your Minecraft instance.',
        ctk=ctk, master=frame
    )
    executable = ExplorerSearch.create(
        name='executable', label="Launcher's Executable Path", find='file',
        placeholder="Enter the path to your launcher's executable.",
        ctk=ctk, master=frame
    )
    update = UpdateButton.create(ctk, frame, instance, executable, textbox, updater.start)

    # Position components
    textbox.grid(row=0, columnspan=2, pady=(20, 5), padx=10, sticky='nsew')
    instance[-1].grid(row=1, sticky='ew', columnspan=2)
    executable[-1].grid(row=2, sticky='ew', columnspan=2)
    update.grid(row=3, padx=10, pady=(14, 15), columnspan=2, sticky='ew')

    return [frame, textbox]