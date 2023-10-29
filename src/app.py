import shutil
import customtkinter as ctk
from tufup.client import Client
from modules import utility
from modules import view
from modules import store
from modules.components import AppMenu, AppWindow
from modules.components.minecraft import MinecraftFrame
from modules.components.valheim import ValheimFrame
from modules.tufup_settings import (
    # App info
    APP_NAME, APP_VERSION, FROZEN,
    # Directories
    BASE_DIR, INSTALL_DIR, DATA_DIR, METADATA_DIR, TARGET_DIR, LOCAL_METADATA_DIR,
    # Update server urls
    METADATA_BASE_URL, TARGET_BASE_URL
)

def main():
    # Initialize tufup and check for updates (only if bundled)
    if FROZEN:
        tufup_client()

    # Store the mod's path in environment
    utility.set_env('nazpath', BASE_DIR.as_posix())

    # Initialize the store
    store.init(DATA_DIR.as_posix())
    initial_state = store.get_state()
    ctk.set_appearance_mode(initial_state.get('theme'))

    # Top level components
    app = AppWindow.create(ctk, initial_state, utility.get_env('nazpath'), APP_NAME)
    AppMenu.create(ctk, app, initial_state)

    # Create frames
    [vh_frame, vh_textbox] = ValheimFrame.create(ctk, app)
    [mc_frame, mc_textbox] = MinecraftFrame.create(ctk, app)

    # Position frames
    vh_frame.grid(row=0, column=1, sticky='nsew')
    mc_frame.grid(row=0, column=1, sticky='nsew')

    # UI Events
    app.bind('<Configure>', lambda _ : view.resize(app)) # Handles saving the window size upon resize

    # Finished launching
    for textbox in [vh_textbox, mc_textbox]:
        view.log(f'[INFO] The app has finished initializing ({APP_VERSION}).', textbox)

    # Main loop
    app.mainloop()


# Set up tufup client
def tufup_client():
    # The app must ensure dirs exist
    for dir_path in [BASE_DIR, METADATA_DIR, TARGET_DIR]:
        dir_path.mkdir(exist_ok=True, parents=True)

    # Move root.json to proper location
    source_path = LOCAL_METADATA_DIR / 'root.json'
    destination_path = METADATA_DIR / 'root.json'
    if not destination_path.exists():
        shutil.copy(src=source_path, dst=destination_path)
        print('Trusted root metadata copied to cache.')

    # Create update client
    client = Client(
        app_name=APP_NAME,
        app_install_dir=INSTALL_DIR,
        current_version=APP_VERSION,
        metadata_dir=METADATA_DIR,
        metadata_base_url=METADATA_BASE_URL,
        target_dir=TARGET_DIR,
        target_base_url=TARGET_BASE_URL,
        refresh_required=False,
    )

    # Perform update
    if client.check_for_updates():
        client.download_and_apply_update(skip_confirmation=True, log_file_name='update.log')

# Run the script
if __name__ == '__main__':
    main()