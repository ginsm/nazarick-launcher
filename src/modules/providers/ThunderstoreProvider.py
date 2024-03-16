import json
import os
import zipfile
import requests
from modules.providers.ProviderAbstract import ProviderAbstract


class ThunderstoreProviderBase(ProviderAbstract):
    def download_mod(self, updater, mod_data, local_paths, destination):
        plugin = mod_data
        plugin_url = f"https://thunderstore.io/package/download/{plugin.replace('-', '/')}"
        plugin_dest = os.path.join(destination, plugin)
        plugin_zip = plugin_dest + '.zip'

        req = requests.get(plugin_url, allow_redirects=True)

        if updater.check_local_mod_paths(local_paths, destination, plugin):
            return

        if req.status_code == 200:
            updater.log(f'[INFO] (D) {plugin}')
            with open(plugin_zip, 'wb') as file:
                file.write(req.content)

            with zipfile.ZipFile(plugin_zip, 'r') as ref:
                ref.extractall(plugin_dest)

            os.remove(plugin_zip)
        else:
            raise Exception(plugin)


    def move_custom_mods(self, mods_dir, updater, mod_index, ignore=[]):
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


    def download_modpack(self, updater):
        req = super().download_modpack(updater)

        if req.status_code != 200:
            raise Exception(f'Invalid from Thunderstore while downloading modpack: {updater.version.get('name')}.')


    def extract_modpack(self, updater, game, pack):
        return super().extract_modpack(updater, game, pack)


    def get_modpack_modlist(self, updater):
        raise NotImplementedError


    def initial_modpack_install(self, updater):
        raise NotImplementedError



class ThunderstoreValheimProvider(ThunderstoreProviderBase):
    def move_custom_mods(self, updater, mod_index, ignore=[]):
        install_path = updater.install_path
        plugins_dir = os.path.join(install_path, 'BepInEx', 'plugins')
        ignore = ['Valheim.DisplayBepInExInfo.dll']

        return super().move_custom_mods(plugins_dir, updater, mod_index, ignore)


    def get_modpack_modlist(self, updater):
        manifest_json_path = os.path.join(updater.temp_path, 'manifest.json')
        contents = open(manifest_json_path, 'r').read()
        dependencies = json.loads(contents).get('dependencies')
        return dependencies


    def initial_modpack_install(self, updater):
        pass
