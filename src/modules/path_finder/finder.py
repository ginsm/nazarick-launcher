import os
import re
from uuid import UUID
import vdf
import subprocess
from modules import constants


# ---- Steam Specific ---- #
def get_steam_path():
    # Finds the path on Windows by checking registry
    if constants.ON_WINDOWS:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Software\\Valve\\Steam')
        steam_path = winreg.QueryValueEx(key, "SteamPath")[0]
        winreg.CloseKey(key)
        return steam_path


def get_steam_game_installdir(library, game_id):
    manifest_path = os.path.join(library.get('path'), 'steamapps', f'appmanifest_{game_id}.acf')

    # Parse manifest to find the game's install directory
    with open(manifest_path, 'r') as fp:
        install_dir = vdf.loads(fp.read()).get('AppState').get('installdir')
    
    return install_dir


def get_steam_game_path(game_id):
    steam_path = get_steam_path()
    libraries_path = os.path.join(steam_path, 'steamapps', 'libraryfolders.vdf')
    libraries_data = vdf.parse(open(libraries_path)).get('libraryfolders')

    # Handle steam AppIDs
    if game_id.startswith('steam://run'):
        game_id = game_id.split("/")[-1]

    # Search for steam library containing game id
    for library_id in libraries_data:
        library = libraries_data[library_id]

        if game_id in library.get('apps'):
            install_dir = get_steam_game_installdir(library, game_id)

            # Create path to install directory
            game_path = os.path.join(library.get('path'), 'steamapps', 'common', install_dir)

            # Check if game path exists and return it
            if os.path.exists(game_path):
                return game_path

    # Return None if not found
    return None


# ---- Windows Specific ---- #
def run_powershell_command(command):
    # This can only be used on windows
    if not constants.ON_WINDOWS:
        return False

    path = subprocess.run(
        ["powershell", "-Command", command],
        capture_output=True,
        text=True # Returns output as string without needing to decode
    )

    if path.returncode != 0:
        raise Exception(path.stderr)

    return path.stdout.strip()


def get_win_folder(folder_id):
    if constants.ON_WINDOWS:
        import modules.path_finder.windows_paths as win_paths

        # Search the environment via PowerShell. This provides more accurate results.
        # Run "[enum]::GetNames( [System.Environment+SpecialFolder] )" in PowerShell to
        # see available folder locations.
        try: 
            return run_powershell_command(f'[Environment]::GetFolderPath("{folder_id}")')
        # Fallback to searching the FOLDERID class for the folder id and using get_path
        except:
            folder_id = getattr(win_paths.FOLDERID, folder_id)
            return win_paths.get_path(folder_id)


def get_appid_from_startmenu(name):
    """ Gets the Start Menu AppID for an app (must be an exact match). """
    if constants.ON_WINDOWS:
        cmd = "(get-StartApps) | Where-Object { $_.Name -eq \"" + name + "\" } | Select-Object -ExpandProperty AppID"
        return run_powershell_command(cmd)


def handle_knownfile_appids(appid):
    if constants.ON_WINDOWS:
        import modules.path_finder.windows_paths as win_paths
        str_id = appid[0:appid.find("}") + 1]
        guid = UUID(str_id)
        return appid.replace(str_id, win_paths.get_path(guid))


def handle_storeapp_appids(appid):
    appid = appid[0:appid.find('!')]
    if constants.ON_WINDOWS:
        # The app dir typically has a version number sandwiched by the ID, i.e. for Minecraft Launcher:
        # AppID: Microsoft.4297127D64EC6_8wekyb3d8bbwe
        # Folder: Microsoft.4297127D64EC6_1.7.2.0_x64__8wekyb3d8bbwe
        split_path = appid.split('_')
        windows_apps_path = os.path.join(get_win_folder("ProgramFiles"), 'WindowsApps')
        game_dir = False

        for app_dir in os.listdir(windows_apps_path):
            # Read above; this checks for a folder containing the ID sandwiching a version number.
            if app_dir.startswith(split_path[0]) and app_dir.endswith(split_path[-1]):
                game_dir = os.path.join(windows_apps_path, app_dir)

        return game_dir


# ---- Main Functionality ---- #
def get_appid_convention(string):
    """ Determines the AppID convention. 
    
    Conventions: `path`, `application`, `steam`, `knownfile`, and `storeapp`. """
    conventions = {
        # r'^[\w]+\.[\w.]+$': 'namespace',
        r'^[A-Za-z]:\\.*\\.*\.exe$': 'path',
        r'^[A-Za-z0-9]+$': 'application',
        r'^steam:\/\/(run|rungameid)\/\d+$': 'steam',
        r'\{.*\}': 'knownfile',
        r'^.*![\w\.]+$': 'storeapp'
    }

    for pattern, name in conventions.items():
        if re.match(pattern, string):
            return name
    return None


def find_appid_path(appid):
    """ Searches for the path based on the AppID and its convention. """
    convention = get_appid_convention(appid)
    match convention:
        case 'path':
            return appid
        case 'application':
            return appid
        case 'steam':
            return get_steam_game_path(appid)
        case 'knownfile':
            return handle_knownfile_appids(appid)
        case 'storeapp':
            return handle_storeapp_appids(appid)
        case _:
            raise Exception(f'AppID type is unhandled: {appid}')
