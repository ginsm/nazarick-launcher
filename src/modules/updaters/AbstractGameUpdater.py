from abc import ABC, abstractmethod
from concurrent.futures import wait
import json
import os
import shutil
import subprocess
import traceback

from modules import constants, filesystem, gui_manager, state_manager, system_check, utility
from modules.components.common import ChangesBox


class AbstractGameUpdater(ABC):
    def __init__(self, ctk, app, pool, widgets, modpack):
        # Initialize basic variables
        self.app = app
        self.ctk = ctk
        self.pool = pool
        self.modpack = modpack
        self.widgets = widgets
        self.log = widgets.get('logbox').get('log')
        self.root = os.environ.get('nazpath')
        self.options = state_manager.get_state()
        self.cancel = False

        # These get initialized later on in each game updater
        self.game = ''
        self.temp_path = ''
        self.install_path = ''
        self.nazarick_json_path = ''
        self.user_input_checks = []
        self.purge_whitelist = []
        self.temp_mods_path = ''
        self.local_paths = []
        self.exe_name = ''
        self.command = []
        self.modprovider = None
        self.version = None


    # ---- ABSTRACT METHODS ---- #    
    @abstractmethod
    def initialize(self):
        raise NotImplementedError
    
    @abstractmethod
    def install_update(self):
        raise NotImplementedError
    

    # ---- COMMON METHODS ---- #
    def start(self, update_button):
        # Run the game-specific initialize method (see __init__ for unitialized variables)
        self.initialize()
        self.update_button = update_button

        # Begin logging and lock gui
        self.log('')
        self.log(f'[INFO] Beginning update process at {utility.get_time()}.')

        self.log(f'[INFO] Locking user input.')
        gui_manager.lock(True)

        # Unlock this update process' button
        update_button.configure(state='normal')

        # Initialize providers
        providers = self.modpack.get('providers')
        try:
            ModpackProvider = providers.get('modpack')()
            self.modprovider = providers.get('mods')()
        except Exception as e:
            self.log('[ERROR] Unable to initialize provider:', 'error')
            self.log(f'[ERROR] {e}', 'error')
            self.log('[INFO] Terminating update process.')
            traceback.print_exc()
            gui_manager.lock(False)
            return

        # Get progress bar and divide 25% of progress bar by amount of tasks
        progressbar = self.widgets.get('progressbar')
        task_percent = 0.25 / 9 # tasks are 25% of the progress, mod download is 75%

        # Print each error present for user input and end the update process.
        errors = self.user_input_has_errors()

        if errors:
            self.widgets.get('tabs').set('Logs')
            for error in errors:
                self.log(f'[ERROR] {error}', 'error')

            self.log(f'[INFO] Unlocking user input.')
            gui_manager.lock(False)

            self.log(f'[INFO] Finished process at {utility.get_time()}.')
            return
        
        
        # Check for internet
        internet_connection = system_check.check_internet()

        if internet_connection:
            self.version = ModpackProvider.get_latest_modpack_version(self.game, self.modpack)
        
        # This is ran after each task (aside from retrieve_mods)
        progressbar.add_percent(task_percent)

        if internet_connection and self.version:
            try:
                # Skips update process if they're already on the latest version
                if self.on_latest_version(ModpackProvider.initial_modpack_install):
                    progressbar.add_percent(1 - (task_percent * 2))
                    self.finalize(task_percent)
                    return

                # Clean up temp directory
                if not self.cancel:
                    self.clean_update_directories()
                    progressbar.add_percent(task_percent)

                # Download latest modpack version
                if not self.cancel:
                    ModpackProvider.download_modpack(self)
                    progressbar.add_percent(task_percent)

                # Unzip update to temp directory
                if not self.cancel:
                    ModpackProvider.extract_modpack(self, self.game, self.modpack.get('name'))
                    progressbar.add_percent(task_percent)

                # Purge any files as instructed from modpack archive
                if not self.cancel:
                    self.purge_files()
                    progressbar.add_percent(task_percent)

                # Attempt to retrieve all of the mod files
                if not self.cancel:
                    mod_index = self.retrieve_mods(self.temp_mods_path, self.local_paths)

                # FIXME - This was causing the updaters to stall.
                # Get version data and move custom mods
                # version_data = get_version_data(variables)
                # if version_data.get('mod_index'):
                #     ModProvider.move_custom_mods(
                #         variables,
                #         version_data.get('mod_index')
                #     )
                # progressbar.add_percent(task_percent)

                # Run game-specific install method
                if not self.cancel:
                    self.install_update()
                    progressbar.add_percent(task_percent)

                # Store update's version number
                if not self.cancel:
                    self.store_version_data(mod_index)
                    progressbar.add_percent(task_percent)
            
            # Handle update process failing
            except Exception as e:
                self.widgets.get('tabs').set('Logs')
                self.log(f'[WARN] {e}; terminating update process.', 'warning')
                self.log('[WARN] You may have trouble connecting to the server.', 'warning')
                traceback.print_exc()

        # Warn the user if self.version couldn't be retrieved
        elif not self.version:
            self.widgets.get('tabs').set('Logs')
            self.log('[WARN] Invalid response from the modpack\'s provider; skipping update process.', 'warning')
            self.log('[WARN] You may have trouble connecting to the server.', 'warning')

        # If self.version exists, the failure was internet_connection; warn the user.
        else:
            self.widgets.get('tabs').set('Logs')
            self.log('[WARN] No internet connection; skipping update process.', 'warning')
            self.log('[WARN] You may have trouble connecting to the server with an outdated modpack.', 'warning')

        # Finish up the update process.
        self.finalize(task_percent)
        
    
    def finalize(self, task_percent):
        progressbar = self.widgets.get('progressbar')

        self.log(f'[INFO] Unlocking user input.')
        gui_manager.lock(False)

        if not self.cancel:
            self.run_executable()
            progressbar.add_percent(task_percent)

        if not self.cancel:
            self.auto_close_app()
            
        # Reset values
        self.log(f'[INFO] Finished process at {utility.get_time()}.')
        progressbar.reset_percent()
        self.update_button.configure(text='Play')
        self.cancel = False
        


    def user_input_has_errors(self):
        self.log('[INFO] Validating the provided executable and instance paths.')

        # Errors are appended to the list, returned, and logged in the start method
        errors = []

        for data in self.user_input_checks:
            value = data.get('value')

            # Ensure value isn't falsy
            if not value:
                errors.append(data.get('no_value'))
            else:
                # Run conditional to check valid value
                if not data.get('conditional')(value):
                    errors.append(data.get('conditional_failed'))
                # Check for file access permissions if required
                if data.get('check_access'):
                    if system_check.check_access(value) == system_check.NEED_ADMIN:
                        errors.append(data.get('access_failed'))

        return errors


    # These methods do not vary per updater.
    def store_version_data(self, mod_index):
        version_name = self.version.get('name')
        version = self.version.get('version')

        data = json.dumps({
            'name': version_name,
            'version': version,
            'mod_index': mod_index
        })

        self.log(f'[INFO] Storing new version ID for future ref: {version_name} ({version}).')
        with open(self.nazarick_json_path, 'w') as f:
            f.write(data)


    def get_version_data(self):
        if os.path.exists(self.nazarick_json_path):
            with open(self.nazarick_json_path, 'rb') as f:
                data = json.loads(f.read().decode('UTF-8'))
            return data
        
        return {}
    

    def on_latest_version(self, initial_install_fn = None):
        # Switch from old nuver to nazarick.json format
        self.convert_to_new_version_format()

        if os.path.exists(self.nazarick_json_path):
            with open(self.nazarick_json_path, 'rb') as f:
                data = json.loads(f.read().decode('UTF-8'))
                name, ver = [data['name'], data['version']]

                # If modpack version and name are the same, you're on the latest version
                if name == self.version.get('name') and ver == self.version.get('version'):
                    self.log(f'[INFO] You are already on the latest version: {name} ({ver}).')
                    return True
        else:
            # Run the function that handles existing files on initial install
            if initial_install_fn:
                self.log('[INFO] Preparing instance for initial install.')
                initial_install_fn(self)

        return False
            

    def convert_to_new_version_format(self):
        nuver_path = os.path.join(self.install_path, 'nuver')

        if os.path.exists(nuver_path):
            with open(nuver_path, 'rb') as f:
                stored_version = f.read().decode('UTF-8').split(" ")
                self.store_version_data({
                    'version': {
                        'name': ' '.join(stored_version[:-1]),
                        'version': stored_version[-1]
                    }
                })

            os.remove(nuver_path)

    
    def purge_files(self):
        launcher_json_path = os.path.join(self.temp_path, 'launcher.json')

        if os.path.exists(launcher_json_path):
            with open(launcher_json_path, 'rb') as f:
                data = json.loads(f.read().decode('UTF-8'))
                purge = data.get('purge')

                if purge:
                    self.log('[INFO] Purging requested files.')
                    futures = []

                    for f in purge:
                        path = os.path.join(self.install_path, f)
                        futures.append(
                            self.pool.submit(filesystem.delete_path, self.install_path, path, self.purge_whitelist)
                        )

                    wait(futures)


    def extract_modpack_changelog(self, game, pack):
        changelog_temp_path = os.path.join(self.temp_path, 'CHANGELOG.md')
        changelog_dest_path = os.path.join(constants.APP_BASE_DIR, 'assets', game, pack, 'CHANGELOG.md')

        if os.path.exists(changelog_temp_path):
            os.makedirs(os.path.split(changelog_dest_path)[0], exist_ok=True)
            shutil.move(changelog_temp_path, changelog_dest_path)

            changebox = self.widgets.get('changebox')
            html_frame = self.widgets.get('html_frame')

            ChangesBox.load_changelog(self.ctk, changebox, game, html_frame)


    def clean_update_directories(self):
        if os.path.exists(self.temp_path):
            self.log('[INFO] Cleaning the update directory.')
            do_not_clean = ['custommods']
            files = os.listdir(self.temp_path)

            for f in files:
                if f not in do_not_clean:
                    file_path = os.path.join(self.temp_path, f)
                    rm_func = shutil.rmtree if os.path.isdir(file_path) else os.remove
                    rm_func(file_path)
        else:
            self.log('[INFO] Creating the update directory.')

        # Create clean tmp directory
        os.makedirs(self.temp_path, exist_ok=True)
        
    
    def retrieve_mods(self, destination, local_paths):
        self.log('[INFO] Retrieving modpack dependencies.')

        mods = self.modprovider.get_modpack_modlist(self)
        task_percent = 0.75 / len(mods)
        futures = []

        # Ensure destination exists
        os.makedirs(destination, exist_ok=True)

        for mod in mods:
            futures.append(
                self.pool.submit(self.retrieve, mod, local_paths, destination, task_percent)
            )

        result = wait(futures)

        # Handle any mods that couldn't be downloaded
        notdownloaded = []

        for task in list(result.done):
            if task.exception():
                notdownloaded.apend(task.exception())

        if notdownloaded:
            self.log('[WARN] The launcher was unable to download the following mods:', 'warning')
            for mod in notdownloaded:
                self.log(f'[WARN] - {mod}', 'warning')
            self.log('[WARN] You will need to download the files manually.', 'warning')

        os.chdir(self.temp_path)

        return os.listdir(destination)
    

    def retrieve(self, mod_data, local_paths, destination, task_percent):
        if not self.cancel:
            self.modprovider.download_mod(self, mod_data, local_paths, destination)
            progress_bar = self.widgets.get('progressbar')
            progress_bar.add_percent(task_percent)


    def check_local_mod_paths(self, local_paths, destination, filename):
        found = False

        for local_path in local_paths:
            local_file_path = os.path.join(local_path, filename)

            if os.path.exists(local_file_path):
                # Move local files
                if not os.path.exists(destination):
                    self.log(f'[INFO] (M) {filename}')
                    shutil.move(local_file_path, destination)
                    found = True
                    break
                            
                # Mods found in overrides should be marked as found; otherwise, if the download
                # fails, it'll prompt the user to download the mod manually.. when they already
                # have it installed.
                if local_file_path == destination:
                    self.log(f'[INFO] (E) {filename}')

                    found = True
                    break

        # Change working directory to free all local paths
        os.chdir(constants.APP_BASE_DIR)

        return found
    

    def run_executable(self):
        # Debug mode stops exe from launching
        if not self.options.get('debug'):
            self.log(f'[INFO] Launching {self.exe_name}.')
            try:
                subprocess.check_call(self.command)
            except Exception as error:
                self.log(f'[ERROR] {error.strerror.replace('%1', ' '.join(self.command))}.')
        else:
            self.log(f'[INFO] The game is not launched whilst in debug mode.')


    def auto_close_app(self):
        if self.options.get('autoclose'):
            self.log('[INFO] Auto close is enabled; closing app.')
            self.app.quit()


    def cancel_update(self):
        self.cancel = True