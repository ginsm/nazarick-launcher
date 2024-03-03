import json
import os
import zipfile
import requests
from modules.providers.ProviderAbstract import ProviderAbstract
from modules.updater.common import check_local_mod_paths


class ThunderstoreProviderBase(ProviderAbstract):
    def download_mod(self, log, mod_data, local_paths, destination):
        plugin = mod_data
        plugin_url = f"https://thunderstore.io/package/download/{plugin.replace('-', '/')}"
        plugin_dest = os.path.join(destination, plugin)
        plugin_zip = plugin_dest + '.zip'

        req = requests.get(plugin_url, allow_redirects=True)

        if check_local_mod_paths(log, local_paths, destination, plugin):
            return

        if req.status_code == 200:
            log(f'[INFO] (D) {plugin}')
            open(plugin_zip, 'wb').write(req.content)

            with zipfile.ZipFile(plugin_zip, 'r') as ref:
                ref.extractall(plugin_dest)

            os.remove(plugin_zip)
        else:
            raise Exception(plugin)
        

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
    

    def get_modpack_modlist(self, variables):
        raise NotImplementedError
    

    def initial_modpack_install(self, variables):
        raise NotImplementedError



class ThunderstoreValheimProvider(ThunderstoreProviderBase):
    def move_custom_mods(self, variables={}, mod_index=[], ignore=[]):
        install_path = variables['instpath']
        plugins_dir = os.path.join(install_path, 'BepInEx', 'plugins')
        ignore = ['Valheim.DisplayBepInExInfo.dll']

        return super().move_custom_mods(plugins_dir, variables, mod_index, ignore)


    def get_modpack_modlist(self, variables):
        manifest_json_path = os.path.join(variables.get('tmp'), 'manifest.json')
        contents = open(manifest_json_path, 'r').read()
        dependencies = json.loads(contents).get('dependencies')
        return dependencies


    def initial_modpack_install(self, variables):
        pass
