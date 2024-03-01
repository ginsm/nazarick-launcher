import json
import os
import zipfile
import requests
from modules.providers.ProviderAbstract import ProviderAbstract


class ThunderstoreProviderBase(ProviderAbstract):
    def download_mod(self, log, mod_data, destination):
        plugin = mod_data['name']
        plugin_url = f"https://thunderstore.io/package/download/{plugin.replace('-', '/')}"
        plugin_zip = destination + '.zip'

        req = requests.get(plugin_url, allow_redirects=True)

        if req.status_code == 200:
            log(f'[INFO] (D) {plugin}')
            open(plugin_zip, 'wb').write(req.content)

            with zipfile.ZipFile(plugin_zip, 'r') as ref:
                ref.extractall(destination)

            os.remove(plugin_zip)
        else:
            raise Exception(f'Invalid response from Thunderstore while downloading plugin: {plugin}.')
        
    def move_custom_mods(self, mods_dir='', variables={}, mod_index=[], ignore=[]):
        raise NotImplementedError

    # The second parameter of the abstract method, game, is unused, as denoted by _.
    def get_latest_modpack_version(self, _, modpack):
        package = modpack.get('project') # see game_list.py
        req = requests.get(f'https://thunderstore.io/api/experimental/package/{package}')

        if req.status_code != 200:
            return False
        
        content = json.loads(req.text)

        return {
            'name': content['full_name'],
            'version': content['latest']['version_number'],
            'url': content['latest']['download_url']
        }
    
    def download_modpack(self, variables):
        req = super().download_modpack(variables)

        if req.status_code != 200:
            raise Exception(f'Invalid from Thunderstore while downloading modpack: {variables['version']['name']}.')
        
    def extract_modpack(self, variables, game, pack):
        return super().extract_modpack(variables, game, pack)
    
    def initial_modpack_install(self):
        raise NotImplementedError



class ThunderstoreValheimProvider(ThunderstoreProviderBase):
    def initial_modpack_install(self):
        pass

    def move_custom_mods(self, variables={}, mod_index=[], ignore=[]):
        install_path = variables['instpath']
        plugins_dir = os.path.join(install_path, 'BepInEx', 'plugins')
        ignore = ['Valheim.DisplayBepInExInfo.dll']

        return super().move_custom_mods(plugins_dir, variables, mod_index, ignore)
