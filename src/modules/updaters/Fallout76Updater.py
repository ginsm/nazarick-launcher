import os
from modules import state_manager
from modules.updaters.AbstractGameUpdater import AbstractGameUpdater


class Fallout76Updater(AbstractGameUpdater):
    def initialize(self):
        # Get game state
        game_state = state_manager.get_pack_state('Fallout76')

        # Begin initializing variables
        self.game = 'Fallout76'

        # Paths used throughout update
        self.temp_path = os.path.join(self.root, '_update_tmp', 'fallout76', self.modpack.get('name'))
        self.install_path = game_state.get('install')
        self.documents_path = game_state.get('documents_path')
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


    def install_update(self):
        pass