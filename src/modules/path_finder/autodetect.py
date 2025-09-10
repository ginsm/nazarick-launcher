import os
from modules import gui_manager, state_manager
from modules.components.common import CoverFrame
from modules.path_finder import finder

PLATFORM_CONVENTION = {
    'Steam': 'steam',
    'Microsoft Store': 'storeapp',
    'Epic Games': 'epic',
    'win_folder': 'win_folder'
}
PLATFORM_CONVENTIONS = list(PLATFORM_CONVENTION.keys())


def get_platform_choices(settings):
    for setting in settings:
        if setting.get('name') == 'platform':
            return setting.get('choices')
    return None


def get_platform_data(setting, platform):
    return setting.get(PLATFORM_CONVENTION[platform])


def detect_generic_path(setting, platforms=PLATFORM_CONVENTIONS):
    for platform in platforms:
        # Get platform data
        platform_data = get_platform_data(setting, platform)

        # Find path based on game_id
        if platform_data:
            ID = platform_data.get('ID')
            game_path = finder.find_appid_path(ID, PLATFORM_CONVENTION[platform])

            # Append exe if it exists
            if game_path and platform_data.get('exe'):
                game_path = os.path.join(game_path, platform_data.get('exe'))

            # Return found path and platform
            if game_path:
                return [game_path, platform]

    return None


def detect_install_path(pack_state, setting, settings):
    platforms = get_platform_choices(settings) or PLATFORM_CONVENTIONS
    platform = pack_state.get('platform')

    if platform:
        # Remove platform from list and insert it at the beginning so it's checked first
        platforms.remove(platform)
        platforms.insert(0, platform)

    return detect_generic_path(setting, platforms)


def autodetect_settings(ctk, app, game, settings, pool):
    def autodetect():
        pack = state_manager.get_selected_pack(game)
        pack_state = state_manager.get_pack_state(game, pack)
        original_state = pack_state.copy()
        detected_path = None

        gui_manager.lock(True)

        for setting in settings:
            if setting.get('type') in ['directory', 'file']:
                setting_name = setting.get('name')

                # Do not touch non-empty settings.
                if not pack_state.get(setting_name):
                    # Detect the path based on name
                    match setting_name:
                        case 'install' | 'instance':
                                detected_path = detect_install_path(pack_state, setting, settings)
                        case _:
                            detected_path = detect_generic_path(setting)

                    # Check if the path was properly detected
                    if detected_path:
                        [game_path, platform] = detected_path

                        # Update the platform setting if its the install/instance setting
                        if setting_name in ['install', 'instance']:
                            pack_state.update({'platform': platform})

                        # Update the install setting and commit to persistent state
                        pack_state.update({ setting_name: game_path})
                        state_manager.set_pack_state(pack_state, game, pack)

                        # Reset detected_path variable
                        detected_path = None

        # Reload frame if settings have changed
        if original_state != pack_state:
            cover_frame = CoverFrame.create(ctk, app)
            gui_manager.reload_frame(ctk, app, pool, game, cover_frame)
            cover_frame.destroy()

        gui_manager.lock(False)
    
    return autodetect