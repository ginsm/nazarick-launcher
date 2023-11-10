import os
import shutil
from modules import utility

def run():
    # (v1.2.0) The _update_tmp folder needs to be shared between the various games; currently, that folder
    # is used solely for Minecraft's updater. This method makes a new directory in _update_tmp named
    # 'Minecraft' and moves any existing files into it.
    move_minecraft_tmp()

def move_minecraft_tmp():
    current_tmp = os.path.join(utility.get_env('nazpath'), '_update_tmp')
    minecraft_tmp = os.path.join(current_tmp, 'minecraft')

    # Check if modrinth.index.json exists in _update_tmp
    if os.path.exists(os.path.join(current_tmp, 'modrinth.index.json')):
        files = os.listdir(current_tmp)
        os.makedirs(minecraft_tmp, exist_ok=True)

        for file_ in files:
            shutil.move(
                os.path.join(current_tmp, file_),
                os.path.join(minecraft_tmp, file_)
            )