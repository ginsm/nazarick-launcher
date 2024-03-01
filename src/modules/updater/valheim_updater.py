import os, json, shutil
from threading import Event
from modules.updater.common import *
from concurrent.futures import wait
from modules import view, utility, store

def start(ctk, app, pool, widgets, modpack):
    # Define the logging function
    log = widgets.get('logbox').get('log')

    # Start logs
    log(f'')
    log(f'[INFO] Beginning process at {utility.get_time()}.')

    # Lock user input
    log(f'[INFO] Locking user input.')
    view.lock(True)

    # Initiate providers
    providers = modpack.get('providers')
    ModpackProvider = providers.get('modpack')()
    ModProvider = providers.get('mods')()

    # Bundling all variables to pass them around throughout the script
    game_state = store.get_game_state('valheim')
    options = store.get_state()
    internet_connection = utility.internet_check()
    variables = {
        'app': app,
        'ctk': ctk,
        'instpath': game_state['install'],
        'options': options,
        'root': utility.get_env('nazpath'),
        'tmp': os.path.join(utility.get_env('nazpath'), '_update_tmp', 'valheim'),
        'widgets': widgets,
        'modprovider': ModProvider,
        'log': log,
        'version': ModpackProvider.get_latest_modpack_version('valheim', modpack) if internet_connection else None
    }
    
    # This represents the percentage each task (other than retrieve_mods) will increment
    # the progress bar.
    task_percent = 0.25 / 10
    progressbar = widgets.get('progressbar')

    if handle_errors(variables):
        # Switch to logs tab
        widgets.get('tabs').set('Logs')

        # Unlock user input
        log(f'[INFO] Unlocking user input.')
        view.lock(False)
        log(f'[INFO] Finished process at {utility.get_time()}.')
        return
    
    # This is ran after each task (aside from retrieve_mods)
    progressbar.add_percent(task_percent)
    
    if internet_connection and variables.get('version'):
        try:
            # Skips update process if they're already on the latest version
            if on_latest_version(variables):
                progressbar.add_percent(1 - (task_percent * 2))
                finalize(variables, task_percent)
                return

            # Clean up temp directory
            clean_update_directories(variables)
            progressbar.add_percent(task_percent)

            # Download latest modpack version
            ModpackProvider.download_modpack(variables)
            progressbar.add_percent(task_percent)

            # Unzip update to temp directory
            ModpackProvider.extract_modpack(variables, 'Valheim', modpack.get('name'))
            progressbar.add_percent(task_percent)

            # Purge any files as instructed from modpack archive
            purge_files(variables, pool, whitelist=['BepInEx/config'])
            progressbar.add_percent(task_percent)

            # Attempt to retrieve all of the mod files.
            # Returns the mod index, aka a list of all mods in the pack; this is
            # used for custom mods.
            mod_index = retrieve_mods(variables, pool)

            # FIXME - This was causing the updater to stall.
            # Get version data and move custom mods
            # version_data = get_version_data(variables)
            # if version_data.get('mod_index'):
            #     ModProvider.move_custom_mods(
            #         variables,
            #         version_data.get('mod_index')
            #     )
            # progressbar.add_percent(task_percent)

            # Install the update into the instance
            install_update(variables, pool)
            progressbar.add_percent(task_percent)

            # Store update's version number
            store_version_data(variables, mod_index)
            progressbar.add_percent(task_percent)

        except Exception as e:
            widgets.get('tabs').set('Logs')
            log(f'[WARN] {e}; terminating update process.', 'warning')
            log('[WARN] You may have trouble connecting to the server.', 'warning')
        
    elif not variables.get('version'):
        widgets.get('tabs').set('Logs')
        log('[WARN] Invalid response from Thunderstore (modpack); skipping update process.', 'warning')
        log('[WARN] You may have trouble connecting to the server.', 'warning')
    else:
        widgets.get('tabs').set('Logs')
        log('[WARN] No internet connection; skipping update process.', 'warning')
        log('[WARN] You may have trouble connecting to the server with an outdated modpack.', 'warning')

    finalize(variables, task_percent)


# This is split so that it can be ran at multiple points in the main function
def finalize(variables, task_percent):
    options, log, widgets = [
        variables['options'],
        variables['log'],
        variables['widgets']
    ]

    progressbar = widgets.get('progressbar')

    log(f'[INFO] Unlocking user input.')
    view.lock(False)
    
    # TODO - Support launching with mac as well
    run_executable(exe_name='valheim.exe', debug=options['debug'], log=log, command=['cmd', '/c', 'start', 'steam://run/892970'])
    progressbar.add_percent(task_percent)

    log(f'[INFO] Finished process at {utility.get_time()}.')
    progressbar.reset_percent()
    autoclose_app(variables)


# ----- Helper Functions ----- #
def handle_errors(variables):
    log, inst_path = [
        variables['log'],
        variables['instpath'],
    ]
    error = False

    log('[INFO] Validating the provided install path.')

    # Ensure the path was provided.
    if inst_path == '':
        log('[ERROR] Please provide a path to your Valheim instance.', 'error')
        error = True
    elif not os.path.exists(inst_path):
        log("[ERROR] The provided path to your Valheim instance doesn't exist.", 'error')
        error = True

    if utility.permission_check(inst_path) == utility.NEED_ADMIN:
        log('[ERROR] The install path requires administrative privileges. Please restart your launcher.', 'error')
        error = True

    return error


def retrieve_mods(variables, pool):
    tmp, log, inst_path = [
        variables['tmp'],
        variables['log'],
        variables['instpath']
    ]

    # Make a plugins folder
    plugins_tmp = os.path.join(tmp, 'plugins')
    os.makedirs(plugins_tmp, exist_ok=True)

    # Read manifest.json
    with open(os.path.join(tmp, 'manifest.json'), 'rb') as f:
        plugins = json.loads(f.read().decode('UTF-8'))['dependencies']
        plugin_progress_percent = 0.75 / len(plugins)
        futures = []

        stop_processing = Event()

        log('[INFO] Retrieving modpack dependencies.')

        for plugin in plugins:
            mod_data = {'name': plugin}
            # These paths are checked for the mod in question; if it exists, it's moved
            # to the destination.
            local_paths = [
                os.path.join(inst_path, 'BepInEx', 'plugins')
            ]
            destination = os.path.join(tmp, 'plugins', plugin)

            futures.append(pool.submit(retrieve, mod_data, variables, local_paths, destination, plugin_progress_percent, stop_processing))

        result = wait(futures, return_when="FIRST_EXCEPTION")

        if len(result.not_done) > 0:
            stop_processing.set()
            exception = list(result.done)[-1].exception()
            raise Exception(exception)
    
    return os.listdir(plugins_tmp)


def install_update(variables, pool):
    inst_path, tmp, log = [
        variables['instpath'],
        variables['tmp'],
        variables['log']
    ]

    # Set up BepInEx
    setup_bepinex(variables, pool)

    # Move BepInEx files
    install_tmp = os.path.join(tmp, 'install')

    # Iterate over install directory
    log('[INFO] Installing the modpack to the specified install path.')
    for file_ in os.listdir(install_tmp):
        file_path_loc = os.path.join(inst_path, file_)
        file_path_tmp = os.path.join(install_tmp, file_)

        # Handle the BepInEx directory
        if file_ == 'BepInEx':
            for bepinex_file in os.listdir(file_path_tmp):
                bf_path_loc = os.path.join(file_path_loc, bepinex_file)
                bf_path_tmp = os.path.join(file_path_tmp, bepinex_file)

                # Handle the config directory
                if bepinex_file == 'config':
                    for config in os.listdir(bf_path_tmp):
                        config_path_loc = os.path.join(bf_path_loc, config)
                        config_path_tmp = os.path.join(bf_path_tmp, config)
                        loc_root, _ = os.path.split(config_path_loc)

                        # Do not overwrite existing configs
                        # Note: If a config needs to be replaced, add it to the modpack's launcher.json purge list.
                        if os.path.exists(config_path_loc):
                            continue
                        
                        if not os.path.exists(loc_root):
                            os.makedirs(loc_root)

                        shutil.move(config_path_tmp, config_path_loc)
                else:
                    overwrite(bf_path_tmp, bf_path_loc)
        else:
            overwrite(file_path_tmp, file_path_loc)


def setup_bepinex(variables, pool):
    tmp, log = [
        variables['tmp'],
        variables['log']
    ]

    # Paths
    plugins_tmp = os.path.join(tmp, 'plugins')
    config_tmp = os.path.join(tmp, 'config')
    custommods_tmp = os.path.join(tmp, 'custommods')
    install_tmp = os.path.join(tmp, 'install')

    # Make install directory
    os.makedirs(install_tmp, exist_ok=True)

    log('[INFO] Setting up BepInEx.')

    # Move BepInEx into install directory
    for plugin in os.listdir(plugins_tmp):
        if 'BepInExPack' in plugin:
            bepinex_path = os.path.join(plugins_tmp, plugin, 'BepInExPack_Valheim')
            files = os.listdir(bepinex_path)
            futures = []

            for f in files:
                futures.append(pool.submit(
                    shutil.move,
                    os.path.join(bepinex_path, f),
                    os.path.join(install_tmp, f)
                ))

            wait(futures)
            
            # Remove BepInEx directory
            shutil.rmtree(os.path.join(plugins_tmp, plugin))
            break

    # Move plugins and configs to new BepInEx structure
    futures = []

    # Move plugins
    for plugin in os.listdir(plugins_tmp):
        futures.append(pool.submit(
            shutil.move,
            os.path.join(plugins_tmp, plugin),
            os.path.join(install_tmp, 'BepInEx', 'plugins', plugin)
        ))

    # Move configs
    for config in os.listdir(config_tmp):
        futures.append(pool.submit(
            shutil.move,
            os.path.join(config_tmp, config),
            os.path.join(install_tmp, 'BepInEx', 'config', config)
        ))

    # Move custom plugins
    if os.path.exists(custommods_tmp):
        for plugin in os.listdir(custommods_tmp):
            futures.append(pool.submit(
                shutil.move,
                os.path.join(custommods_tmp, plugin),
                os.path.join(install_tmp, 'BepInEx', 'plugins', plugin)
            ))

    wait(futures)