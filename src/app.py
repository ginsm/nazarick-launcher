from concurrent.futures import ThreadPoolExecutor
import customtkinter as ctk
from elevate import elevate
from modules import game_list, utility, view, store, tufup, version_upgrader, theme_list
from modules.components import AppWindow, AppSideBar, SettingsFrame
from modules.components.common import GameFrame

frames = []

def main():
    # Store the mod's path in environment
    utility.set_env('nazpath', tufup.BASE_DIR.as_posix())

    # Upgrade the app (converts old version conventions to newer ones)
    version_upgrader.run()

    # Initialize the store
    store.init(tufup.DATA_DIR.as_posix())
    initial_state = store.get_state()

    # Check if elevated permission is necessary
    permission_check_failed = utility.some(
        store.get_game_paths(),
        lambda v: utility.permission_check(v) == utility.NEED_ADMIN
    )
    if (permission_check_failed):
        elevate(show_console=False)

    # Set mode
    ctk.set_appearance_mode(initial_state.get('mode') or 'System')

    # Set theme
    theme = theme_list.get_theme_from_title(initial_state.get('theme'))
    ctk.set_default_color_theme(theme.get('name'))

    # Initialize tufup and check for updates (only if bundled)
    if tufup.FROZEN:
        tufup.init(initial_state)

    # Initialize the thread pool executor
    threadamount = initial_state.get('threadamount') or 4
    pool = ThreadPoolExecutor(max_workers=threadamount - 1)

    # Top level components
    app = AppWindow.create(ctk, initial_state, utility.get_env('nazpath'), tufup.APP_NAME)

    # Create frames
    create_frames(ctk, app, pool, initial_state)

    # UI Events
    app.bind('<Configure>', lambda _ : view.resize(app)) # Handles saving the window size upon resize

    # Finished launching
    broadcast(f'[INFO] The app has finished initializing ({tufup.APP_VERSION}).')

    # Main loop
    app.mainloop()


def create_frames(ctk, app, pool, state):
    global frames

    # Create frames and add their data to frames
    games = game_list.LIST
    for game in games:
        [frame, textbox] = GameFrame.create(ctk, app, pool, **game)
        frames.append({'name': game.get('name'), 'frame': frame, 'textbox': textbox})
        frame.grid(row=0, column=1, rowspan=len(games) + 2, sticky='nsew')

    settings_frame = SettingsFrame.create(ctk, app, pool, state)
    frames.append({'name': 'Settings', 'frame': settings_frame, 'textbox': None})

    sidebar = AppSideBar.create(ctk, app, frames)
    frames.append({'name': 'Sidebar', 'frame': sidebar, 'textbox': None})

    # Position frames
    sidebar.grid(row=0, column=0, sticky='ns')
    settings_frame.grid(row=0, column=1, rowspan=len(frames), sticky='nsew')

    # Raise selected frame and set color
    raise_selected_frame(frames)

def raise_selected_frame(games):
    selected_game = store.get_game()
    for game in games:
        [name, frame] = utility.destructure(game, ['name', 'frame'])
        if name.lower() == selected_game:
            frame.tkraise()
            AppSideBar.color_buttons(name)

def broadcast(message):
    global frames

    for data in frames:
        textbox = data['textbox']
        if textbox:
            textbox['log'](message)


def reload_widgets(ctk, app, pool, state):
    global frames

    # Delete all frames
    for data in frames:
        frame = data['frame']
        frame.destroy()

    # Clear all stored widgets
    frames.clear()
    AppSideBar.clear_game_Buttons()
    view.clear_lockable_elements()

    # Recreate the frames
    create_frames(ctk, app, pool, state)


# Run the script
if __name__ == '__main__':
    main()