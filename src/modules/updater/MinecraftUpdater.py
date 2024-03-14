from concurrent.futures import wait
import os
import shutil
from modules import filesystem, state_manager
from modules.updater.AbstractGameUpdater import AbstractGameUpdater


class MinecraftUpdater(AbstractGameUpdater):
    def initialize(self):
        # Get game state
        game_state = state_manager.get_pack_state('Minecraft')

        # Initialize variables
        self.game = 'Minecraft'
        self.temp_path = os.path.join(self.root, '_update_tmp', 'minecraft')
        self.temp_mods_path = os.path.join(self.temp_path, 'overrides', 'mods')
        self.local_paths = [
            os.path.join(self.install_path, 'mods'),
            os.path.join(self.install_path, 'mods-old'),
            self.temp_mods_path
        ]
        self.install_path = game_state.get('instance')
        self.nazarick_json_path = os.path.join(self.install_path, 'nazarick.json')
        self.executable_path = game_state.get('executable')
        self.purge_whitelist=['config', 'shaderpacks']
        self.exe_name = os.path.split(self.executable_path)[-1]
        self.command = [self.executable_path]
        self.user_input_checks = [
            {
                'value': self.install_path,
                'no_value': 'Please provide a path to your Minecraft instance.',
                'conditional': os.path.exists,
                'conditional_failed': 'The provided path to your Minecraft instance doesn\'t exist.',
                'check_access': True,
                'access_failed': 'The instance path requires administrative privileges. Please restart your launcher.'
            },
            {
                'value': self.executable_path,
                'no_value': 'Please provide a path to your launcher\'s executable.',
                'conditional': os.path.exists,
                'conditional_failed': 'The provided path to your launcher doesn\'t exist.',
                'check_access': False,
                'access_failed': ''
            },
        ]


    def install_update(self):
        mods_tmp = os.path.join(self.temp_path, 'overrides', 'mods')
        custommods_tmp = os.path.join(self.temp_path, 'custommods')

        self.log('[INFO] Installing the modpack to specified destination.')

        # Move user added mods to the tmp path
        if os.path.exists(custommods_tmp):
            for mod in os.listdir(custommods_tmp):
                shutil.move(
                    os.path.join(custommods_tmp, mod),
                    os.path.join(mods_tmp, mod)
                )

        # Move overrides to main destination
        futures = []

        override_directory = os.path.join(self.temp_path, 'overrides')
        for override in os.listdir(override_directory):
            futures.append(
                self.pool.submit(self.move_override, override)
            )

        wait(futures)


    def move_override(self, override):
        override_path = os.path.join(self.temp_path, 'overrides', override)
        destination = os.path.join(self.install_path, override)

        # Ensure program is not operating in override or destination locations
        if os.getcwd() in [override_path, destination]:
            os.chdir(self.temp_path)

        # Move files without overwriting user-added files
        match override:
            case 'mods' | 'scripts' | 'packmenu' | 'patchouli_books':
                filesystem.move_files(override_path, destination)
            case _:
                filesystem.move_files(override_path, destination, overwrite=False)