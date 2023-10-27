from tufup.repo import Repository
from repo_settings import ONLINE_DIR

# Initialize repo from config
repo = Repository.from_config()

# Re-sign expired roles (downstream roles are refreshed automatically)
repo.refresh_expiration_date(role_name='snapshot', days=9)
repo.publish_changes(private_key_dirs=[ONLINE_DIR])