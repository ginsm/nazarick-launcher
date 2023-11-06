import os
import subprocess
import json
import zipfile
import shutil
from concurrent.futures import wait
import requests
from modules import view
from modules.utility import get_env, get_time, can_delete_path
from modules import store

# ----- Main Functions ----- #
def start(app, ctk, textbox, pool):
    view.log(f'', textbox)
    view.log(f'[INFO] Beginning process at {get_time()}.', textbox)

    # Lock user input
    view.log(f'[INFO] Locking user input.', textbox)
    view.lock(True)

    # Bundling all variables to pass them around throughout the script
    game_state = store.get_game_state('minecraft')
    options = store.get_state()
    variables = {
        'app': app,
        'ctk': ctk,
        'exepath': game_state['executable'],
        'instpath': game_state['instance'],
        'options': options,
        'root': get_env('nazpath'),
        'tmp': os.path.join(get_env('nazpath'), '_update_tmp'),
        'textbox': textbox,
        'version': get_latest_version('1.20.1'),
    }

    # Error Handling
    if (handle_errors(variables)):
        view.log(f'[INFO] Unlocking user input.', textbox)
        view.lock(False)
        view.log(f'[INFO] Finished process at {get_time()}.', textbox)
        return
    
    # Skip updating process if nuver is equal to latest ver
    if (on_latest_version(variables)):
        finalize(variables)
        return

    # Clean up temp directory
    clean_update_directories(variables)

    # Download latest modpack version
    download_modpack(variables)

    # Unzip update to temp directory
    extract_modpack(variables)

    # Purge any files as instructed from modpack archive
    purge_files(variables, pool)

    # Retrieve all of the mod files
    retrieve_mods(variables, pool)

    # Install the update into the instance
    install_update(variables)

    # Store update's version number
    store_version_number(variables)

    # Run the final bit of code
    finalize(variables)


# This is split so that it can be ran after resume_update finishes or before updating (if nuver is equal to
# latest ver)
def finalize(vars_):
    options, textbox, exe_path, app = [
        vars_['options'],
        vars_['textbox'],
        vars_['exepath'],
        vars_['app']
    ]

    # Unlock the program
    view.log(f'[INFO] Unlocking user input.', textbox)
    view.lock(False)

    # Debug mode stops exe from launching
    if (not options['debug']):
        executed = execute_launcher(textbox=textbox, exe_path=exe_path)
        if (not executed):
            return
    else:
        view.log('[INFO] The executable is not launched whilst in debug mode.', textbox)

                    
    view.log(f'[INFO] Finished process at {get_time()}.', textbox)

    # Check if auto close is enabled; close if so
    if (options['autoclose']):
        view.log('[INFO] Auto close is enabled; closing app.', textbox)
        app.quit()


# ----- Helper Functions ----- #
def handle_errors(vars_):
    textbox, exe_path, inst_path = [
        vars_['textbox'],
        vars_['exepath'],
        vars_['instpath']
    ]
    error = False

    view.log('[INFO] Validating the provided executable and instance paths.', textbox)

    # Ensure the path was provided.
    if inst_path == '':
        view.log('[ERROR] Please provide a path to your Minecraft instance.', textbox)
        error = True
    else:
        # Ensure the path is valid.
        if not os.path.exists(inst_path):
            view.log("[ERROR] The provided path to your Minecraft instance doesn't exist.", textbox)
            error = True

    # Ensure the path was provided.
    if exe_path == '':
        view.log("[ERROR] Please provide a path to your launcher's executable.", textbox)
        error= True
    else:
        # Ensure the path is valid.
        if not os.path.isfile(exe_path):
            view.log("[ERROR] The provided path to your launcher doesn't exist.", textbox)
            error =  True
        
    
    return error


def clean_update_directories(vars_):
    tmp, textbox = [
        vars_['tmp'],
        vars_['textbox']
    ]
    # Delete any existing tmp directory
    if os.path.exists(tmp):
        view.log('[INFO] Pruning old tmp directory.', textbox)
        shutil.rmtree(tmp)
    else:
        view.log('[INFO] Creating tmp directory.', textbox)

    # Create clean tmp directory
    os.mkdir(tmp)


def get_latest_version(version):
    def parse_json(obj):
        return {
            'name': obj['name'],
            'url': obj['files'][0]['url']
        }
    
    req = requests.get(f'https://api.modrinth.com/v2/project/nazarick-smp/version?game_versions=["{version}"]')
    data = json.loads(req.text)
    parsed = list(map(parse_json, data))
    return parsed[0]


def on_latest_version(vars_):
    version_name, inst_path = [
        vars_['version']['name'],
        vars_['instpath']
    ]
    nuver_path = os.path.join(inst_path, 'nuver')

    # Handle existing install
    if (os.path.exists(nuver_path)):
        with open(os.path.join(inst_path, 'nuver'), 'rb') as f:
            last_version_name = f.read().decode('UTF-8')
            if (version_name == last_version_name):
                view.log(f'[INFO] You are already on the latest version ({version_name}).', vars_['textbox'])
                return True
            
    # Handle first install
    else:
        view.log('[INFO] Preparing instance for initial install.', vars_['textbox'])
        configpath = os.path.join(inst_path, 'config')
        modspath = os.path.join(inst_path, 'mods')

        def move_existing_files(path):
            if os.path.exists(path):
                os.rename(path, f'{path}-old')

        move_existing_files(configpath)
        move_existing_files(modspath)

        return False


def store_version_number(vars_):
    version_name, textbox, inst_path = [
        vars_['version']['name'],
        vars_['textbox'],
        vars_['instpath']
    ]

    view.log(f'[INFO] Storing new version ID for future ref: {version_name}.', textbox)
    open(os.path.join(inst_path, 'nuver'), 'w').write(version_name)


def download_modpack(vars_):
    textbox, tmp, version = [
        vars_['textbox'],
        vars_['tmp'],
        vars_['version']
    ]

    view.log(f'[INFO] Downloading latest version: {version['name']}.', textbox)

    # Download the mrpack as .zip
    req = requests.get(version['url'], allow_redirects=True)
    open(os.path.join(tmp, 'update.zip'), 'wb').write(req.content)


def extract_modpack(vars_):
    textbox, tmp = [
        vars_['textbox'],
        vars_['tmp']
    ]

    view.log('[INFO] Extracting the modpack zip.', textbox)
    with zipfile.ZipFile(os.path.join(tmp, 'update.zip'), 'r') as ref:
        ref.extractall(tmp)


def purge_files(vars_, pool):
    textbox, inst_path, tmp = [
        vars_['textbox'],
        vars_['instpath'],
        vars_['tmp']
    ]

    json_path = os.path.join(tmp, 'launcher.json')

    # Ensure the path exists
    if os.path.exists(json_path):
        with open(json_path, 'rb') as f:
            # Get delete information
            obj = json.loads(f.read().decode('UTF-8'))
            delete = obj.get('purge')

            if bool(delete):
                view.log('[INFO] Purging obsolete files:', textbox)
                futures = []
                # Ensures only files from these directories will be purged
                whitelist = ['config', 'shaderpacks']

                for file_ in delete:
                    path = os.path.join(inst_path, file_)
                    futures.append(pool.submit(delete_path, inst_path, path, whitelist, textbox))

                wait(futures)


def delete_path(base_path, path, whitelist, textbox):
    if can_delete_path(base_path, path, whitelist):
        # Determine if path is a file or not
        if os.path.isfile(path):
            os.remove(path)
        else:
            shutil.rmtree(path)

        view.log(f'[INFO] (R) {path.replace(base_path, "")[1:]}', textbox)


def retrieve_mods(vars_, pool):
    tmp, textbox = [
        vars_['tmp'],
        vars_['textbox'],
    ]

    # read modrinth.index.json
    with open(os.path.join(tmp, 'modrinth.index.json'), 'rb') as f:
        mods = json.loads(f.read().decode('UTF-8'))['files']
        futures = []

        view.log('[INFO] Retrieving any mods not present in the modpack zip:', textbox)

        for mod in mods:
            futures.append(pool.submit(retrieve, mod, vars_))

        wait(futures)


def retrieve(mod, vars_):
    _, name = os.path.split(mod['path'])
    textbox, inst_path, tmp = [
        vars_['textbox'],
        vars_['instpath'],
        vars_['tmp']
    ]

    # Split path to get mod name and join with instpath
    local_path = os.path.join(inst_path, 'mods', name)
    local_path_old = os.path.join(inst_path, 'mods-old', name)
    destination = os.path.join(tmp, 'overrides', 'mods', name)

    # Move file if it exists locally
    if os.path.isfile(local_path):
        view.log(f'[INFO] (M) {name.split('.jar')[0]}.', textbox)
        if not os.path.isfile(destination):
            shutil.move(local_path, destination)
    # Move file if it exists locally (initial install)
    elif os.path.isfile(local_path_old):
        view.log(f'[INFO] (C) {name.split('.jar')[0]}.', textbox)
        if not os.path.isfile(destination):
            shutil.copyfile(local_path_old, destination)
    # Download mod
    else:
        view.log(f'[INFO] (D) {name.split('.jar')[0]}.', textbox)
        req = requests.get(mod['downloads'][0], allow_redirects=True)
        open(destination, 'wb').write(req.content)


def install_update(vars_):
    inst_path, tmp, textbox = [
        vars_['instpath'],
        vars_['tmp'],
        vars_['textbox']
    ]

    # Paths
    mods_dest = os.path.join(inst_path, 'mods')
    config_dest = os.path.join(inst_path, 'config')
    yosbr_path = os.path.join(inst_path, 'config', 'yosbr')
    mods_tmp = os.path.join(tmp, 'overrides', 'mods')
    config_tmp = os.path.join(tmp, 'overrides', 'config')

    # Remove old mods path and move updated mods to instance
    view.log('[INFO] Moving updated mods into the provided instance location.', textbox)
    if (os.path.exists(mods_dest)):
        shutil.rmtree(mods_dest)
    shutil.move(mods_tmp, mods_dest)

    # Remove yosbr and move updated configs to instance
    view.log('[INFO] Moving updated configs into the provided instance location.', textbox)
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


def execute_launcher(textbox, exe_path):
    _, exe_name = os.path.split(exe_path)
    view.log(f'[INFO] Launching {exe_name}.', textbox)
    try:
        subprocess.check_call([exe_path])
        return True
    except Exception as error:
        view.log(f'[ERROR] {error.strerror.replace('%1', exe_path)}.', textbox)
        return False