import shutil
import customtkinter as ctk
from tufup.client import Client
from concurrent.futures import ThreadPoolExecutor
from modules import utility
from modules import view
from modules import store
from modules import tufup
from modules.components import AppMenu, AppWindow, AppSideBar
from modules.components.minecraft import MinecraftFrame
from modules.components.valheim import ValheimFrame

def main():
    # Initialize tufup and check for updates (only if bundled)
    if tufup.FROZEN:
        tufup.init()

    # Store the mod's path in environment
    utility.set_env('nazpath', tufup.BASE_DIR.as_posix())

    # Initialize the store
    store.init(tufup.DATA_DIR.as_posix())
    initial_state = store.get_state()
    ctk.set_appearance_mode(initial_state.get('theme'))

    # Initialize the thread pool executor
    pool = ThreadPoolExecutor(max_workers=3)

    # Top level components
    app = AppWindow.create(ctk, initial_state, utility.get_env('nazpath'), tufup.APP_NAME)
    AppMenu.create(ctk, app, initial_state)

    # Create frames
    [vh_frame, vh_textbox] = ValheimFrame.create(ctk, app, pool)
    [mc_frame, mc_textbox] = MinecraftFrame.create(ctk, app, pool)

    games = [
        {'name': 'Minecraft', 'frame': mc_frame},
        {'name': 'Valheim', 'frame': vh_frame},
    ]

    vh_frame.grid(row=0, column=1, rowspan=len(games), sticky='nsew')
    mc_frame.grid(row=0, column=1, rowspan=len(games), sticky='nsew')

    # Add side bar
    sidebar = AppSideBar.create(ctk, app, games)
    sidebar.grid(row=0, column=0, sticky='ns')

    # Raise selected game and set color
    raise_selected_game(games)

    # UI Events
    app.bind('<Configure>', lambda _ : view.resize(app)) # Handles saving the window size upon resize

    # Finished launching
    for textbox in [vh_textbox, mc_textbox]:
        view.log(f'[INFO] The app has finished initializing ({tufup.APP_VERSION}).', textbox)

    # Main loop
    app.mainloop()

def raise_selected_game(games):
    selected_game = store.get_game()
    for game in games:
        [name, frame] = utility.destructure(game, ['name', 'frame'])
        if name.lower() == selected_game:
            frame.tkraise()
            AppSideBar.color_buttons(name)

# Run the script
if __name__ == '__main__':
    main()