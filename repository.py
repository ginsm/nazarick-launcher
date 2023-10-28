import sys
from tufup.repo import Repository
from src.modules.tufup_settings import APP_NAME, APP_VERSION
from repository_settings import (
    # Settings
    ENCRYPTED_KEYS,
    EXPIRATION_DAYS,
    KEY_MAP,
    THRESHOLDS,
    # Directories
    DIST_DIR,
    KEYS_DIR,
    REPO_DIR,
    OFFLINE_DIR_1,
    OFFLINE_DIR_2,
    ONLINE_DIR
)

def run_operation():
    # Get operation and run accompanying function
    operation = sys.argv[1]

    match operation:
        case 'bundle':
            bundle()
        case 'init':
            init()
        case 'sign':
            sign()
        case _:
            print('Usage: python repository.py <operation>\nOperations: bundle, init, sign')

def init():
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

def bundle():
    # Create archive from latest pyinstaller bundle (assuming we have already
    # created a pyinstaller bundle, and there is only one).
    try:
        bundle_dirs = [path for path in DIST_DIR.iterdir() if path.is_dir()]
    except FileNotFoundError:
        sys.exit(f'Directory not found: {DIST_DIR}\nDid you run pyinstaller?')
    if len(bundle_dirs) != 1:
        sys.exit(f'Expected one bundle, found {len(bundle_dirs)}.')
    bundle_dir = bundle_dirs[0]
    print(f'Adding bundle: {bundle_dir}')

    # Create repository instance from config file (assuming the repository
    # has already been initialized)
    repo = Repository.from_config()

    # Add new app bundle to repository
    repo.add_bundle(new_version=APP_VERSION, new_bundle_dir=bundle_dir)
    repo.publish_changes(private_key_dirs=[OFFLINE_DIR_1, ONLINE_DIR])

    print('Done.')

def sign():
    # Initialize repo from config
    repo = Repository.from_config()

    # Re-sign expired roles (downstream roles are refreshed automatically)
    repo.refresh_expiration_date(role_name='snapshot', days=9)
    repo.publish_changes(private_key_dirs=[ONLINE_DIR])

run_operation()