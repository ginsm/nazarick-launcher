import sys, pathlib, os, shutil, logging, webbrowser
from modules import constants
from customtkinter.windows.widgets.theme import ThemeManager
from tufup.client import Client
from tuf.api.exceptions import ExpiredMetadataError

from modules.components.common import InfoModal

logger = logging.getLogger(constants.LOGGER_NAME)

# Set rootpath
INSTALL_DIR = constants.APP_BASE_DIR.parent

# For development
DEV_DIR = constants.APP_BASE_DIR.parent / 'pyinstaller' / 'temp'

# This is used to copy the trusted root metadata directly from the repo dir or BASE_DIR
LOCAL_METADATA_DIR = constants.APP_BASE_DIR if constants.APP_BUNDLED else DEV_DIR / 'repository' / 'metadata'

# Get and set storage path
if constants.ON_WINDOWS:
    PER_USER_DATA_DIR = pathlib.Path(os.getenv('LOCALAPPDATA'))
elif constants.ON_MAC:
    PER_USER_DATA_DIR = pathlib.Path.home() / 'Library'
else:
    raise NotImplementedError('Unsupported platform')

# App directories
DATA_DIR = PER_USER_DATA_DIR / constants.APP_NAME if constants.APP_BUNDLED else DEV_DIR / constants.APP_NAME
UPDATE_CACHE_DIR = DATA_DIR / 'update_cache'
METADATA_DIR = UPDATE_CACHE_DIR / 'metadata'
TARGET_DIR = UPDATE_CACHE_DIR / 'targets'

# Update server urls
if constants.APP_BUNDLED:
    METADATA_BASE_URL = 'https://mgin.me/nazarick-launcher/repo/metadata/'
    TARGET_BASE_URL = 'https://mgin.me/nazarick-launcher/repo/targets/'
else:
    METADATA_BASE_URL = 'http://localhost:8000/metadata/'
    TARGET_BASE_URL = 'http://localhost:8000/targets/'

INIT_SUCCESS = 'success'
INIT_FAILED = 'failed'

# Set up tufup client
def init(initial_state):
    try:
        # The app must ensure dirs exist
        for dir_path in [constants.APP_BASE_DIR, METADATA_DIR, TARGET_DIR]:
            dir_path.mkdir(exist_ok=True, parents=True)

        # Move root.json to proper location
        source_path = LOCAL_METADATA_DIR / 'root.json'
        destination_path = METADATA_DIR / 'root.json'
        if not destination_path.exists():
            shutil.copy(src=source_path, dst=destination_path)
            print('Trusted root metadata copied to cache.')

        # Create update client
        client = Client(
            app_name=constants.APP_NAME,
            app_install_dir=INSTALL_DIR,
            current_version=constants.APP_VERSION,
            metadata_dir=METADATA_DIR,
            metadata_base_url=METADATA_BASE_URL,
            target_dir=TARGET_DIR,
            target_base_url=TARGET_BASE_URL,
            refresh_required=False,
        )

        # Perform update
        if client.check_for_updates():
            if initial_state.get('autorestart'):
                custom_batch_template = """@echo off
                {log_lines}
                echo Moving app files...
                robocopy "{src_dir}" "{dst_dir}" {robocopy_options}
                echo Done.
                echo Restarting app
                start "" "{app_exe_path}"
                {delete_self}
                """

                client.download_and_apply_update(
                    skip_confirmation=True,
                    log_file_name='logs/app-update.log',
                    batch_template=custom_batch_template,
                    batch_template_extra_kwargs=dict(app_exe_path=sys.executable),
                )
            else:
                client.download_and_apply_update(
                    skip_confirmation=True,
                    log_file_name='logs/app-update.log'
                )

        return INIT_SUCCESS
    except Exception as e:
        return e

def handle_error(ctk, error):
    if isinstance(error, ExpiredMetadataError):
        logger.warning("Tufup: " + str(error))
    else:
        border_color = ThemeManager.theme.get("CTkCheckBox").get("border_color")
        InfoModal.create(
            ctk=ctk,
            title="Error: Update Failed",
            text="The launcher tried to update itself but ran into issues. As such, the launcher may not function properly.\n\nYou can either try to use the launcher without updating or download the most recent version and update it manually.",
            max_width=350,
            buttons=[
                {"text": "Cancel", "command": lambda modal: modal.destroy()},
                {
                    "text": "Download",
                    "command": lambda _: webbrowser.open(
                        "https://github.com/ginsm/nazarick-launcher/releases/latest/download/Nazarick.Launcher.zip"
                    ),
                    "border": border_color,
                },
            ],
        )

    pass
