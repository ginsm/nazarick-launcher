import json
import os
from modules.providers.ProviderAbstract import ProviderAbstract

class ModrinthProviderBase(ProviderAbstract):
    def download_mod(self, updater, mod_data, local_paths, destination):
        mod_download_url = mod_data.get('downloads')[0] if mod_data.get('downloads') else None
        mod_name = mod_data.get('name')
        
        normalized_mod_data = {
            "mod_download_url": mod_download_url,
            "mod_name": mod_name
        }
        
        super().download_mod(updater, normalized_mod_data, local_paths, destination)


    def move_custom_mods(self, mods_dir, updater, mod_index, ignore=[]):
        return super().move_custom_mods(mods_dir, updater, mod_index, ignore)


    def get_latest_modpack_version(self):
        raise NotImplementedError


    def download_modpack(self, updater):
        raise NotImplementedError


    def extract_modpack(self, updater, game, pack):
        raise NotImplementedError


    def get_modpack_modlist(self, game):
        raise NotImplementedError


    def initial_install(self, updater):
        pass



class ModrinthMinecraftProvider(ModrinthProviderBase):
    def initial_install(self, updater):
        destination = os.path.join(updater.install_path, 'instance-backup')
        overrides_path = os.path.join(updater.temp_path, 'overrides')
        overrides = {'mods', 'config'}
        existing_files = False

        if os.path.exists(overrides_path):
            files = os.listdir(overrides_path)
            for f in files:
                overrides.add(f)

        # Move any conflicting overrides to `instance-backup`
        for override in overrides:
            source = os.path.join(updater.install_path, override)
            target = os.path.join(destination, override)
            if os.path.exists(source):
                filesystem.move_files(source, target, overwrite=True)
                existing_files = True

        if existing_files:
            updater.logger.info("Moved existing instance files into 'instance-backup' folder.")


    def get_modpack_modlist(self, updater):
        modrinth_json_path = os.path.join(updater.temp_path, 'modrinth.index.json')

        with open(modrinth_json_path, 'r') as file:
            content = file.read()
            files = json.loads(content).get('files')

            for mod in files:
                filename = os.path.split(mod.get('path'))[1]
                mod.update(name=filename)

            return files
        

    def move_custom_mods(self, mods_dir, updater, mod_index, ignore=[]):
        raise NotImplementedError
