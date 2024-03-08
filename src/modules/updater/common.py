import os, shutil, json, subprocess
from concurrent.futures import wait
from threading import Event
from modules import utility
from modules.components.common import ChangesBox
from modules import constants


# ANCHOR - Version Related Methods
def store_version_data(variables, mod_index):
    version, log, inst_path = [
        variables['version'],
        variables['log'],
        variables['instpath']
    ]

    data = json.dumps({
        'name': version['name'],
        'version': version['version'],
        'mod_index': mod_index
    })

    log(f'[INFO] Storing new version ID for future ref: {version['name']} ({version['version']}).')
    open(os.path.join(inst_path, 'nazarick.json'), 'w').write(data)


def get_version_data(variables):
    inst_path = variables['instpath']

    nazarick_path = os.path.join(inst_path, 'nazarick.json')

    if os.path.exists(nazarick_path):
        with open(nazarick_path, 'rb') as f:
            data = json.loads(f.read().decode('UTF-8'))
        return data
    
    return {}


def on_latest_version(variables, initial_install_fn = None):
    version, inst_path, log = [
        variables['version'],
        variables['instpath'],
        variables['log']
    ]

    # Convert from 'nuver' file to 'nazarick.json'
    convert_to_new_version_format(variables)

    # Check if the user is on the latest version
    nazarick_path = os.path.join(inst_path, 'nazarick.json')

    if os.path.exists(nazarick_path):
        with open(nazarick_path, 'rb') as f:
            data = json.loads(f.read().decode('UTF-8'))
            name, ver = [data['name'], data['version']]

            # Ensure modpack version and name are the same
            if name == version['name'] and ver == version['version']:
                log(f'[INFO] You are already on the latest version: {name} ({ver}).')
                return True
    else:
        if initial_install_fn:
            # Run the function that handles existing files on initial install
            log('[INFO] Preparing instance for initial install.')
            initial_install_fn(variables)

    return False


def convert_to_new_version_format(variables):
    inst_path, log = [
        variables['instpath'],
        variables['log']
    ]

    nuver_path = os.path.join(inst_path, 'nuver')

    if os.path.exists(nuver_path):
        with open(nuver_path, 'rb') as f:
            stored_version = f.read().decode('UTF-8').split(" ")
            store_version_data({
                'version': {
                    'name': ' '.join(stored_version[:-1]),
                    'version': stored_version[-1]
                },
                'instpath': inst_path,
                'log': log
            })

        # Delete nuver
        os.remove(nuver_path)


# ANCHOR - File Manipulation
def purge_files(variables, pool, whitelist):
    log, inst_path, tmp = [
        variables['log'],
        variables['instpath'],
        variables['tmp']
    ]

    json_path = os.path.join(tmp, 'launcher.json')

    # Ensure the path exists
    if os.path.exists(json_path):
        with open(json_path, 'rb') as f:
            # Get delete information
            obj = json.loads(f.read().decode('UTF-8'))
            delete = obj.get('purge')

            if bool(delete):
                log('[INFO] Purging requested files.')
                futures = []

                for file_ in delete:
                    path = os.path.join(inst_path, file_)
                    futures.append(pool.submit(delete_path, inst_path, path, whitelist, log))

                wait(futures)


def extract_modpack_changelog(variables, game, pack):
    tmp, ctk, widgets = [
        variables.get('tmp'),
        variables.get('ctk'),
        variables.get('widgets')
    ]

    # Move the changelog to its destination
    changelog_tmp = os.path.join(tmp, 'CHANGELOG.md')
    changelog_dest = os.path.join(constants.APP_BASE_DIR, 'assets', game, pack, 'CHANGELOG.md')

    if os.path.exists(changelog_tmp):
        os.makedirs(os.path.split(changelog_dest)[0], exist_ok=True)
        shutil.move(changelog_tmp, changelog_dest)

        ChangesBox.load_changelog(ctk, widgets.get('changebox'), game, widgets.get('html_frame'))


def delete_path(base_path, path, whitelist, log):
    if can_delete_path(base_path, path, whitelist):
        rm_func = shutil.rmtree if os.path.isdir(path) else os.remove
        rm_func(path)
        log(f'[INFO] (R) {path.replace(base_path, "")[1:]}')


def can_delete_path(base_path, path, whitelist = []):
    """
        Ensures that the given path is within a whitelisted directory inside the instance path and that the path exists.\n\n
    """
    # Variables
    path_abs = os.path.abspath(path)
    result = False
            
    # Determine if the path is within the base path
    if not utility.path_is_relative(base_path, path_abs):
        return False

    # Ensure the path exists
    if not os.path.exists(path_abs):
        return False

    # Ensure the file to delete is within a whitelisted directory
    # while ensuring the target isn't the directory itself.
    for dir_ in whitelist:
        base_whitelist_path = os.path.join(base_path, dir_)
        if utility.path_is_relative(base_whitelist_path, path_abs) and base_whitelist_path != path_abs:
            result = True

    # 
    if len(whitelist) == 0:
        result = True

    return result


def overwrite(source, target):
    target_root, _ = os.path.split(target)
    rm_func = shutil.rmtree if os.path.isdir(target) else os.remove

    if os.path.exists(target):
        rm_func(target)

    if not os.path.exists(target_root):
        os.makedirs(target_root)

    shutil.move(source, target)


def clean_update_directories(variables):
    tmp, log = [
        variables['tmp'],
        variables['log']
    ]
            
    # Remove any files not in whitelist do_not_clean
    if os.path.exists(tmp):
        log('[INFO] Cleaning the tmp directory.')
        do_not_clean = ['custommods']

        # Cleanup tmp dir
        files = os.listdir(tmp)
        for f in files:
            if f not in do_not_clean:
                file_path = os.path.join(tmp, f)
                rm_func = shutil.rmtree if os.path.isdir(file_path) else os.remove
                rm_func(file_path)
    else:
        log('[INFO] Creating the tmp directory.')

    # Create clean tmp directory
    os.makedirs(tmp, exist_ok=True)
    

def retrieve_mods(variables, destination, local_paths, pool):
    tmp, log, ModProvider = [
        variables.get('tmp'),
        variables.get('log'),
        variables.get('modprovider')
    ]

    # Get the modlist
    mods = ModProvider.get_modpack_modlist(variables)

    # Update variables
    plugin_progress_percent = 0.75 / len(mods)
    futures = []

    # Make sure the destination exists
    os.makedirs(destination, exist_ok=True)

    # Create stop processing event
    stop_processing = Event()

    log('[INFO] Retrieving modpack dependencies.')

    for mod in mods:
        futures.append(
            pool.submit(retrieve, # Function being called
                        # Variables being passed to function
                        mod, variables, local_paths, destination, plugin_progress_percent, stop_processing
            )
        )

    result = wait(futures)

    # Handle any mods that could not be downloaded
    notdownloaded = []

    for task in list(result.done):
        if task.exception():
            notdownloaded.append(task.exception())

    if len(notdownloaded):
        log('[WARN] The launcher was unable to download the following mods:', 'warning')
        for mod in notdownloaded:
            log(f'[WARN] - {mod}', 'warning')
        log('[WARN] You will need to download them manually.', 'warning')


    os.chdir(tmp)
        
    return os.listdir(destination)


def retrieve(mod_data, variables, local_paths, destination, progress_percent, stop_processing):
    log, ModProvider, widgets = [
        variables['log'],
        variables['modprovider'],
        variables['widgets']
    ]

    if stop_processing.is_set():
        return

    # Download the mod
    ModProvider.download_mod(log, mod_data, local_paths, destination)
    
    # Increment progress bar
    progress_bar = widgets.get('progressbar')
    progress_bar.add_percent(progress_percent)


def check_local_mod_paths(log, local_paths, destination, filename):
    found = False

    for local_path in local_paths:
        local_file_path = os.path.join(local_path, filename)

        if os.path.exists(local_file_path):
            # Move local files
            if not os.path.exists(destination):
                log(f'[INFO] (M) {filename}')
                shutil.move(local_file_path, destination)
                found = True
                break
            
            # Mods found in overrides should be marked as found; otherwise, if the download
            # fails, it'll prompt the user to download the mod manually.. when they already
            # have it installed.
            if local_file_path == destination:
                log(f'[INFO] (E) {filename}')

                found = True
                break
    
    # Change to tmp to free all local paths
    os.chdir(constants.APP_BASE_DIR)

    return found


# ANCHOR -  Finalize Methods
def run_executable(exe_name, debug, log, command):
    # Debug mode stops exe from launching
    if not debug:
        log(f'[INFO] Launching {exe_name}.')
        try:
            subprocess.check_call(command)
        except Exception as error:
            log(f'[ERROR] {error.strerror.replace('%1', ' '.join(command))}.')
    else:
        log('[INFO] The executable is not launched whilst in debug mode.')


def autoclose_app(variables):
    options, log, app = [
        variables['options'],
        variables['log'],
        variables['app']
    ]

    if options['autoclose']:
        log('[INFO] Auto close is enabled; closing app.')
        app.quit()

