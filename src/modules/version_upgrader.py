import os
import shutil
from modules import constants, game_list, store, utility

def run():
    move_minecraft_tmp()
    move_changelogs()


# (v1.2.0) The _update_tmp folder needs to be shared between the various games; currently, that folder
# is used solely for Minecraft's updater. This method makes a new directory in _update_tmp named
# 'Minecraft' and moves any existing files into it.
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


# (v1.4.6) Adding multiple modpack support per game. As such, the changelog should be stored in a sub
# folder representing the pack.. not just in the game folder.
def move_changelogs():
    for game in game_list.LIST:
        name = game.get('name')
        pack = store.get_selected_pack(name)

        old_changelog_path = os.path.join(constants.APP_BASE_DIR, 'assets', name, 'CHANGELOG.md')
        new_changelog_path = os.path.join(constants.APP_BASE_DIR, 'assets', name, pack, 'CHANGELOG.md')

        if os.path.exists(old_changelog_path):
            os.makedirs(os.path.split(new_changelog_path)[0], exist_ok=True)
            shutil.move(old_changelog_path, new_changelog_path)


def rename_nazarick_smp_state():
    pass