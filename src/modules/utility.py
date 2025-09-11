from datetime import datetime
from modules import constants, game_list
from elevate import elevate
import os, ctypes


def get_time():
    return datetime.now().strftime('%m/%d/%Y %H:%M:%S')


def get_modpack_data(game, modpack):
    for game_dict in game_list.LIST:
        if game_dict.get('name').lower() == game.lower() and game_dict.get('modpacks'):
            for pack in game_dict.get('modpacks'):
                if pack.get('name').lower() == modpack.lower():
                    return pack
    return {}


def running_as_admin():
    if constants.ON_WINDOWS:
        try:
            return bool(ctypes.windll.shell32.IsUserAnAdmin())
        except Exception:
            return False
    else:
        return os.geteuid() == 0
    

def normalize_dir(path):
    """ Normalizes the path and returns it if it's safe """
    if not path: return None
    p = os.path.normpath(path.strip().strip('"'))
    return p if os.path.isdir(p) else None


def elevate_launcher(app):
    app.destroy()
    app.quit()
    elevate(show_console=False)