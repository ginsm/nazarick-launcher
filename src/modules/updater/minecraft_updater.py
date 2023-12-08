import os, json, shutil
from concurrent.futures import wait
from threading import Event
from modules import view, store, utility
from modules.updater.common import *
from modules.providers.ModpackProviders import SelfHostedMinecraftModpackProvider
from modules.providers.ModProviders import ModrinthModProvider

# ----- Main Functions ----- #
def start(ctk, app, pool, widgets):
    # Define the logging function
    log = widgets.get('logbox').get('log')

    # Start logs
    log(f'')
    log(f'[INFO] Beginning process at {utility.get_time()}.')

    # Lock user input
    log(f'[INFO] Locking user input.')
    view.lock(True)

    # Initiate providers
    ModpackProvider = SelfHostedMinecraftModpackProvider()
    ModProvider = ModrinthModProvider()

    # Bundling all variables to pass them around throughout the script
    game_state = store.get_game_state('minecraft')
    options = store.get_state()
    internet_connection = utility.internet_check()
    variables = {
        'app': app,
        'ctk': ctk,
        'exepath': game_state['executable'],
        'instpath': game_state['instance'],
        'options': options,
        'root': utility.get_env('nazpath'),
        'tmp': os.path.join(utility.get_env('nazpath'), '_update_tmp', 'minecraft'),
        'widgets': widgets,
        'modprovider': ModProvider,
        'log': log,
        'version': ModpackProvider.get_latest_version('minecraft', 'nazarick-smp') if internet_connection else None,
    }

    # This represents the percentage each task (other than retrieve_mods) will increment
    # the progress bar
    task_percent = 0.25 / 9
    progressbar = widgets.get('progressbar')

    # Error Handling
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
            if (on_latest_version(variables, ModpackProvider.initial_install)):
                progressbar.add_percent(1 - (task_percent * 2))
                finalize(variables, task_percent)
                return

            # Clean up temp directory
            clean_update_directories(variables)
            progressbar.add_percent(task_percent)

            # Download latest modpack version
            ModpackProvider.download(variables)
            progressbar.add_percent(task_percent)

            # Unzip update to temp directory
            ModpackProvider.extract(variables, 'Minecraft')
            progressbar.add_percent(task_percent)

            # Purge any files as instructed from modpack archive
            purge_files(variables, pool, whitelist=['config', 'shaderpacks'])
            progressbar.add_percent(task_percent)

            # Attempt to retrieve all of the mod files
            retrieve_mods(variables, pool)

            # Install the update into the instance
            install_update(variables)
            progressbar.add_percent(task_percent)

            # Store update's version number
            store_version_number(variables)
            progressbar.add_percent(task_percent)

        except Exception as e:
            widgets.get('tabs').set('Logs')
            log(f'[WARN] {e}; terminating update process.', 'warning')
            log('[WARN] You may have trouble connecting to the server.', 'warning')

    elif not variables.get('version'):
        widgets.get('tabs').set('Logs')
        log('[WARN] Invalid response from Modrinth (modpack); skipping update process.', 'warning')
        log('[WARN] You may have trouble connecting to the server.', 'warning')

    else:
        widgets.get('tabs').set('Logs')
        log('[WARN] No internet connection; skipping update process.', 'warning')
        log('[WARN] You may have trouble connecting to the server with an outdated modpack.', 'warning')

    # Run the final bit of code
    finalize(variables, task_percent)


# This is split so that it can be ran at multiple points in the main function
def finalize(variables, task_percent):
    options, log, exe_path, widgets = [
        variables['options'],
        variables['log'],
        variables['exepath'],
        variables['widgets']
    ]
    progressbar = widgets.get('progressbar')

    log(f'[INFO] Unlocking user input.')
    view.lock(False)

    run_executable(exe_name=os.path.split(exe_path)[-1], debug=options['debug'], log=log, command=[exe_path]) 
    progressbar.add_percent(task_percent)
   
    log(f'[INFO] Finished process at {utility.get_time()}.')
    progressbar.reset_percent()
    autoclose_app(variables)


# ----- Helper Functions ----- #
def handle_errors(variables):
    log, exe_path, inst_path = [
        variables['log'],
        variables['exepath'],
        variables['instpath']
    ]
    error = False

    log('[INFO] Validating the provided executable and instance paths.')

    # Ensure the path was provided.
    if inst_path == '':
        log('[ERROR] Please provide a path to your Minecraft instance.', 'error')
        error = True
    else:
        # Ensure the path is valid.
        if not os.path.exists(inst_path):
            log("[ERROR] The provided path to your Minecraft instance doesn't exist.", 'error')
            error = True

    # Ensure the path was provided.
    if exe_path == '':
        log("[ERROR] Please provide a path to your launcher's executable.", 'error')
        error = True
    else:
        # Ensure the path is valid.
        if not os.path.isfile(exe_path):
            log("[ERROR] The provided path to your launcher doesn't exist.", 'error')
            error =  True

    if utility.permission_check(inst_path) == utility.NEED_ADMIN:
        log("[ERROR] The instance path requires administrative privileges. Please restart your launcher.", 'error')
        error = True
        
    return error


def retrieve_mods(variables, pool):
    tmp, log, inst_path = [
        variables['tmp'],
        variables['log'],
        variables['instpath']
    ]

    # read modrinth.index.json
    with open(os.path.join(tmp, 'modrinth.index.json'), 'rb') as f:
        mods = json.loads(f.read().decode('UTF-8'))['files']
        mod_progress_percent = 0.75 / len(mods)
        futures = []

        stop_processing = Event()

        log('[INFO] Retrieving any mods not present in the modpack zip:')

        for mod in mods:
            # Assign name key to mod data (used in retrieve and provider.download).
            file_name = os.path.split(mod.get('path'))[1]
            mod['name'] = file_name

            # These paths are checked for the mod in question; if it exists, it's moved
            # to the destination.
            local_paths = [
                os.path.join(inst_path, 'mods'),
                os.path.join(inst_path, 'mods-old')
            ]
            destination = os.path.join(tmp, 'overrides', 'mods', file_name)

            futures.append(pool.submit(retrieve, mod, variables, local_paths, destination, mod_progress_percent, stop_processing))

        result = wait(futures, return_when="FIRST_EXCEPTION")

        if len(result.not_done) > 0:
            stop_processing.set()
            exception = list(result.done)[-1].exception()
            raise Exception(exception)


def install_update(variables):
    inst_path, tmp, log = [
        variables['instpath'],
        variables['tmp'],
        variables['log']
    ]

    # Paths
    mods_dest = os.path.join(inst_path, 'mods')
    config_dest = os.path.join(inst_path, 'config')
    yosbr_path = os.path.join(inst_path, 'config', 'yosbr')
    mods_tmp = os.path.join(tmp, 'overrides', 'mods')
    config_tmp = os.path.join(tmp, 'overrides', 'config')

    # Remove old mods path and move updated mods to instance
    log('[INFO] Moving updated mods into the provided instance location.')
    if (os.path.exists(mods_dest)):
        shutil.rmtree(mods_dest)
    shutil.move(mods_tmp, mods_dest)

    # Remove yosbr and move updated configs to instance
    log('[INFO] Moving updated configs into the provided instance location.')
    if (os.path.exists(yosbr_path)):
        shutil.rmtree(yosbr_path)

    for file_ in os.listdir(config_tmp):
        file_path = os.path.join(config_tmp, file_)

        # Handle directories recursively (if they're not yosbr)
        if (os.path.isdir(file_path) and file_ != 'yosbr'):
            for root, _, files in os.walk(file_path):
                for name in files:
                    root_path = os.path.join(root, name)

                    # Pass everything after config as arguments for os.path.join
                    target_path = os.path.join(config_dest, root_path.replace(config_tmp, '')[1:])
                    target_root, _ = os.path.split(target_path)

                    # Ensure file's root folder exists (shutil.move gets sad about nested folders not existing)
                    if (not os.path.exists(target_root)):
                        os.makedirs(target_root)

                    shutil.move(root_path, target_path)

        # Handle top-level files by simply moving them (overwrites if it exists)
        else:
            target_path = os.path.join(config_dest, file_)
            shutil.move(file_path, target_path)