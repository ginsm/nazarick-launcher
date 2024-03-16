from concurrent.futures import wait
import os
import shutil
from modules import state_manager
from modules.filesystem import overwrite
from modules.updaters.AbstractGameUpdater import AbstractGameUpdater


class ValheimUpdater(AbstractGameUpdater):
    def initialize(self):
        # Get game state
        game_state = state_manager.get_pack_state('Valheim')

        # Begin initializing variables
        self.game = 'Valheim'

        # Paths used throughout update
        self.temp_path = os.path.join(self.root, '_update_tmp', 'valheim', self.modpack.get('name'))
        self.install_path = game_state.get('install')
        self.nazarick_json_path = os.path.join(self.install_path, 'nazarick.json')

        # Used by super.user_input_has_errors
        self.user_input_checks = [
            {
                'value': self.install_path,
                'no_value': 'Please provide a path to your Valheim install.',
                'conditional': os.path.exists,
                'conditional_failed': 'The provided path to your Valheim install doesn\'t exist.',
                'check_access': True,
                'access_failed': 'The install path requires administrative privileges. Please restart your launcher.'
            }
        ]

        # Used by super.purge
        self.purge_whitelist = ['BepInEx/config']

        # Used by super.retrieve_mods
        self.temp_mods_path = os.path.join(self.temp_path, 'plugins')
        self.local_paths = [
                os.path.join(self.install_path, 'BepInEx', 'plugins')
        ]

        # Used by super.run_executable
        self.exe_name = 'valheim.exe'
        self.command = ['cmd', '/c', 'start', 'steam://run/892970']
        

    def install_update(self):
        # Set up BepInEx
        self.setup_bepinex()

        # Move BepInEx files
        install_tmp = os.path.join(self.temp_path, 'install')

        # Iterate over install directory
        self.log('[INFO] Installing the modpack to the specified install path.')
        for file_ in os.listdir(install_tmp):
            file_path_loc = os.path.join(self.install_path, file_)
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


    def setup_bepinex(self):
        # Paths
        plugins_tmp = os.path.join(self.temp_path, 'plugins')
        config_tmp = os.path.join(self.temp_path, 'config')
        custommods_tmp = os.path.join(self.temp_path, 'custommods')
        install_tmp = os.path.join(self.temp_path, 'install')

        # Make install directory
        os.makedirs(install_tmp, exist_ok=True)

        self.log('[INFO] Setting up BepInEx.')

        # Move BepInEx into install directory
        for plugin in os.listdir(plugins_tmp):
            if 'BepInExPack' in plugin:
                bepinex_path = os.path.join(plugins_tmp, plugin, 'BepInExPack_Valheim')
                files = os.listdir(bepinex_path)
                futures = []

                for f in files:
                    futures.append(self.pool.submit(
                        shutil.move,
                        os.path.join(bepinex_path, f),
                        os.path.join(install_tmp, f)
                    ))

                wait(futures)
            
                # Remove BepInEx directory
                shutil.rmtree(os.path.join(plugins_tmp, plugin))
                break

        # Move plugins and configs to new BepInEx structure
        futures = []

        # Move plugins
        for plugin in os.listdir(plugins_tmp):
            futures.append(self.pool.submit(
                shutil.move,
                os.path.join(plugins_tmp, plugin),
                os.path.join(install_tmp, 'BepInEx', 'plugins', plugin)
            ))

        # Move configs
        for config in os.listdir(config_tmp):
            futures.append(self.pool.submit(
                shutil.move,
                os.path.join(config_tmp, config),
                os.path.join(install_tmp, 'BepInEx', 'config', config)
            ))

        # Move custom plugins
        if os.path.exists(custommods_tmp):
            for plugin in os.listdir(custommods_tmp):
                futures.append(self.pool.submit(
                    shutil.move,
                    os.path.join(custommods_tmp, plugin),
                    os.path.join(install_tmp, 'BepInEx', 'plugins', plugin)
                ))

        wait(futures)