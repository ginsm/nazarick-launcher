import os
import vdf
import subprocess
from modules import constants

# ---- STEAM ---- #
def find_steam():
    # Finds the path on Windows by checking registry
    if constants.ON_WINDOWS:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Software\\Valve\\Steam')
        steam_path = winreg.QueryValueEx(key, "SteamPath")[0]
        winreg.CloseKey(key)
        return steam_path


def find_steam_game(game_id, directory):
    steam_path = find_steam()
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


# ---- PowerShell ---- #
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


def find_win_folder(name):
    return run_powershell_command(f'[Environment]::GetFolderPath("{name}")')


def find_start_menu_game(name):
    path = run_powershell_command(f"(get-StartApps | Select-String \"{name}\") -replace '^.*AppID=([^!]+).*$', '$1'")

    if not path.endswith('.exe'):
        program_files_path = find_win_folder("ProgramFiles")
        path = os.path.join(program_files_path, 'WindowsApps', path)

    return path