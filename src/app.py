from concurrent.futures import ThreadPoolExecutor
import webbrowser
import customtkinter as ctk
from customtkinter.windows.widgets.theme import ThemeManager
from elevate import elevate
from modules import app_upgrader, system_check, utility, view, store, tufup, constants, theme_list, frames
from modules.components import AppWindow
from modules.components.common import InfoModal

def main():
    # Store the mod's path in environment
    utility.set_env('nazpath', constants.APP_BASE_DIR.as_posix())

    # Initialize the store
    store.init(tufup.DATA_DIR.as_posix())
    initial_state = store.get_state()
    
    # Upgrade the app (converts old version conventions to newer ones)
    app_upgrader.run()

    # Check if elevated permission is necessary
    permission_check_failed = utility.some(
        store.get_game_paths(),
        lambda v: system_check.check_perms(v) == system_check.NEED_ADMIN
    )
    if (permission_check_failed):
        elevate(show_console=False)

    # Set mode
    ctk.set_appearance_mode(initial_state.get('mode') or 'System')

    # Set theme
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

    # Top level components
    app = AppWindow.create(ctk, initial_state, utility.get_env('nazpath'), constants.APP_NAME)
    app.grid_rowconfigure(0, weight=1)

    # Create frames
    frames.create_frames(ctk, app, pool, initial_state)

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

    # UI Events
    app.bind('<Configure>', lambda _ : view.resize(app)) # Handles saving the window size upon resize

    # Finished launching
    frames.broadcast(f'[INFO] The app has finished initializing ({constants.APP_VERSION}).')

    # Main loop
    app.mainloop()


# Run the script
if __name__ == '__main__':
    main()