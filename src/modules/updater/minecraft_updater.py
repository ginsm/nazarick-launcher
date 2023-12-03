import os, subprocess, json, zipfile, shutil, requests
from concurrent.futures import wait
from modules import view, store, utility
from modules.components.common import ChangesBox
from modules.tufup import BASE_DIR
from modules.updater.common import *

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
        'log': log,
        'version': get_latest_version('1.20.1') if internet_connection else None,
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
    
    # Skip updating process if nuver is equal to latest ver
    if internet_connection:
        if (on_latest_version(variables, initial_install)):
            progressbar.add_percent(1 - (task_percent * 2))
            finalize(variables, task_percent)
            return

        # Clean up temp directory
        clean_update_directories(variables)
        progressbar.add_percent(task_percent)

        # Download latest modpack version
        download_modpack(variables)
        progressbar.add_percent(task_percent)

        # Unzip update to temp directory
        extract_modpack(variables)
        progressbar.add_percent(task_percent)

        # Purge any files as instructed from modpack archive
        purge_files(variables, pool, whitelist=['config', 'shaderpacks'])
        progressbar.add_percent(task_percent)

        # Retrieve all of the mod files
        retrieve_mods(variables, pool)

        # Install the update into the instance
        install_update(variables)
        progressbar.add_percent(task_percent)

        # Store update's version number
        store_version_number(variables)
        progressbar.add_percent(task_percent)
    else:
        log('[INFO] No internet connection; skipping update process.')

    # Run the final bit of code
    finalize(variables, task_percent)


# This is split so that it can be ran at multiple points in the main function
def finalize(vars_, task_percent):
    options, log, exe_path, widgets = [
        vars_['options'],
        vars_['log'],
        vars_['exepath'],
        vars_['widgets']
    ]
    progressbar = widgets.get('progressbar')

    log(f'[INFO] Unlocking user input.')
    view.lock(False)

    run_executable(exe_name=os.path.split(exe_path)[-1], debug=options['debug'], log=log, command=[exe_path]) 
    progressbar.add_percent(task_percent)
   
    log(f'[INFO] Finished process at {utility.get_time()}.')
    progressbar.reset_percent()
    autoclose_app(vars_)


# ----- Helper Functions ----- #
def handle_errors(vars_):
    log, exe_path, inst_path = [
        vars_['log'],
        vars_['exepath'],
        vars_['instpath']
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


def get_latest_version(version):
    def parse_json(obj):
        return {
            'name': ' '.join(obj['name'].split(" ")[:-1]),
            'url': obj['files'][0]['url'],
            'version': obj['version_number']
        }
    
    req = requests.get(f'https://api.modrinth.com/v2/project/nazarick-smp/version?game_versions=["{version}"]')
    data = json.loads(req.text)
    parsed = list(map(parse_json, data))
    return parsed[0]


def initial_install(vars_):
    inst_path = vars_['instpath']
    configpath = os.path.join(inst_path, 'config')
    modspath = os.path.join(inst_path, 'mods')

    def move_existing_files(path):
        if os.path.exists(path):
            os.rename(path, f'{path}-old')

    move_existing_files(configpath)
    move_existing_files(modspath)


def download_modpack(vars_):
    log, tmp, version = [
        vars_['log'],
        vars_['tmp'],
        vars_['version']
    ]

    log(f'[INFO] Downloading latest version: {version['name']} v{version['version']}.')

    # Download the mrpack as .zip
    req = requests.get(version['url'], allow_redirects=True)
    open(os.path.join(tmp, 'update.zip'), 'wb').write(req.content)


def extract_modpack(vars_):
    ctk, log, tmp, widgets = [
        vars_['ctk'],
        vars_['log'],
        vars_['tmp'],
        vars_['widgets']
    ]

    zip_file = os.path.join(tmp, 'update.zip')

    log('[INFO] Extracting the modpack zip.')
    with zipfile.ZipFile(zip_file, 'r') as ref:
        ref.extractall(tmp)
    
    # Remove update.zip
    os.remove(zip_file)

    # Move the changelog to its destination
    extract_modpack_changelog(vars_, 'Minecraft')


def retrieve_mods(vars_, pool):
    tmp, log = [
        vars_['tmp'],
        vars_['log'],
    ]

    # read modrinth.index.json
    with open(os.path.join(tmp, 'modrinth.index.json'), 'rb') as f:
        mods = json.loads(f.read().decode('UTF-8'))['files']
        mod_progress_percent = 0.75 / len(mods)
        futures = []

        log('[INFO] Retrieving any mods not present in the modpack zip:')

        for mod in mods:
            futures.append(pool.submit(retrieve, mod, vars_, mod_progress_percent))

        wait(futures)


def retrieve(mod, vars_, mod_percent):
    _, name = os.path.split(mod['path'])
    log, inst_path, tmp, widgets = [
        vars_['log'],
        vars_['instpath'],
        vars_['tmp'],
        vars_['widgets']
    ]
    progressbar = widgets.get('progressbar')

    # Split path to get mod name and join with instpath
    local_path = os.path.join(inst_path, 'mods', name)
    local_path_old = os.path.join(inst_path, 'mods-old', name)
    destination = os.path.join(tmp, 'overrides', 'mods', name)

    # Move file if it exists locally
    if os.path.isfile(local_path):
        log(f'[INFO] (M) {name.split('.jar')[0]}.')
        if not os.path.isfile(destination):
            shutil.move(local_path, destination)
    # Move file if it exists locally (initial install)
    elif os.path.isfile(local_path_old):
        log(f'[INFO] (C) {name.split('.jar')[0]}.')
        if not os.path.isfile(destination):
            shutil.copyfile(local_path_old, destination)
    # Download mod
    else:
        log(f'[INFO] (D) {name.split('.jar')[0]}.')
        req = requests.get(mod['downloads'][0], allow_redirects=True)
        open(destination, 'wb').write(req.content)
    
    progressbar.add_percent(mod_percent)


def install_update(vars_):
    inst_path, tmp, log = [
        vars_['instpath'],
        vars_['tmp'],
        vars_['log']
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