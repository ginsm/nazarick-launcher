import requests
from modules import constants
from modules.providers.ProviderAbstract import ProviderAbstract

class CurseForgeProviderBase(ProviderAbstract):
    def get_latest_modpack_version(self):
        raise NotImplementedError
        
    def download_modpack(self, variables):
        raise NotImplementedError
        
    def extract_modpack(self, variables, game):
        raise NotImplementedError
    
    def get_download_url(self, mod_data):
        mod_id, file_id = [
        mod_data.get('projectID'),
        mod_data.get('fileID')
        ]

        # Request file information
        req = requests(f'https://api.curseforge.com/v1/mods/{mod_id}/files/{file_id}', headers={
            'Accept': 'application/json',
            'x-api-key': constants.CURSEFORGE_API_KEY
        })

        # Get file url and name and return
        if req.status_code == 200:
            contents = req.json()
            mod_download_url = contents.get('downloadUrl')
            mod_name = contents.get('displayName')
            return [mod_download_url, mod_name]
        else:
            raise Exception(f'Invalid response from CurseForge API while retrieving file data for mod {mod_id}, file {file_id}.')

    def download_mod(self, log, mod_data, destination):
        mod_download_url, mod_name = self.get_download_url(mod_data)

        req = requests.get(mod_download_url, allow_redirects=True)

        if req.status_code == 200:
            log(f'[INFO] (D) {mod_name}')
            open(destination.get('destination'), 'wb').write(req.content)

        else:
            raise Exception(f'Invalid response from CurseForge while downloading mod: {mod_name}.')


class CurseForgeMinecraftProvider(CurseForgeProviderBase):
    def initial_modpack_install(self):
        pass

    def move_custom_mods(self, variables={}, mod_index=[], ignore=[]):
        raise NotImplementedError