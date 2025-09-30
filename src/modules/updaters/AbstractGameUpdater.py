from abc import ABC, abstractmethod
from concurrent.futures import as_completed
import json
import logging
import os
import shutil
import subprocess
from modules import constants, filesystem, gui_manager, state_manager, system_check, utility, network
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
        self.initial_install = False
        self.downloads_mods = True
        self.session = None

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

        # This is set by game updaters that need their mods unzipped
        self.unzip_mods = False
        self.unzip_into_subdir = False # uses the archive name for subdir



    # ---- ABSTRACT METHODS ---- #    
    @abstractmethod
    def initialize(self):
        raise NotImplementedError

    @abstractmethod
    def install_update(self):
        raise NotImplementedError
    
    # ---- HOOKS ---- #
    def pre_update(self):
        pass

    def post_update(self):
        pass


    # ---- COMMON METHODS ---- #
    def start(self, update_button):
        # Run the game-specific initialize method (see __init__ for unitialized variables)
        self.initialize()

        # These variables each rely on data from outside the updaters or need to be set
        # each time an updater runs (in the respective updater).
        self.options = state_manager.get_state()
        self.update_button = update_button
        self.temp_nazarick_json_path = os.path.join(self.temp_path, 'nazarick.json')
        self.logger = logging.getLogger(
            f"{constants.LOGGER_NAME}.{self.game.lower()}.{self.modpack.get('name').lower()}"
        )

        # Begin logging and lock gui
        self.logger.info('')
        self.logger.info(f'Beginning update process at {utility.get_time()}.')
        self.logger.info(f'Locking user input.')
        gui_manager.lock(True)

        # Defaults in case of failures in the try branch
        task_percent = 0.0
        ModpackProvider = None
        mod_index = []

        # Create network session
        self.session = network.make_session(pool_maxsize=constants.MAX_WORKER_AMOUNT + 2)

        try:
            # Unlock this update process' button so user can cancel
            update_button.configure(state='normal')

            # Initialize providers
            providers = self.modpack.get('providers')
            ModpackProvider = providers.get('modpack')()
            self.modprovider = providers.get('mods')()

            # Get progress bar and divide 25% of progress bar by amount of tasks
            progressbar = self.widgets.get('progressbar')
            task_percent = 0.2 / 12 # (tasks are 20%, modpack download is 30%, and mods are 50%)

            # Print each error present for user input and end the update process.
            errors = self.user_input_has_errors()

            if errors:
                self.widgets.get('tabs').set('Logs')
                for error in errors:
                    self.logger.error(f'{error}')
                self.cancel = True
                return

            # Check for internet
            internet_connection = system_check.check_internet()
            
            if internet_connection:
                self.version = ModpackProvider.get_latest_modpack_version(self.game, self.modpack)

            # This is ran after each task (aside from retrieve_mods)
            progressbar.add_percent(task_percent)

            if internet_connection and self.version:
                # Skips update process if they're already on the latest version
                if self.on_latest_version():
                    progressbar.add_percent(1 - (task_percent * 2))
                    return

                # Run pre update hook
                if not self.cancel:
                    self.pre_update()
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
                    self.post_update()
                    progressbar.add_percent(task_percent)

            # Warn the user if self.version couldn't be retrieved
            elif not self.version:
                self.widgets.get('tabs').set('Logs')
                self.logger.error('Invalid response from the modpack\'s provider; skipping update process.')
                self.logger.debug(f"ModpackProvider: {ModpackProvider.__class__.__name__ if ModpackProvider else 'uninitialized'}")
                self.cancel = True

            # If self.version exists, the failure was internet_connection; warn the user.
            else:
                self.widgets.get('tabs').set('Logs')
                self.logger.warning('No internet connection; skipping update process.')
                self.cancel = True
        except Exception:
            self.widgets.get('tabs').set('Logs')
            self.logger.exception("Stack Trace:")
            self.logger.error(f'Updater crashed; terminating update process. Check log file.')
            self.logger.debug(f"ModpackProvider: {ModpackProvider.__class__.__name__ if ModpackProvider else 'uninitialized'}")
            self.logger.debug(f"ModProvider: {self.modprovider.__class__.__name__ if getattr(self, 'modprovider', None) else 'uninitialized'}")
            self.logger.debug(f"CWD: {os.getcwd()}")
            self.logger.debug(f"STATE: {self.options}")
            self.cancel = True
        finally:
            # Finish up the update process.
            self.finalize(task_percent)


    def finalize(self, task_percent):
        # Close the networking session
        try:
            session = getattr(self, "session", None)
            if session:
                session.close()
        except Exception:
            pass

        # Finish update and either close app or unlock GUI
        progressbar = self.widgets.get('progressbar')

        self.logger.info(f'Finished process at {utility.get_time()}.')

        if not self.cancel:
            self.run_executable()
            progressbar.add_percent(task_percent)

        if not self.cancel:
            self.auto_close_app()

        self.logger.info(f'Unlocking user input.')
        gui_manager.lock(False)

        # Reset values
        progressbar.reset_percent()
        self.update_button.configure(text='Play')
        self.cancel = False


    def user_input_has_errors(self):
        self.logger.info('Validating game settings.')

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

                    for future in as_completed(futures):
                        try:
                            future.result()
                        except Exception as e:
                            print(e)
                            pass

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

        if not self.downloads_mods:
            progress_bar = self.widgets.get('progressbar')
            progress_bar.add_percent(0.5)
            return []

        mods = self.modprovider.get_modpack_modlist(self)
        task_percent = 0.5 / len(mods)
        futures = []
        future_to_mod = {}

        # Ensure destination exists
        os.makedirs(destination, exist_ok=True)

        for mod in mods:
            future = self.pool.submit(self.retrieve, mod, local_paths, destination, task_percent)
            futures.append(future)
            future_to_mod[future] = mod

        # Handle any mods that couldn't be downloaded, logging any failed retrievals
        notdownloaded = []
        for f in as_completed(futures):
            try:
                f.result()
            except Exception as e:
                mod = future_to_mod.get(f)
                self.logger.exception(f"Failed to retrieve mod: {mod}")
                notdownloaded.append({'mod': mod, 'error': e})

        #  Abort update early if 20% of the mods fail to download
        if not self.cancel: # Do not alert if the download was canceled by user
            if len(notdownloaded) / max(len(mods), 1) > 0.20:
                self.logger.error("Too many mods failed to download. Aborting update process.")
                self.cancel = True  
            elif notdownloaded:
                self.logger.warning('The launcher was unable to download the following mods:')
                for result in notdownloaded:
                    self.logger.warning(f"- {result['mod']}")
                self.logger.warning('You will need to download the files manually.')

        os.chdir(self.temp_path)

        return self.resolve_mod_index(mods, destination)
    

    def resolve_mod_index(self, mods, destination):
        """
            This method allows for each updater to override what the mod_index contains
            per updater. For example, some games may want a list of mods found in the
            mod folder while others may want the stored mod list in the modpack itself.
        """
        return os.listdir(destination)


    def retrieve(self, mod_data, local_paths, destination, task_percent):
        if not self.cancel:
            self.modprovider.download_mod(self, mod_data, local_paths, destination)
            progress_bar = self.widgets.get('progressbar')
            progress_bar.add_percent(task_percent)


    def check_local_mod_paths(self, local_paths, destination, filename):
        found = False

        for local_path in local_paths:
            # Check for presence of exact file
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

            # Check for folder with same stem (e.g. a mod that was extracted from a zip)
            stem = os.path.splitext(filename)[0]
            local_dir_path = os.path.join(local_path, stem)

            if os.path.isdir(local_dir_path):
                dest_dir = os.path.join(destination, stem)
                if not os.path.exists(dest_dir):
                    self.logger.info(f'(M) {filename}')
                    shutil.copytree(local_dir_path, dest_dir)
                else:
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