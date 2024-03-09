import os, shutil
import traceback
from modules.updater.common import *
from modules import filesystem, system_check, view, utility, store


# ----- Main Functions ----- #
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
    try:
        ModpackProvider = providers.get('modpack')()
        ModProvider = providers.get('mods')()
    except Exception as e:
        log('[ERROR] Unable to initialize provider:', 'error')
        log(f'[ERROR] {e}', 'error')
        log('[INFO] Terminating update process.')
        traceback.print_exc()
        view.lock(False)
        return

    # Bundling all variables to pass them around throughout the script
    game_state = store.get_pack_state('minecraft')
    options = store.get_state()
    internet_connection = system_check.check_internet()
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
        'version': ModpackProvider.get_latest_modpack_version('minecraft', modpack) if internet_connection else None,
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
            if (on_latest_version(variables, ModpackProvider.initial_modpack_install)):
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
            ModpackProvider.extract_modpack(variables, 'Minecraft', modpack.get('name'))
            progressbar.add_percent(task_percent)

            # Purge any files as instructed from modpack archive
            purge_files(variables, pool, whitelist=['config', 'shaderpacks'])
            progressbar.add_percent(task_percent)

            # Attempt to retrieve all of the mod files
            destination = os.path.join(variables.get('tmp'), 'overrides', 'mods')
            inst_path = variables.get('instpath')
            local_paths = [
                os.path.join(inst_path, 'mods'),
                os.path.join(inst_path, 'mods-old'),
                destination
            ]
            mod_index = retrieve_mods(variables, destination, local_paths, pool)

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
            traceback.print_exc()

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

    if system_check.check_perms(inst_path) == system_check.NEED_ADMIN:
        log("[ERROR] The instance path requires administrative privileges. Please restart your launcher.", 'error')
        error = True
        
    return error


def install_update(variables, pool):
    tmp, log = [
        variables['tmp'],
        variables['log']
    ]

    mods_tmp = os.path.join(tmp, 'overrides', 'mods')
    custommods_tmp = os.path.join(tmp, 'custommods')

    log('[INFO] Installing the modpack to the specified instance path.')

    # Move user added mods to the tmp path
    custommods = os.listdir(custommods_tmp)
    os.chdir(tmp)
    
    if os.path.exists(custommods_tmp):
        for mod in custommods:
            shutil.move(
                os.path.join(custommods_tmp, mod),
                os.path.join(mods_tmp, mod)
            )

    # Move overrides to main destination
    futures = []

    override_directory = os.path.join(tmp, 'overrides')
    for override in os.listdir(override_directory):
        futures.append(
            pool.submit(move_override, variables, override)
        )

    wait(futures)


def move_override(variables, override):
    inst_path, tmp_path = [
        variables.get('instpath'),
        variables.get('tmp')
    ]

    override_path = os.path.join(tmp_path, 'overrides', override)
    destination = os.path.join(inst_path, override)

    # Ensure program is not operating in override or destination locations
    if os.getcwd() in [override_path, destination]:
        os.chdir(tmp_path)

    # Move files without overwriting user-added files
    match override:
        case 'mods' | 'scripts' | 'packmenu' | 'patchouli_books':
            filesystem.move_files(override_path, destination)
        case _:
            filesystem.move_files(override_path, destination, overwrite=False)