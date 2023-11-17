import sys, pathlib, os, shutil
from tufup.client import Client
from tufup.utils.platform_specific import ON_MAC, ON_WINDOWS

# App info
APP_VERSION = '1.2.4'
APP_NAME = 'Nazarick_Launcher'

# Are we running in a PyInstaller bundle?
# https://pyinstaller.org/en/stable/runtime-information.html
FROZEN = getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')

# Get module directory path and set rootpath
BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
INSTALL_DIR = BASE_DIR.parent

# For development
DEV_DIR = BASE_DIR.parent / 'pyinstaller' / 'temp'

# This is used to copy the trusted root metadata directly from the repo dir or BASE_DIR
LOCAL_METADATA_DIR = BASE_DIR if FROZEN else DEV_DIR / 'repository' / 'metadata'

# Get and set config path
if ON_WINDOWS:
    PER_USER_DATA_DIR = pathlib.Path(os.getenv('LOCALAPPDATA'))
elif ON_MAC:
    PER_USER_DATA_DIR = pathlib.Path.home() / 'Library'
else:
    raise NotImplementedError('Unsupported platform')

# App directories
DATA_DIR = PER_USER_DATA_DIR / APP_NAME if FROZEN else DEV_DIR / APP_NAME
UPDATE_CACHE_DIR = DATA_DIR / 'update_cache'
METADATA_DIR = UPDATE_CACHE_DIR / 'metadata'
TARGET_DIR = UPDATE_CACHE_DIR / 'targets'

# Update server urls
if FROZEN:
    METADATA_BASE_URL = 'https://mgin.me/nazarick-launcher/repo/metadata/'
    TARGET_BASE_URL = 'https://mgin.me/nazarick-launcher/repo/targets/'
else:
    METADATA_BASE_URL = 'http://localhost:8000/metadata/'
    TARGET_BASE_URL = 'http://localhost:8000/targets/'

# Set up tufup client
def init(initial_state):
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
                log_file_name='update.log',
                batch_template=custom_batch_template,
                batch_template_extra_kwargs=dict(app_exe_path=sys.executable),
            )
        else:
            client.download_and_apply_update(
                skip_confirmation=True,
                log_file_name='update.log'
            )