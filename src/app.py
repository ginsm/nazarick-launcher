import customtkinter as ctk
import shutil
from tufup.client import Client
from modules import utility
from modules import view
from modules import store
from modules.components import AppWindow, AppMenu, MainFrame, LogBox, InstanceEntry, ExecutableEntry, UpdateButton
from modules.tufupsettings import (
    # App info
    APP_NAME, APP_VERSION,
    # Directories
    BASE_DIR, INSTALL_DIR, DATA_DIR, METADATA_DIR, TARGET_DIR, LOCAL_METADATA_DIR,
    # Update server urls
    METADATA_BASE_URL, TARGET_BASE_URL
)

def main():
    # Initialize tufup and check for updates
    tufupClient()

    # Store the mod's path in environment
    utility.setenv("nazpath", BASE_DIR.as_posix())

    # Initialize the store
    store.init(DATA_DIR.as_posix())

    # Get state to configure the app with persistent data
    initialState = store.getState()
    ctk.set_appearance_mode(initialState.get("theme"))

    # Top level components
    app = AppWindow.create(ctk, initialState, utility.getenv("nazpath"), APP_NAME)
    AppMenu.create(ctk, app, initialState)

    # Main frame and its components
    main_frame = MainFrame.create(ctk, app)
    textbox = LogBox.create(ctk, main_frame)
    instance = InstanceEntry.create(ctk, main_frame, initialState)
    executable = ExecutableEntry.create(ctk, main_frame, initialState)
    UpdateButton.create(ctk, main_frame, instance, executable, textbox)

    # UI Events
    app.bind("<Configure>", lambda event : view.resize(event, app)) # Handles saving the window size upon resize

    # Finished launching
    view.addText(f"[INFO] The app has finished initializing ({APP_VERSION}).", textbox)

    # Main loop
    app.mainloop()


# Set up tufup client
def tufupClient():
    # The app must ensure dirs exist
    for dir_path in [BASE_DIR, METADATA_DIR, TARGET_DIR]:
        dir_path.mkdir(exist_ok=True, parents=True)

    # Move root.json to proper location
    source_path = LOCAL_METADATA_DIR / 'root.json'
    destination_path = METADATA_DIR / 'root.json'
    if not destination_path.exists():
        shutil.copy(src=source_path, dst=destination_path)
        print("Trusted root metadata copied to cache.")

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
        client.download_and_apply_update()

# Run the script
if __name__ == '__main__':
    main()