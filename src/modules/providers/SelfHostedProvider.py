import json
import os
import requests
from modules import constants
from modules.providers.ProviderAbstract import ProviderAbstract


class SelfHostedProviderBase(ProviderAbstract):
    def download_mod(self, updater, mod_data, local_paths, destination):
        raise NotImplementedError
    
    def move_custom_mods(self, mods_dir, updater, mod_index, ignore=[]):
        raise NotImplementedError

    def get_latest_modpack_version(self, game, modpack):
        website = constants.SELFHOSTED_WEBSITE
        pack = modpack.get('project')
        req = requests.get(f'{website}/modpacks/manifest.json')

        if (req.status_code != 200):
            return False
        
        content = json.loads(req.text)
        version_data = content.get(game.lower()).get(pack).get('versions')[0]
        version_data.update({'url': f'{website}{version_data.get('url')}'})

        return content.get(game.lower()).get(pack).get('versions')[0]
    
    def download_modpack(self, updater):
        req = super().download_modpack(updater)

        if req.status_code != 200:
            raise Exception('Invalid response from SelfHosted (modpack)')
    
    def extract_modpack(self, updater, game, pack):
        return super().extract_modpack(updater, game, pack)
    
    def get_modpack_modlist(self, updater):
        raise NotImplementedError
    
    def initial_modpack_install(self, updater):
        raise NotImplementedError



class SelfHostedMinecraftProvider(SelfHostedProviderBase):
    def initial_modpack_install(self, updater):
        inst_path = updater.install_path
        configpath = os.path.join(inst_path, 'config')
        modspath = os.path.join(inst_path, 'mods')

        def move_existing_files(path):
            if os.path.exists(path):
                os.rename(path, f'{path}-old')

        move_existing_files(configpath)
        move_existing_files(modspath)

    def move_custom_mods(self, updater, mod_index):
        instance_path = updater.install_path
        mods_dir = os.path.join(instance_path, 'mods')
                
        super().move_custom_mods(mods_dir, updater, mod_index)