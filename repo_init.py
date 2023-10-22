
from tufup.repo import Repository

from src.modules.tufupsettings import APP_NAME
from repo_settings import (
    # Settings
    ENCRYPTED_KEYS,
    EXPIRATION_DAYS,
    KEY_MAP,
    THRESHOLDS,
    # Directories
    KEYS_DIR,
    REPO_DIR,
    OFFLINE_DIR_1,
    OFFLINE_DIR_2,
    ONLINE_DIR
)

if __name__ == '__main__':
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