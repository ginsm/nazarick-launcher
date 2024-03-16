from concurrent.futures import ThreadPoolExecutor
import os, webbrowser
import customtkinter as ctk
from customtkinter.windows.widgets.theme import ThemeManager
from elevate import elevate
from modules import app_upgrader, gui_manager, state_manager, system_check, tufup, constants, theme_list
from modules.components import AppWindow
from modules.components.common import InfoModal

def main():
    # Store the mod's path in environment
    BASE_DIR = os.path.abspath(constants.APP_BASE_DIR)
    os.environ['nazpath'] = BASE_DIR

    # Initialize the store
    state_manager.init(tufup.DATA_DIR.as_posix())
    initial_state = state_manager.get_state()
    
    # Upgrade the app (converts old version conventions to newer ones)
    app_upgrader.run()

    # Check if launcher needs to be elevated
    game_paths = state_manager.get_game_paths()
    if system_check.elevation_needed(game_paths):
        elevate(show_console=False)

    # Set appearance
    ctk.set_appearance_mode(initial_state.get('mode') or 'System')
    theme = theme_list.get_theme_from_title(initial_state.get('theme'))
    ctk.set_default_color_theme(theme.get('name'))

    # Initialize tufup and check for updates (only if bundled)
    if constants.APP_BUNDLED:
        tufup_status = tufup.init(initial_state)
    else:
        tufup_status = tufup.INIT_SUCCESS

    # Initialize the thread pool executor
    threadamount = initial_state.get('threadamount') or 4
    pool = ThreadPoolExecutor(max_workers=threadamount - 1)

    # Create the top level component
    app = AppWindow.create(ctk, initial_state, BASE_DIR, constants.APP_NAME)
    app.grid_rowconfigure(0, weight=1)

    # Creates the rest of the GUI dynamically
    gui_manager.create_gui(ctk, app, pool, initial_state)

    # Handle tufup running into issues
    if tufup_status == tufup.INIT_FAILED:
        border_color = ThemeManager.theme.get('CTkCheckBox').get('border_color')
        InfoModal.create(
            ctk=ctk,
            title='Error: Update Failed',
            text='The launcher tried to update itself but ran into issues. As such, the launcher may not function properly.\n\nYou can either try to use the launcher without updating or download the most recent version and update it manually.',
            max_width=350,
            buttons=[
                {'text': 'Cancel', 'command': lambda modal: modal.destroy()},
                {'text': 'Download', 'command': lambda _: webbrowser.open('https://github.com/ginsm/nazarick-launcher/releases/latest/download/Nazarick.Launcher.zip'), 'border': border_color}
            ])

    # UI Event Handlers
    app.bind('<Configure>', lambda _ : gui_manager.resize(app)) # Handles saving the window size upon resize

    # Finished launching
    gui_manager.broadcast(f'[INFO] The app has finished initializing ({constants.APP_VERSION}).')

    # Main loop
    app.mainloop()


# Run the script
if __name__ == '__main__':
    main()