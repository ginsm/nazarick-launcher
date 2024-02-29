import json
import os
import requests
from modules import constants
from modules.providers.ProviderAbstract import ProviderAbstract


class SelfHostedProviderBase(ProviderAbstract):
    def download_mod(self, log, mod_data, destination):
        raise NotImplementedError
    
    def move_custom_mods(self, mods_dir='', variables={}, mod_index=[], ignore=[]):
        raise NotImplementedError

    def get_latest_modpack_version(self, game, modpack):
        website = constants.SELFHOSTED_WEBSITE
        pack = modpack.get('name')
        req = requests.get(f'{website}/modpacks/manifest.json')

        if (req.status_code != 200):
            return False
        
        content = json.loads(req.text)

        version_data = content.get(game).get(pack).get('versions')[0]
        version_data.update({'url': f'{website}{version_data.get('url')}'})

        return content.get(game).get(pack).get('versions')[0]
    
    def download_modpack(self, variables):
        req = super().download_modpack(variables)

        if req.status_code != 200:
            raise Exception('Invalid response from SelfHosted (modpack)')
    
    def extract_modpack(self, variables, game):
        return super().extract_modpack(variables, game)
    
    def initial_modpack_install(self):
        raise NotImplementedError



class SelfHostedMinecraftProvider(SelfHostedProviderBase):
    def initial_modpack_install(self, variables):
        inst_path = variables['instpath']
        configpath = os.path.join(inst_path, 'config')
        modspath = os.path.join(inst_path, 'mods')

        def move_existing_files(path):
            if os.path.exists(path):
                os.rename(path, f'{path}-old')

        move_existing_files(configpath)
        move_existing_files(modspath)

    def move_custom_mods(self, variables, mod_index):
        instance_path = variables['instpath']
        mods_dir = os.path.join(instance_path, 'mods')
                
        super().move_custom_mods(mods_dir, variables, mod_index)