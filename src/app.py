import customtkinter as ctk
from concurrent.futures import ThreadPoolExecutor
from modules import utility, view, store, tufup, version_upgrader, theme_list
from modules.components import AppWindow, AppSideBar, MinecraftFrame, ValheimFrame, SettingsFrame

frames = []

def main():
    # Store the mod's path in environment
    utility.set_env('nazpath', tufup.BASE_DIR.as_posix())

    # Upgrade the app (converts old version conventions to newer ones)
    version_upgrader.run()

    # Initialize the store
    store.init(tufup.DATA_DIR.as_posix())
    initial_state = store.get_state()

    # Set mode
    ctk.set_appearance_mode(initial_state.get('mode') or 'System')

    # Set theme
    theme = utility.get_theme_from_title(
        initial_state.get('theme'),
        theme_list.get_themes()
    )
    ctk.set_default_color_theme(theme.get('name') if theme else 'blue')

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
    [mc_frame, mc_textbox] = MinecraftFrame.create(ctk, app, pool)
    frames.append({'name': 'Minecraft', 'frame': mc_frame, 'textbox': mc_textbox})

    [vh_frame, vh_textbox] = ValheimFrame.create(ctk, app, pool)
    frames.append({'name': 'Valheim', 'frame': vh_frame, 'textbox': vh_textbox})

    settings_frame = SettingsFrame.create(ctk, app, pool, state)
    frames.append({'name': 'Settings', 'frame': settings_frame, 'textbox': None})

    sidebar = AppSideBar.create(ctk, app, frames)
    frames.append({'name': 'Sidebar', 'frame': sidebar, 'textbox': None})

    # Position frames
    sidebar.grid(row=0, column=0, sticky='ns')
    vh_frame.grid(row=0, column=1, rowspan=len(frames), sticky='nsew')
    mc_frame.grid(row=0, column=1, rowspan=len(frames), sticky='nsew')
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


def reload_widgets(ctk, app, pool, state):
    global frames

    # Delete all frames
    for data in frames:
        frame = data['frame']
        frame.destroy()

    frames.clear()
    AppSideBar.clear_game_Buttons()

    # Recreate the frames
    create_frames(ctk, app, pool, state)


def broadcast(message):
    global frames
    for data in frames:
        textbox = data['textbox']
        if textbox:
            view.log(message, textbox)


# Run the script
if __name__ == '__main__':
    main()