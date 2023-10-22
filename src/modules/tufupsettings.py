# These are settings for tufup.
# See here: https://github.com/dennisvang/tufup

import sys
import pathlib
import os
from tufup.utils.platform_specific import ON_MAC, ON_WINDOWS

# App info
APP_NAME = "Nazarick Launcher"
APP_VERSION = "1.0.3"

# Are we running in a PyInstaller bundle?
# https://pyinstaller.org/en/stable/runtime-information.html
FROZEN = getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')

# Get module directory path and set rootpath
BASE_DIR = pathlib.Path(__file__).resolve().parent.parent

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
METADATA_BASE_URL = 'http://localhost:8000/metadata/'
TARGET_BASE_URL = 'http://localhost:8000/targets/'