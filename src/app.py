import customtkinter as ctk
from concurrent.futures import ThreadPoolExecutor
from modules import utility, view, store, tufup, version_upgrader
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
    ctk.set_appearance_mode(initial_state.get('theme'))
    ctk.set_default_color_theme(initial_state.get('accent') or 'blue')

    # Initialize tufup and check for updates (only if bundled)
    if tufup.FROZEN:
        tufup.init(initial_state)

    # Initialize the thread pool executor
    pool = ThreadPoolExecutor(max_workers=(initial_state.get('threadamount') or 4) - 1)

    # Top level components
    app = AppWindow.create(ctk, initial_state, utility.get_env('nazpath'), tufup.APP_NAME)

    # Create frames
    create_frames(ctk, app, pool, initial_state)

    # UI Events
    app.bind('<Configure>', lambda _ : view.resize(app)) # Handles saving the window size upon resize

    # Finished launching
    for frame_data in frames:
        textbox = frame_data['textbox']
        if textbox:
            view.log(f'[INFO] The app has finished initializing ({tufup.APP_VERSION}).', textbox)

    # Main loop
    app.mainloop()


def create_frames(ctk, app, pool, state):
    global frames
    # Create frames
    [vh_frame, vh_textbox] = ValheimFrame.create(ctk, app, pool)
    [mc_frame, mc_textbox] = MinecraftFrame.create(ctk, app, pool)
    settings_frame = SettingsFrame.create(ctk, app, pool, state)

    # Add frame data to frames
    frames.append({'name': 'Minecraft', 'frame': mc_frame, 'textbox': mc_textbox})
    frames.append({'name': 'Valheim', 'frame': vh_frame, 'textbox': vh_textbox})
    frames.append({'name': 'Settings', 'frame': settings_frame, 'textbox': None})

    # Create sidebar
    sidebar = AppSideBar.create(ctk, app, frames)
    frames.append({'name': 'Sidebar', 'frame': sidebar, 'textbox': None})

    # Position frames
    sidebar.grid(row=0, column=0, sticky='ns')
    vh_frame.grid(row=0, column=1, rowspan=len(frames), sticky='nsew')
    mc_frame.grid(row=0, column=1, rowspan=len(frames), sticky='nsew')
    settings_frame.grid(row=0, column=1, rowspan=len(frames), sticky='nsew')

    # Raise selected game and set color
    raise_selected_frame(frames)


def raise_selected_frame(games):
    selected_game = store.get_game()
    for game in games:
        [name, frame] = utility.destructure(game, ['name', 'frame'])
        if name.lower() == selected_game:
            frame.tkraise()
            AppSideBar.color_buttons(name)


def reload_widgets(ctk, app, pool, state):
    delete_all_frames()
    AppSideBar.clear_game_Buttons()
    create_frames(ctk, app, pool, state)


def delete_all_frames():
    global frames
    for game_data in frames:
        # Remove the frame from grid
        frame = game_data['frame']
        frame.grid_forget()
        frame.destroy()
    frames.clear()


# Run the script
if __name__ == '__main__':
    main()