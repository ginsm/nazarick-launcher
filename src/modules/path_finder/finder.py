import os, re, vdf, subprocess, json, glob
from uuid import UUID
from modules import constants, utility
from modules.exceptions import MissingAppIDError, InvalidAppIDTypeError, MissingSteamPathError, PowerShellCommandError

# ---- Epic Specific ---- #
def find_epic_game_path(game_id):
    for f in glob.glob(r"C:\ProgramData\Epic\EpicGamesLauncher\Data\Manifests\*.item"):
        try:
            data = json.loads(open(f, "r", encoding="utf-8").read().strip())
            location = utility.normalize_dir(data.get("InstallLocation"))
            name = (data.get("DisplayName") or data.get("AppName") or "").lower()
            if location and (game_id in name):
                return location
        except Exception:
            continue
    return None


# ---- Steam Specific ---- #
def find_steam_path():
    # Finds the path on Windows by checking registry
    if constants.ON_WINDOWS:
        steam_path = None
        try:
            # Check the registery for steam's path
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Software\\Valve\\Steam')
            steam_path = winreg.QueryValueEx(key, "SteamPath")[0]
            winreg.CloseKey(key)
        except:
            # Otherwise attempt to find the path via the start menu
            steam_appid = get_location_from_startmenu("Steam")
            if steam_appid:
                steam_path = find_appid_path(steam_appid)
                if steam_path:
                    # Remove any instance of 'steam.exe' from steam_path
                    steam_path = steam_path.lower().replace('steam.exe', '')

        return steam_path


def get_steam_game_installdir(library_path, game_id):
    manifest_path = os.path.join(library_path, 'steamapps', f'appmanifest_{game_id}.acf')

    # Parse manifest to find the game's install directory
    if os.path.exists(manifest_path):
        with open(manifest_path, 'r') as fp:
            install_dir = vdf.loads(fp.read()).get('AppState').get('installdir')
        
        return install_dir
    
    return None


def get_steam_game_path(game_id):
    steam_path = find_steam_path()

    if not steam_path:
        raise MissingSteamPathError("Could not find steam path.")

    libraries_path = os.path.join(steam_path, 'steamapps', 'libraryfolders.vdf')
    libraries_data = vdf.parse(open(libraries_path)).get('libraryfolders')

    for library_id in libraries_data:
        library = libraries_data.get(library_id)
        library_path = library.get('path')
        install_dir = get_steam_game_installdir(library_path, game_id)

        if install_dir:
            game_path = os.path.join(library_path, 'steamapps', 'common', install_dir)

            if os.path.exists(game_path):
                return game_path

    return None


# ---- Windows Specific ---- #
def find_knownfile_paths(appid):
    if constants.ON_WINDOWS:
        import modules.path_finder.knownpaths as win_paths
        str_id = appid[0:appid.find("}") + 1]
        guid = UUID(str_id)
        return appid.replace(str_id, win_paths.get_path(guid, win_paths.UserHandle.current))


def find_default_windows_path(folder):
    """ Leverages the knownpath wrapper to locate 'special' Windows folders.
     
    See the 'FOLDERID' class in knownpaths.py for list of folders."""
    if constants.ON_WINDOWS:
        import modules.path_finder.knownpaths as win_paths
        # Get ID from FOLDERID class if folder is a string
        if type(folder) is str:
            folder = getattr(win_paths.FOLDERID, folder)
        return win_paths.get_path(folder, win_paths.UserHandle.current)


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
        raise PowerShellCommandError(
            f"Command failed (rc={path.returncode}): {command}\nSTDERR:\n{path.stderr}"
        )

    return path.stdout.strip()


def get_location_from_startmenu(appid):
    """ Gets the Start Menu location for an app (must be an exact match). """
    if not constants.ON_WINDOWS:
        return None
    cmd = "(get-StartApps) | Where-Object { $_.Name -eq \"" + appid + "\" } | Select-Object -ExpandProperty AppID"
    return run_powershell_command(cmd)


def get_appx_install_location(appid):
    if not constants.ON_WINDOWS:
        return None
    try:
        path = utility.normalize_dir(
            run_powershell_command(f"(Get-AppxPackage -Name '{appid}').InstallLocation")
        )
        if path and os.path.isdir(path):
            return path
    except Exception:
        pass
    return None


def find_store_app_location(appid):
    if not constants.ON_WINDOWS:
        return None
    # The app dir typically has a version number sandwiched by the ID, i.e. for Minecraft Launcher:
    # AppID: Microsoft.4297127D64EC6_8wekyb3d8bbwe
    # Folder: Microsoft.4297127D64EC6_1.7.2.0_x64__8wekyb3d8bbwe
    split_path = appid.split('_')
    package_name = split_path[0]
    family_suffix = split_path[-1]    

    windows_apps_path = os.path.join(find_default_windows_path("ProgramFiles"), 'WindowsApps')

    # Try to get the path without admin
    appx_install_loc = get_appx_install_location(package_name)
    if appx_install_loc:
        return appx_install_loc

    if not utility.running_as_admin():
        return None
    
    try:
        if not os.path.isdir(windows_apps_path):
            return None

        with os.scandir(windows_apps_path) as it:
            for entry in it:
                if not entry.is_dir():
                    continue
                name = entry.name
                # Read above; this checks for a folder containing the ID sandwiching a version number.
                if name.startswith(package_name) and name.endswith(family_suffix):
                    return os.path.join(windows_apps_path, name)
    # Even elevated, ACLs can still block access
    except (PermissionError, OSError):
        return None

    return None
    

# ---- Main Functionality ---- #
def get_appid_convention(appid):
    """ Determines the AppID convention. 
    
    Conventions: `path`, `application`, `steam`, `knownfile`, and `storeapp`. """
    conventions = {
        # r'^[\w]+\.[\w.]+$': 'namespace',
        r'^[A-Za-z]:\\.*\\.*\.exe$': 'path',
        r'^[A-Za-z0-9]+$': 'application',
        r'^steam:\/\/\d+$': 'steam',
        r'\{.*\}': 'knownfile',
        r'^.*![\w\.]+$': 'storeapp'
    }

    for pattern, name in conventions.items():
        if re.match(pattern, appid):
            return name

    return None


def normalize_appid(appid, convention):
    match convention:
        case 'steam':
            if appid.startswith('steam://'):
                return appid.split("/")[-1]
        case 'storeapp':
            if '!' in appid:
                return appid[0:appid.find('!')]
    
    return appid


def find_appid_path(appid, convention=None):
    """ Searches for the path based on the AppID and its convention. """
    if not appid:
        raise MissingAppIDError('The provided AppID was empty.')

    if not convention:
        convention = get_appid_convention(appid)

    appid = normalize_appid(appid, convention)

    match convention:
        case 'path' | 'application':
            return appid
        case 'steam':
            return get_steam_game_path(appid)
        case 'epic':
            return find_epic_game_path(appid)
        case 'storeapp':
            return find_store_app_location(appid)
        case 'win_folder':
            return find_default_windows_path(appid)
        case 'knownfile':
            return find_knownfile_paths(appid)
        case _:
            raise InvalidAppIDTypeError(f'AppID type ({convention}) is unhandled by find_appid_path: {appid}')