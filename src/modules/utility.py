from datetime import datetime
from modules import constants, game_list, state_manager
from elevate import elevate
import os, ctypes, sys, subprocess


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


def respawn_launcher():
    state = state_manager.get_state()
    cmd = [sys.executable, *sys.argv]
    kwargs = dict(cwd=os.getcwd(), env=os.environ, close_fds=True)
    if constants.ON_WINDOWS:
        # create console if in debug mode
        if state.get("debug") or not constants.APP_BUNDLED:
            CREATE_NEW_CONSOLE = 0x00000010
            kwargs["creationflags"] = CREATE_NEW_CONSOLE
        # detach from the current console/window
        else:
            DETACHED_PROCESS = 0x00000008
            CREATE_NEW_PROCESS_GROUP = 0x00000200
            kwargs["creationflags"] = DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
    else:
        kwargs["start_new_session"] = True

    subprocess.Popen(cmd, **kwargs)
    os._exit(0)  # or sys.exit(0) after root.destroy()