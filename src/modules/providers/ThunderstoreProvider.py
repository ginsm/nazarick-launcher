import json, os, requests
from modules import constants
from modules.providers.ProviderAbstract import ProviderAbstract


class ThunderstoreProviderBase(ProviderAbstract):
    def download_mod(self, updater, mod_data, local_paths, destination):
        mod_name = mod_data # the mod_data is just the name of the plugin (including version)
        mod_download_url = f"https://thunderstore.io/package/download/{mod_name.replace('-', '/')}"

        normalized_mod_data = {
            "mod_name": mod_name + ".zip",
            "mod_download_url": mod_download_url
        }

        super().download_mod(updater, normalized_mod_data, local_paths, destination)


    def move_custom_mods(self, mods_dir, updater, mod_index, ignore=[]):
        raise NotImplementedError


    # The second parameter of the abstract method, game, is unused, as denoted by _.
    def get_latest_modpack_version(self, _, modpack):
        package = modpack.get('project') # see game_list.py
        req = requests.get(f'https://thunderstore.io/api/experimental/package/{package}', timeout=constants.DOWNLOAD_TIMEOUTS)

        if req.status_code != 200:
            return False

        content = json.loads(req.text)

        return {
            'name': content['full_name'],
            'version': content['latest']['version_number'],
            'url': content['latest']['download_url']
        }


    def download_modpack(self, updater):
        result = super().download_modpack(updater)

        if result is not True:
            raise Exception(f"Invalid from Thunderstore while downloading modpack: {updater.version.get('name')}.")


    def extract_modpack(self, updater, game, pack):
        return super().extract_modpack(updater, game, pack)


    def get_modpack_modlist(self, updater):
        raise NotImplementedError


    def initial_install(self, updater):
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


    def initial_install(self, updater):
        pass
