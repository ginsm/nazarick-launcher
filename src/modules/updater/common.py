import os, shutil, json, subprocess
from concurrent.futures import wait
from modules import utility


# ---- LOCAL VERSION CHECKING ---- #
def store_version_number(vars_):
    version, textbox, inst_path = [
        vars_['version'],
        vars_['textbox'],
        vars_['instpath']
    ]

    data = json.dumps({
        'name': version['name'],
        'version': version['version']
    })

    textbox['log'](f'[INFO] Storing new version ID for future ref: {version['name']} (v{version['version']}).')
    open(os.path.join(inst_path, 'nazarick.json'), 'w').write(data)


def on_latest_version(vars_, initial_install_fn):
    version, inst_path, textbox = [
        vars_['version'],
        vars_['instpath'],
        vars_['textbox']
    ]

    # Convert from 'nuver' file to 'nazarick.json'
    convert_to_new_version_format(vars_)

    # Check if the user is on the latest version
    nazarick_path = os.path.join(inst_path, 'nazarick.json')

    if os.path.exists(nazarick_path):
        with open(nazarick_path, 'rb') as f:
            data = json.loads(f.read().decode('UTF-8'))
            name, ver = [data['name'], data['version']]


            # is trying to update an instance path with another pack installed.
            if name == version['name'] and ver == version['version']:
                textbox['log'](f'[INFO] You are already on the latest version: {name} (v{ver}).')
                return True
    else:
        # Run the function that handles existing files on initial install
        log('[INFO] Preparing instance for initial install.')
        initial_install_fn(vars_)

    return False


def convert_to_new_version_format(vars_):
    inst_path, textbox = [
        vars_['instpath'],
        vars_['textbox']
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
                'textbox': textbox
            })

        # Delete nuver
        os.remove(nuver_path)


# ---- FILE MANIPULATION ---- #
def purge_files(vars_, pool, whitelist):
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
                textbox['log']('[INFO] Purging obsolete files:')
                futures = []

                for file_ in delete:
                    path = os.path.join(inst_path, file_)
                    futures.append(pool.submit(delete_path, inst_path, path, whitelist, textbox))

                wait(futures)


def delete_path(base_path, path, whitelist, textbox):
    if can_delete_path(base_path, path, whitelist):
        rm_func = shutil.rmtree if os.path.isdir(path) else os.remove
        rm_func(path)
        textbox['log'](f'[INFO] (R) {path.replace(base_path, "")[1:]}')


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
    tmp, textbox = [
        vars_['tmp'],
        vars_['textbox']
    ]
            
    # Delete any existing tmp directory
    if os.path.exists(tmp):
        textbox['log']('[INFO] Cleaning the tmp directory.')
        shutil.rmtree(tmp)
    else:
        textbox['log']('[INFO] Creating the tmp directory.')

    # Create clean tmp directory
    os.makedirs(tmp, exist_ok=True)


# ---- Finalize Methods ---- #
def run_executable(exe_name, debug, textbox, command):
    # Debug mode stops exe from launching
    if not debug:
        textbox['log'](f'[INFO] Launching {exe_name}.')
        try:
            subprocess.check_call(command)
        except Exception as error:
            textbox['log'](f'[ERROR] {error.strerror.replace('%1', ' '.join(command))}.')
    else:
        textbox['log']('[INFO] The executable is not launched whilst in debug mode.')

def autoclose_app(vars_):
    options, textbox, app = [
        vars_['options'],
        vars_['textbox'],
        vars_['app']
    ]

    if options['autoclose']:
        textbox['log']('[INFO] Auto close is enabled; closing app.')
        app.quit()