from modules import state_manager, utility
from modules.updater.common import run_executable

# This game currently has no mods; thus the 'update' function is going to be pretty
# barren for now.
def start(ctk, app, pool, widgets, modpack):
    log = widgets.get('logbox').get('log')
    options = state_manager.get_state()

    log(f'')
    log(f'[INFO] Beginning process at {utility.get_time()}.')


    log(f'[INFO] This game doesn\'t require updates as it\'s vanilla only currently.')

    run_executable(exe_name='enshrouded.exe', debug=options['debug'], log=log, command=['cmd', '/c', 'start', 'steam://run/1203620'])