import json
import os
import shutil
from modules import filesystem, state_manager
from modules.updaters.AbstractGameUpdater import AbstractGameUpdater


class Fallout76Updater(AbstractGameUpdater):
    def initialize(self):
        # Get game state
        game_state = state_manager.get_pack_state('Fallout76')

        # Begin initializing variables
        self.game = 'Fallout76'
        self.downloads_mods = False

        # Paths used throughout update
        self.temp_path = os.path.join(self.root, '_update_tmp', 'fallout76', self.modpack.get('name'))
        self.install_path = game_state.get('install')
        self.documents_path = game_state.get('documents')
        self.nazarick_json_path = os.path.join(self.install_path, 'nazarick.json')

        # The platform can either be 'Steam' or 'Microsoft Store'
        self.platform = game_state.get('platform')

        # Used by super.user_input_has_errors
        self.user_input_checks = [
            {
                'value': self.install_path,
                'no_value': 'Please provide the path to your Fallout 76 install.',
                'conditional': os.path.exists,
                'conditional_failed': 'The provided path to your Fallout 76 install doesn\'t exist.',
                'check_access': True,
                'access_failed': 'The install path requires administrative privileges. Please restart your launcher.'
            },
            {
                'value': self.documents_path,
                'no_value': 'Please provide the path to your Documents.',
                'conditional': os.path.exists,
                'conditional_failed': 'The provided path to your Documents doesn\'t exist.',
                'check_access': True,
                'access_failed': 'The provided path to your Documents requires adminstrative privileges. Please restart your launcher.'
            },
        ]

        # Used by super.run_executable
        self.exe_name = 'Fallout76.exe'
        if self.platform == 'Steam':
            self.command = ['cmd', '/c', 'start', 'steam://run/1151340']
        else:
            self.command = ['cmd', '/c', 'start', os.path.join(self.install_path, self.exe_name)]


    # Uninstall modpack each update; this is because there's no way to tell the version for each
    # mod. It's easier to just remove all the mods and move the new ones there.
    def pre_update(self):
        self.uninstall_modpack()


    def uninstall_modpack(self):
        if os.path.exists(self.nazarick_json_path):
            # Remove any installed mods
            with open(self.nazarick_json_path, 'r') as file:
                # Get mod index
                contents = json.loads(file.read())
                mods = contents.get('mod_index')

                if mods:
                    self.logger.info('Removing previously installed mods.')
                    for mod in mods:
                        mod_path = os.path.join(self.install_path, mod)

                        # Check if mod exists before deleting
                        if os.path.exists(mod_path):
                            filesystem.safe_delete(
                                path=mod_path,
                                base_path=self.install_path, 
                                whitelist=[],
                                logger=self.logger
                            )
                            self.logger.debug(f'(R) {mod}')

            # Remove Fallout76Custom.ini
            custom_ini_dir = os.path.join(self.documents_path, 'My Games', 'Fallout 76')
            custom_ini_path = os.path.join(custom_ini_dir, 'Fallout76Custom.ini')

            if os.path.exists(custom_ini_path):
                filesystem.safe_delete(
                    path=custom_ini_path,
                    base_path=custom_ini_dir,
                    whitelist=[],
                    logger=self.logger
                )


    def resolve_mod_index(self, mods, _):
        return mods


    def install_update(self):
        # Move modifications to install path (merging via shutil)
        modifications_path = os.path.join(self.temp_mods_path, 'Modifications')
        shutil.copytree(modifications_path, self.install_path, dirs_exist_ok=True)

        # Move Fallout76Custom.ini into Fallout 76 documents
        doc_path = os.path.join(self.temp_path, 'Fallout76Custom.ini')
        doc_dest_path = os.path.join(self.documents_path, 'My Games', 'Fallout 76', 'Fallout76Custom.ini')
        filesystem.overwrite_path(doc_path, doc_dest_path)