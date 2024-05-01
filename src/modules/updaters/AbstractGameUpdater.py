from abc import ABC, abstractmethod
from concurrent.futures import wait
import json
import logging
import os
import shutil
import subprocess
import traceback
from modules import constants, filesystem, gui_manager, state_manager, system_check, utility
from modules.components.common import ChangesBox


logger = logging.getLogger(constants.LOGGER_NAME)

class AbstractGameUpdater(ABC):
    def __init__(self, ctk, app, pool, widgets, modpack):
        # Initialize basic variables
        self.app = app
        self.ctk = ctk
        self.pool = pool
        self.modpack = modpack
        self.widgets = widgets
        self.root = os.environ.get('nazpath')
        self.cancel = False
        self.initial_install = True

        # These get set each time the updater runs (in self.start)
        self.options = {}
        self.update_button = None
        self.temp_nazarick_json_path = ''
        self.logger = None

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

        # These variables each rely on data from outside the updaters or need to be set
        # each time the updaters run.
        self.options = state_manager.get_state()
        self.update_button = update_button
        self.temp_nazarick_json_path = os.path.join(self.temp_path, 'nazarick.json')
        self.logger = logging.getLogger(
            f'{constants.LOGGER_NAME}.{self.game.lower()}.{self.modpack.get('name').lower()}'
        )

        # Begin logging and lock gui
        self.logger.info('')
        self.logger.info(f'Beginning update process at {utility.get_time()}.')

        self.logger.info(f'Locking user input.')
        gui_manager.lock(True)

        # Unlock this update process' button
        update_button.configure(state='normal')

        # Initialize providers
        providers = self.modpack.get('providers')
        try:
            ModpackProvider = providers.get('modpack')()
            self.modprovider = providers.get('mods')()
        except Exception as e:
            # Print exception
            self.logger.error('Unable to initialize provider:')
            self.logger.error(f'{e}')
            self.logger.info('Terminating update process.')
            traceback.print_exc()

            # Set cancel to true so nothing runs in finalize except unlocking and sending logs
            self.cancel = True
            self.finalize()
            return

        # Get progress bar and divide 25% of progress bar by amount of tasks
        progressbar = self.widgets.get('progressbar')
        task_percent = 0.25 / 13 # tasks are 25% of the progress, mod download is 75%

        # Print each error present for user input and end the update process.
        errors = self.user_input_has_errors()

        if errors:
            self.widgets.get('tabs').set('Logs')
            for error in errors:
                self.logger.error(f'{error}')

            self.logger.info(f'Unlocking user input.')
            gui_manager.lock(False)

            self.logger.info(f'Finished process at {utility.get_time()}.')
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
                if self.on_latest_version():
                    progressbar.add_percent(1 - (task_percent * 2))
                    self.finalize(task_percent)
                    return

                # Run pre update hook
                if not self.cancel:
                    ModpackProvider.pre_update(self)
                    progressbar.add_percent(task_percent)

                # Clean up temp directory
                if not self.cancel:
                    self.clean_update_directory(initial_clean=True)
                    progressbar.add_percent(task_percent)

                # Store version data in temporary update directory (needed to resume updates)
                if not self.cancel:
                    self.store_version_data([], self.temp_nazarick_json_path)
                    progressbar.add_percent(task_percent)

                # Download latest modpack version
                if not self.cancel:
                    # This is necessary to prevent downloading the modpack a second time if the
                    # previous update was cancelled. If there's more than just nazarick.json in
                    # the temp_path, the modpack has already been downloaded.
                    if not len(os.listdir(self.temp_path)) > 1:
                        ModpackProvider.download_modpack(self)
                    progressbar.add_percent(task_percent)

                # Unzip update to temp directory
                if not self.cancel:
                    ModpackProvider.extract_modpack(self, self.game, self.modpack.get('name'))
                    progressbar.add_percent(task_percent)

                # handle initial install
                if not self.cancel and self.initial_install:
                    self.logger.info('Preparing for initial modpack install.')
                    ModpackProvider.initial_install(self)

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

                # Clean up after the update
                if not self.cancel:
                    self.clean_update_directory()
                    progressbar.add_percent(task_percent)

                # Run post update hook
                if not self.cancel:
                    ModpackProvider.post_update(self)
                    progressbar.add_percent(task_percent)

            # Handle update process failing
            except Exception as e:
                self.widgets.get('tabs').set('Logs')
                self.logger.error(f'{e}; terminating update process.')
                logger.debug(f"ModpackProvider: {ModpackProvider.__class__.__name__}")
                logger.debug(f"ModProvider: {self.modprovider.__class__.__name__}")
                logger.debug(f"CWD: {os.getcwd()}")
                logger.debug(f"STATE: {self.options}")
                traceback.print_exc()
                self.cancel = True

        # Warn the user if self.version couldn't be retrieved
        elif not self.version:
            self.widgets.get('tabs').set('Logs')
            self.logger.error('Invalid response from the modpack\'s provider; skipping update process.')
            logger.debug(f"ModpackProvider: {ModpackProvider.__class__.__name__}")

        # If self.version exists, the failure was internet_connection; warn the user.
        else:
            self.widgets.get('tabs').set('Logs')
            self.logger.warning('No internet connection; skipping update process.')

        # Finish up the update process.
        self.finalize(task_percent)


    def finalize(self, task_percent):
        progressbar = self.widgets.get('progressbar')

        self.logger.info(f'Unlocking user input.')
        gui_manager.lock(False)

        if not self.cancel:
            self.run_executable()
            progressbar.add_percent(task_percent)

        if not self.cancel:
            self.auto_close_app()

        # Reset values
        self.logger.info(f'Finished process at {utility.get_time()}.')
        progressbar.reset_percent()
        self.update_button.configure(text='Play')
        self.cancel = False


    def user_input_has_errors(self):
        self.logger.info('Validating the provided executable and instance paths.')

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
    def store_version_data(self, mod_index, path = ''):
        version_name = self.version.get('name')
        version = self.version.get('version')

        data = json.dumps({
            'name': version_name,
            'version': version,
            'mod_index': mod_index
        })

        if not path:
            self.logger.info(f'Storing version information: {version_name} ({version}).')
        with open(path or self.nazarick_json_path, 'w') as f:
            f.write(data)


    def get_version_data(self):
        if os.path.exists(self.nazarick_json_path):
            with open(self.nazarick_json_path, 'r') as f:
                data = json.loads(f.read())
            return data

        return {}


    def on_latest_version(self):
        # Switch from old nuver to nazarick.json format
        self.convert_to_new_version_format()

        if os.path.exists(self.nazarick_json_path):
            with open(self.nazarick_json_path, 'r') as f:
                data = json.loads(f.read())
                name, ver = [data['name'], data['version']]

                # If modpack version and name are the same, you're on the latest version
                if name == self.version.get('name') and ver == self.version.get('version'):
                    self.logger.info(f'You are already on the latest version: {name} ({ver}) for {self.game}.')
                    return True
        else:
            self.initial_install = True

        return False


    def convert_to_new_version_format(self):
        nuver_path = os.path.join(self.install_path, 'nuver')

        if os.path.exists(nuver_path):
            with open(nuver_path, 'r') as f:
                stored_version = f.read().split(" ")
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
            with open(launcher_json_path, 'r') as f:
                data = json.loads(f.read())
                purge = data.get('purge')

                if purge:
                    self.logger.info('Purging requested files.')
                    futures = []

                    for f in purge:
                        path = os.path.join(self.install_path, f)
                        futures.append(
                            self.pool.submit(filesystem.safe_delete, path, self.install_path, self.purge_whitelist, self.logger)
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


    def clean_update_directory(self, initial_clean=False):
        # Release the temp path to allow its deletion
        if os.getcwd() == self.temp_path:
            os.chdir(constants.APP_BASE_DIR)

        # This is ran at the beginning of the update process.
        if initial_clean:
            if os.path.exists(self.temp_nazarick_json_path):
                if self.check_for_unfinished_update():
                    self.logger.info('An update has already been started for that version; continuing...')
                    return

            # The path should be empty if there's no previously started update; recreate it.
            if os.path.exists(self.temp_path):
                if len(os.listdir(self.temp_path)):
                    self.logger.info('Recreating temporary update directory.')
                    shutil.rmtree(self.temp_path)
                    os.makedirs(self.temp_path)
            else:
                self.logger.info('Creating temporary update directory')
                os.makedirs(self.temp_path)

        # This is ran at the end of the update process.
        else:
            self.logger.info('Removing temporary update directory.')
            shutil.rmtree(self.temp_path)


    def retrieve_mods(self, destination, local_paths):
        self.logger.info('Retrieving modpack dependencies.')

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
            self.logger.warning('The launcher was unable to download the following mods:')
            for mod in notdownloaded:
                self.logger.warning(f'- {mod}')
            self.logger.warning('You will need to download the files manually.')

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
                    self.logger.info(f'(M) {filename}')
                    shutil.copy(local_file_path, destination)
                    found = True
                    break

                # Mods found in overrides should be marked as found; otherwise, if the download
                # fails, it'll prompt the user to download the mod manually.. when they already
                # have it installed.
                if local_file_path == destination:
                    self.logger.info(f'(E) {filename}')

                    found = True
                    break

        # Change working directory to free all local paths
        os.chdir(constants.APP_BASE_DIR)

        return found


    def check_for_unfinished_update(self):
        if os.path.exists(self.temp_nazarick_json_path):
            # Check if name and version are matching; if they are, consider it an unfinished update.
            with open(self.temp_nazarick_json_path, 'r') as f:
                content = json.loads(f.read())
                matching_name = content.get('name') == self.version.get('name')
                matching_version = content.get('version') == self.version.get('version')
                return matching_name and matching_version
        return False


    def run_executable(self):
        # Debug mode stops exe from launching
        if not self.options.get('debug'):
            self.logger.info(f'Launching {self.exe_name}.')
            try:
                subprocess.check_call(self.command)
            except Exception as error:
                self.logger.info(f'{error.strerror.replace('%1', ' '.join(self.command))}.')
        else:
            self.logger.info(f'The game is not launched whilst in debug mode.')


    def auto_close_app(self):
        if self.options.get('autoclose'):
            self.logger.info('Auto close is enabled; closing app.')
            self.app.quit()


    def cancel_update(self):
        self.cancel = True