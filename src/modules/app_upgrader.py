import os
import shutil
from modules import constants, game_list, state_manager, theme_list

def run():
    _move_minecraft_tmp_1_2_0()
    _move_changelogs_1_4_6()
    _update_state()

    for game in game_list.LIST:
        state_manager.create_game_state(game)

# ---- General Upgraders ---- #
# The _update_tmp folder needs to be shared between the various games; currently, that folder
# is used solely for Minecraft's updater. This method makes a new directory in _update_tmp named
# 'Minecraft' and moves any existing files into it.
def _move_minecraft_tmp_1_2_0():
    current_tmp = os.path.join(os.environ.get('nazpath'), '_update_tmp')
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


# Adding multiple modpack support per game. As such, the changelog should be stored in a sub
# folder representing the pack.. not just in the game folder.
def _move_changelogs_1_4_6():
    for game in game_list.LIST:
        name = game.get('name')
        pack = state_manager.get_selected_pack(name)
        if pack:
            old_changelog_path = os.path.join(constants.APP_BASE_DIR, 'assets', name, 'CHANGELOG.md')
            new_changelog_path = os.path.join(constants.APP_BASE_DIR, 'assets', name, pack, 'CHANGELOG.md')

            if os.path.exists(old_changelog_path):
                os.makedirs(os.path.split(new_changelog_path)[0], exist_ok=True)
                shutil.move(old_changelog_path, new_changelog_path)


# ---- Store Updater ---- #
def _update_state():
    state = state_manager.get_state()

    # Run updaters
    state = _update_1_0_7(state)
    state = _update_1_3_0(state)
    state = _update_1_4_1(state)

    state_manager.set_state_doc(state)


def _update_1_4_1(state):
    # Rename 'game' to frame
    game = state.get('game')
    if game:
        state.update({'frame': game})
        del state['game']

    # Add tab state
    if not state.get('tab'):
        state.update({'tab': {
            'minecraft': 'Settings',
            'valheim': 'Settings'
        }})
        
    return state


def _update_1_3_0(state):
    # Remove unused variables

    # v1.4.1 - Removed since 'frame' is now used.
    # if state.get('frame'):
    #     del state['frame']

    if state.get('accent'):
        del state['accent']

    # Move to new theme/mode convention
    if state.get('theme') in ['System', 'Dark', 'Light']:
        mode = state.get('theme')
        state.update({'mode': mode, 'theme': 'Blue'})

    # Prevent malformed/invalid theme name issues
    themes = list(map(lambda o: o.get('title'), theme_list.get_themes()))
    if state.get('theme') not in themes:
        state.update({'theme': 'Blue'})

    return state


# Version 1.0.7 state updater
def _update_1_0_7(state):
    # Check if the state is old 1.0.6 format
    if state.get('executable'):
        executable = state['executable']
        instance = state['instance']

        # Update data
        stateUpdate = {
            'game': 'minecraft',
            'games': {
                'minecraft': {
                    'selectedpack': 'nazarick-smp',
                    'nazarick-smp': {
                        'instance': instance,
                        'executable': executable
                    }
                },
                'valheim': {
                    'selectedpack': 'nazarick-smp',
                    'nazarick-smp': {
                        'install': ''
                    }
                }
            }
        }

        # Remove old unused keys
        del state['executable']
        del state['instance']

        # Update the state
        state.update(stateUpdate)

    # Return the updated state
    return state