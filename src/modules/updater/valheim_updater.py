import os, requests, json, shutil, zipfile
from modules.updater.common import *
from concurrent.futures import wait
from modules import view, utility, store

def start(ctk, app, pool, widgets):
    # Definet he logging function
    log = widgets.get('logbox').get('log')

    # Start logs
    log(f'')
    log(f'[INFO] Beginning process at {utility.get_time()}.')

    # Lock user input
    log(f'[INFO] Locking user input.')
    view.lock(True)

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
        'log': log,
        'version': get_latest_version() if internet_connection else None
    }

    # This represents the percentage each task (other than retrieve_mods) will increment
    # the progress bar.
    task_percent = 0.25 / 9
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
        if on_latest_version(variables, initial_install):
            progressbar.add_percent(1 - (task_percent * 2))
            finalize(variables, task_percent)
            return
        progressbar.add_percent(task_percent)

        clean_update_directories(variables)
        progressbar.add_percent(task_percent)

        download_modpack(variables)
        progressbar.add_percent(task_percent)

        extract_modpack(variables)
        progressbar.add_percent(task_percent)

        purge_files(variables, pool, whitelist=['BepInEx/config'])
        progressbar.add_percent(task_percent)

        retrieve_mods(variables, pool)

        install_update(variables, pool)
        progressbar.add_percent(task_percent)

        store_version_number(variables)
        progressbar.add_percent(task_percent)
    elif not variables.get('version'):
        log('[INFO] Invalid response from Thunderstore; skipping update process.')
    else:
        log('[INFO] No internet connection; skipping update process.')

    finalize(variables, task_percent)


# This is split so that it can be ran at multiple points in the main function
def finalize(vars_, task_percent):
    options, log, widgets = [
        vars_['options'],
        vars_['log'],
        vars_['widgets']
    ]

    progressbar = widgets.get('progressbar')

    log(f'[INFO] Unlocking user input.')
    view.lock(False)
    
    # TODO - Support launching with mac as well
    run_executable(exe_name='valheim.exe', debug=options['debug'], log=log, command=['cmd', '/c', 'start', 'steam://run/892970'])
    progressbar.add_percent(task_percent)

    log(f'[INFO] Finished process at {utility.get_time()}.')
    progressbar.reset_percent()
    autoclose_app(vars_)


# ----- Helper Functions ----- #
def handle_errors(vars_):
    log, inst_path = [
        vars_['log'],
        vars_['instpath'],
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

# Get latest version from thunderstore.io API
def get_latest_version():
    req = requests.get('https://thunderstore.io/api/experimental/package/Syh/Nazarick_Core/')

    if (req.status_code != 200):
        return False

    data = json.loads(req.text)
    return {
        'name': data['full_name'],
        'version': data['latest']['version_number'],
        'url': data['latest']['download_url']
    }


def initial_install(vars_):
    return


def download_modpack(vars_):
    log, tmp, version = [
        vars_['log'],
        vars_['tmp'],
        vars_['version']
    ]

    log(f'[INFO] Downloading latest version: {version['name']} ({version['version']}).')

    # Download the mrpack as .zip
    req = requests.get(version['url'], allow_redirects=True)
    open(os.path.join(tmp, 'update.zip'), 'wb').write(req.content)


def extract_modpack(vars_):
    log, tmp = [
        vars_['log'],
        vars_['tmp'],
    ]

    zip_file = os.path.join(tmp, 'update.zip')

    log('[INFO] Extracting the modpack zip.')
    with zipfile.ZipFile(zip_file, 'r') as ref:
        ref.extractall(tmp)
        
    # Remove update.zip
    os.remove(zip_file)

    # Move the changelog to its destination
    extract_modpack_changelog(vars_, 'Valheim')



def retrieve_mods(vars_, pool):
    tmp, log = [
        vars_['tmp'],
        vars_['log']
    ]

    # Make a plugins folder
    plugins_tmp = os.path.join(tmp, 'plugins')
    os.makedirs(plugins_tmp, exist_ok=True)

    # Read manifest.json
    with open(os.path.join(tmp, 'manifest.json'), 'rb') as f:
        plugins = json.loads(f.read().decode('UTF-8'))['dependencies']
        plugin_progress_percent = 0.75 / len(plugins)
        futures = []

        log('[INFO] Retrieving modpack dependencies:')

        for plugin in plugins:
            futures.append(pool.submit(retrieve, plugin, vars_, plugins_tmp, plugin_progress_percent))

        wait(futures)


def retrieve(plugin, vars_, plugins_tmp, plugin_percent):
    log, inst_path, widgets = [
        vars_['log'],
        vars_['instpath'],
        vars_['widgets']
    ]
    progressbar = widgets.get('progressbar')

    plugin_url = f"https://thunderstore.io/package/download/{plugin.replace('-', '/')}"
    plugin_zip = os.path.join(plugins_tmp, f'{plugin}.zip')
    tmp_plugin_dir = os.path.join(plugins_tmp, plugin)
    loc_plugin_dir = os.path.join(inst_path, 'BepInEx', 'plugins', plugin)

    # Move plugin if it already exists locally
    if os.path.isdir(loc_plugin_dir):
        log(f'[INFO] (M) {plugin}')
        if not os.path.exists(tmp_plugin_dir):
            shutil.move(loc_plugin_dir, tmp_plugin_dir)
    # Download zip then extract and delete it
    else:
        log(f'[INFO] (D) {plugin}')

        req = requests.get(plugin_url, allow_redirects=True)
        open(plugin_zip, 'wb').write(req.content)

        with zipfile.ZipFile(plugin_zip, 'r') as ref:
            ref.extractall(tmp_plugin_dir)

        os.remove(plugin_zip)

    progressbar.add_percent(plugin_percent)


def install_update(vars_, pool):
    inst_path, tmp, log = [
        vars_['instpath'],
        vars_['tmp'],
        vars_['log']
    ]

    # Set up BepInEx
    setup_bepinex(vars_, pool)

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


def setup_bepinex(vars_, pool):
    tmp, log = [
        vars_['tmp'],
        vars_['log']
    ]

    # Paths
    plugins_tmp = os.path.join(tmp, 'plugins')
    config_tmp = os.path.join(tmp, 'config')
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
    

    # Move plugins and configs to new BepInEx structure
    futures = []

    for plugin in os.listdir(plugins_tmp):
        futures.append(pool.submit(
            shutil.move,
            os.path.join(plugins_tmp, plugin),
            os.path.join(install_tmp, 'BepInEx', 'plugins', plugin)
        ))

    for config in os.listdir(config_tmp):
        futures.append(pool.submit(
            shutil.move,
            os.path.join(config_tmp, config),
            os.path.join(install_tmp, 'BepInEx', 'config', config)
        ))

    wait(futures)