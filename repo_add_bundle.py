import sys
from tufup.repo import Repository
from src.modules.tufupsettings import APP_VERSION
from repo_settings import (
    DIST_DIR,
    OFFLINE_DIR_1,
    ONLINE_DIR
)


if __name__ == '__main__':
    # create archive from latest pyinstaller bundle (assuming we have already
    # created a pyinstaller bundle, and there is only one)
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