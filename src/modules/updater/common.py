import os, shutil, json, subprocess
from concurrent.futures import wait
from modules import utility
from modules.components.common import ChangesBox
from modules.tufup import BASE_DIR


# ---- LOCAL VERSION CHECKING ---- #
def store_version_number(vars_):
    version, log, inst_path = [
        vars_['version'],
        vars_['log'],
        vars_['instpath']
    ]

    data = json.dumps({
        'name': version['name'],
        'version': version['version']
    })

    log(f'[INFO] Storing new version ID for future ref: {version['name']} (v{version['version']}).')
    open(os.path.join(inst_path, 'nazarick.json'), 'w').write(data)


def on_latest_version(vars_, initial_install_fn):
    version, inst_path, log = [
        vars_['version'],
        vars_['instpath'],
        vars_['log']
    ]

    # Convert from 'nuver' file to 'nazarick.json'
    convert_to_new_version_format(vars_)

    # Check if the user is on the latest version
    nazarick_path = os.path.join(inst_path, 'nazarick.json')

    if os.path.exists(nazarick_path):
        with open(nazarick_path, 'rb') as f:
            data = json.loads(f.read().decode('UTF-8'))
            name, ver = [data['name'], data['version']]

            # Ensure modpack version and name are the same
            if name == version['name'] and ver == version['version']:
                log(f'[INFO] You are already on the latest version: {name} (v{ver}).')
                return True
    else:
        # Run the function that handles existing files on initial install
        log('[INFO] Preparing instance for initial install.')
        initial_install_fn(vars_)

    return False


def convert_to_new_version_format(vars_):
    inst_path, log = [
        vars_['instpath'],
        vars_['log']
    ]

    nuver_path = os.path.join(inst_path, 'nuver')

    if os.path.exists(nuver_path):
        with open(nuver_path, 'rb') as f:
            stored_version = f.read().decode('UTF-8').split(" ")
            store_version_number({
                'version': {
                    'name': ' '.join(stored_version[:-1]),
                    'version': stored_version[-1]
                },
                'instpath': inst_path,
                'log': log
            })

        # Delete nuver
        os.remove(nuver_path)


# ---- FILE MANIPULATION ---- #
def purge_files(vars_, pool, whitelist):
    log, inst_path, tmp = [
        vars_['log'],
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
                log('[INFO] Purging obsolete files:')
                futures = []

                for file_ in delete:
                    path = os.path.join(inst_path, file_)
                    futures.append(pool.submit(delete_path, inst_path, path, whitelist, log))

                wait(futures)


def extract_modpack_changelog(vars_, game):
    tmp, ctk, widgets = [
        vars_.get('tmp'),
        vars_.get('ctk'),
        vars_.get('widgets')
    ]

    # Move the changelog to its destination
    changelog_tmp = os.path.join(tmp, 'CHANGELOG.md')
    changelog_dest = os.path.join(BASE_DIR, 'assets', game, 'CHANGELOG.md')

    if os.path.exists(changelog_tmp):
        os.makedirs(os.path.split(changelog_dest)[0], exist_ok=True)
        shutil.move(changelog_tmp, changelog_dest)

        ChangesBox.load_changelog(ctk, widgets.get('changebox'), 'Valheim', widgets.get('html_frame'))


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


def clean_update_directories(vars_):
    tmp, log = [
        vars_['tmp'],
        vars_['log']
    ]
            
    # Delete any existing tmp directory
    if os.path.exists(tmp):
        log('[INFO] Cleaning the tmp directory.')
        shutil.rmtree(tmp)
    else:
        log('[INFO] Creating the tmp directory.')

    # Create clean tmp directory
    os.makedirs(tmp, exist_ok=True)


# ---- Finalize Methods ---- #
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


def autoclose_app(vars_):
    options, log, app = [
        vars_['options'],
        vars_['log'],
        vars_['app']
    ]

    if options['autoclose']:
        log('[INFO] Auto close is enabled; closing app.')
        app.quit()