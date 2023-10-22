import pathlib
import copy

from tufup.repo import (
    DEFAULT_KEY_MAP, 
    DEFAULT_KEYS_DIR_NAME, 
    DEFAULT_REPO_DIR_NAME,
    DEFAULT_META_DIR_NAME,
    DEFAULT_TARGETS_DIR_NAME
)

# App info
APP_NAME="Nazarick Launcher"

# Path to directory containing current module
BASE_DIR = pathlib.Path(__file__).resolve().parent

# For development
DEV_DIR = BASE_DIR / 'pyinstaller' / 'temp'
DIST_DIR = DEV_DIR / 'dist'

# Local repo path and keys path (would normally be offline)
KEYS_DIR = BASE_DIR / DEFAULT_KEYS_DIR_NAME
ONLINE_DIR = KEYS_DIR / 'online_secrets'
OFFLINE_DIR_1 = KEYS_DIR / 'offline_secrets_1'
OFFLINE_DIR_2 = KEYS_DIR / 'offline_secrets_2'
REPO_DIR = DEV_DIR / DEFAULT_REPO_DIR_NAME
META_DIR = REPO_DIR / DEFAULT_META_DIR_NAME
TARGETS_DIR = REPO_DIR / DEFAULT_TARGETS_DIR_NAME

# Key settings
EXPIRATION_DAYS = dict(root=365, targets=100, snapshot=7, timestamp=1)
THRESHOLDS = dict(root=2, targets=1, snapshot=1, timestamp=1)
KEY_MAP = copy.deepcopy(DEFAULT_KEY_MAP)
KEY_MAP['root'].append('root_two') # use two keys for root
ENCRYPTED_KEYS=['root', 'root_two', 'targets']