import sys
import pathlib
import copy
from tufup.repo import (
    Repository,
    DEFAULT_KEY_MAP, 
    DEFAULT_KEYS_DIR_NAME, 
    DEFAULT_REPO_DIR_NAME
)
from src.modules.constants import APP_NAME, APP_VERSION

def run_operation():
    # Get operation and run accompanying function
    operation = sys.argv[1] if len(sys.argv) > 1 else ''
    arguments = sys.argv[2:]

    match operation:
        case 'bundle':
            bundle(arguments)
        case 'init':
            init(arguments)
        case 'sign':
            sign(arguments)
        case _:
            print('Usage: python repository.py <operation> [arguments]\nOperations: bundle [required], init, sign')

# SETTINGS
# Paths to tufup and bundled app
BASE_DIR = pathlib.Path(__file__).resolve().parent
TUFUP_DIR = BASE_DIR / 'tufup'
BUNDLE_DIR = BASE_DIR / 'pyinstaller' / 'dist'

# Local repo path and keys path (would normally be offline)
KEYS_DIR = TUFUP_DIR / DEFAULT_KEYS_DIR_NAME
ONLINE_DIR = KEYS_DIR / 'online_secrets'
OFFLINE_DIR_1 = KEYS_DIR / 'offline_secrets_1'
OFFLINE_DIR_2 = KEYS_DIR / 'offline_secrets_2'
REPO_DIR = TUFUP_DIR / DEFAULT_REPO_DIR_NAME

# Key settings
EXPIRATION_DAYS = dict(root=365, targets=100, snapshot=14, timestamp=14)
THRESHOLDS = dict(root=2, targets=1, snapshot=1, timestamp=1)
KEY_MAP = copy.deepcopy(DEFAULT_KEY_MAP)
KEY_MAP['root'].append('root_two') # use two keys for root
ENCRYPTED_KEYS=['root', 'root_two', 'targets']

# OPERATIONS
def init(_):
    # Create repository instance
    repo = Repository(
        app_name=APP_NAME,
        repo_dir=REPO_DIR,
        keys_dir=KEYS_DIR,
        key_map=KEY_MAP,
        expiration_days=EXPIRATION_DAYS,
        encrypted_keys=ENCRYPTED_KEYS,
        thresholds=THRESHOLDS,
    )

    # Save configuration (JSON file)
    repo.save_config()

    # Initialize repository (creates keys and root metadata, if necessary)
    repo.initialize()

    # The keys are initially created in the same dir, but the private keys must
    # remain secret, so we typically want to move them to different locations.
    for private_key_name, dst_dir in [
        ('root', OFFLINE_DIR_1),
        ('root_two', OFFLINE_DIR_2),
        ('targets', OFFLINE_DIR_1),
        ('snapshot', ONLINE_DIR),
        ('timestamp', ONLINE_DIR),
    ]:
        private_key_path = KEYS_DIR / private_key_name
        if private_key_path.exists():
            dst_dir.mkdir(exist_ok=True)
            private_key_path.rename(dst_dir / private_key_name)

    print("Done.")

def bundle(arguments):
    # Create archive from latest pyinstaller bundle (assuming we have already
    # created a pyinstaller bundle, and there is only one).
    try:
        bundle_dirs = [path for path in BUNDLE_DIR.iterdir() if path.is_dir()]
    except FileNotFoundError:
        sys.exit(f'Directory not found: {BUNDLE_DIR}\nDid you run pyinstaller?')
    if len(bundle_dirs) != 1:
        sys.exit(f'Expected one bundle, found {len(bundle_dirs)}.')
    bundle_dir = bundle_dirs[0]
    print(f'Adding bundle: {bundle_dir}')

    # Create repository instance from config file (assuming the repository
    # has already been initialized)
    repo = Repository.from_config()

    # Configure the bundle
    config = {
        'new_version': APP_VERSION,
        'new_bundle_dir': bundle_dir
    }

    if '--required' in arguments or '-r' in arguments:
        config.update({'required': True})

    # Add new app bundle to repository
    repo.add_bundle(**config)
    repo.publish_changes(private_key_dirs=[OFFLINE_DIR_1, ONLINE_DIR])

    print('Done.')

def sign(_):
    # Initialize repo from config
    repo = Repository.from_config()

    # Re-sign expired roles (downstream roles are refreshed automatically)
    repo.refresh_expiration_date(role_name='snapshot', days=9)
    repo.publish_changes(private_key_dirs=[ONLINE_DIR])

    print("Done.")

run_operation()