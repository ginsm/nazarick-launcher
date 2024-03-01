import requests
from modules.providers.ProviderAbstract import ProviderAbstract

class ModrinthProviderBase(ProviderAbstract):
    def get_latest_modpack_version(self):
        raise NotImplementedError
        
    def download_modpack(self, variables):
        raise NotImplementedError
        
    def extract_modpack(self, variables, game, pack):
        raise NotImplementedError

    def download_mod(self, log, mod_data, destination):
        mod_download_url = mod_data.get('downloads')[0]
        mod_name = mod_data.get('name')

        req = requests.get(mod_download_url, allow_redirects=True)

        if req.status_code == 200:
            log(f'[INFO] (D) {mod_name}')
            open(destination, 'wb').write(req.content)

        else:
            raise Exception(f'Invalid response from Modrinth while downloading mod: {mod_name}.')


class ModrinthMinecraftProvider(ModrinthProviderBase):
    def initial_modpack_install(self):
        pass

    def move_custom_mods(self, variables={}, mod_index=[], ignore=[]):
        raise NotImplementedError
