import os
import re
from uuid import UUID
import vdf
import subprocess
from modules import constants

# ---- STEAM ---- #
def get_steam_path():
    # Finds the path on Windows by checking registry
    if constants.ON_WINDOWS:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Software\\Valve\\Steam')
        steam_path = winreg.QueryValueEx(key, "SteamPath")[0]
        winreg.CloseKey(key)
        return steam_path


def get_steam_game_path(game_id, directory):
    steam_path = get_steam_path()
    libraries_path = os.path.join(steam_path, 'steamapps', 'libraryfolders.vdf')
    libraries_data = vdf.parse(open(libraries_path)).get('libraryfolders')

    # Search for steam library containing game id
    for library_id in libraries_data:
        library = libraries_data[library_id]

        if game_id in library.get('apps'):
            game_path = os.path.join(library.get('path'), 'steamapps', 'common', directory)

            # Check if game path exists and return it
            if os.path.exists(game_path):
                return game_path

    # Return false if not found
    return False


# ---- PowerShell (Windows Only) ---- #
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

        # Convert string folder_ids to proper format
        if type(folder_id) is str:
            # Convert GUID strings to UUID
            if folder_id.startswith("{"):
                folder_id = UUID(folder_id)
            # Handle plain-text folders, i.e. Documents, MyDocuments, Programs, etc.
            else:
                # Search the environment via PowerShell. This provides more accurate results.
                # Run "[enum]::GetNames( [System.Environment+SpecialFolder] )" in PowerShell to
                # see available folder locations.
                try: 
                    return run_powershell_command(f'[Environment]::GetFolderPath("{folder_id}")')
                # Fallback to searching the FOLDERID class for the folder id
                except:
                    folder_id = getattr(win_paths.FOLDERID, folder_id)

        return win_paths.get_path(folder_id)


def get_microsoft_app_dir(app_id):
    if constants.ON_WINDOWS:
        # The app dir typically has a version number sandwiched by the ID, i.e. for Minecraft Launcher:
        # AppID: Microsoft.4297127D64EC6_8wekyb3d8bbwe
        # Folder: Microsoft.4297127D64EC6_1.7.2.0_x64__8wekyb3d8bbwe
        split_path = app_id.split('_')
        windows_apps_path = os.path.join(get_win_folder("ProgramFiles"), 'WindowsApps')
        result = False

        for app_dir in os.listdir(windows_apps_path):
            # Read above; this checks for a folder containing the ID sandwiching a version number.
            if app_dir.startswith(split_path[0]) and app_dir.endswith(split_path[-1]):
                result = os.path.join(windows_apps_path, app_dir)

        return result


def get_startmenu_game_path(name, exe=''):
    if constants.ON_WINDOWS:
        # Get the AppID via PowerShell's get-StartApps
        app_id = run_powershell_command("(get-StartApps) | Where-Object { $_.Name -eq \"" + name + "\" } | Select-Object -ExpandProperty AppID")

        # Ensures the AppID ends with either .exe or !* pattern
        if not app_id.endswith('.exe') and not re.search(r'!.*$', app_id):
            raise Exception(f"Unhandled AppID for {name}: {app_id}.")
        
        # Handle KNOWNFOLDERID AppIDs
        if app_id.startswith("{"):
            import modules.path_finder.windows_paths as win_paths
            str_id = app_id[0:app_id.find("}") + 1] # Get only the UUID
            win_path = win_paths.get_path(UUID(str_id))
            app_id = app_id.replace(str_id, win_path) # Replace the UUID with the actual windows path
            
        # Handle Microsoft Store Apps' AppIDs
        if re.search(r'!.*$', app_id):
            app_id = app_id[0:app_id.find("!")] # Remove !* from the end of the line
            game_dir = get_microsoft_app_dir(app_id)
            app_id = os.path.join(game_dir, exe) if game_dir else False

        return app_id