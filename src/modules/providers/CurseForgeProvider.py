import json
import requests
from modules import constants
from modules.providers.ProviderAbstract import ProviderAbstract

class CurseForgeProviderBase(ProviderAbstract):
    def download_mod(self, log, mod_data, destination):
        download_info = self.get_download_info(mod_data)

        req = requests.get(download_info.get('url'), allow_redirects=True)

        if req.status_code == 200:
            log(f'[INFO] (D) {download_info.get('file')}')
            open(destination.get('destination'), 'wb').write(req.content)

        else:
            raise Exception(f'Invalid response from CurseForge while downloading mod: {download_info.get('file')}.')
        
        
    def move_custom_mods(self, mods_dir='', variables={}, mod_index=[], ignore=[]):
        raise NotImplementedError
        

    def get_latest_modpack_version(self, _, modpack):
        project_id, file_id, game_version = [
            modpack.get('project'),
            modpack.get('file'),
            modpack.get('game_version')
        ]
        download_info = False

        if file_id == 'latest':
            req = requests(f'https://api.curseforge.com/v1/mods/{project_id}')

            if req.status_code != 200:
                return False
            
            content = json.loads(req.text)
            
            for version in content.get('latestFilesIndexes'):
                if version.get('gameVersion') == game_version:
                    download_info = self.get_download_info({
                        'projectID': project_id,
                        'fileID': version.get('fileId')
                    })
        else:
            download_info = self.get_download_info({
                'projectID': project_id,
                'fileID': file_id
            })

        return {
            'name': download_info.get('name'),
            'version': download_info.get('file'),
            'url': download_info.get('url')
        } if download_info else False
        

    def download_modpack(self, variables):
        req = super().download_modpack(variables)

        if req.status_code != 200:
            raise Exception(f'Invalid response from SelfHosted while downloading modpack: {variables['version']['name']}.')
        

    def extract_modpack(self, variables, game, pack):
        return super().extract_modpack(variables, game, pack)
    

    def initial_modpack_install(self):
        pass
    

    # NOTE - Below are helper methods, that aren't part of the ProviderAbstract interface.
    def get_download_info(self, mod_data):
        mod_id, file_id = [
            mod_data.get('projectID'),
            mod_data.get('fileID')
        ]

        # Request file information
        req = requests.get(f'https://api.curseforge.com/v1/mods/{mod_id}/files/{file_id}', headers={
            'Accept': 'application/json',
            'x-api-key': constants.CURSEFORGE_API_KEY
        }, timeout=10)

        # Get file url and name and return
        if req.status_code == 200:
            contents = req.json().get('data')
            return {
                'url': contents.get('downloadUrl'),
                'name': contents.get('displayName'),
                'file': contents.get('fileName')
            }
        else:
            raise Exception(f'Invalid response from CurseForge API while retrieving file data for mod {mod_id}, file {file_id}.')



class CurseForgeMinecraftProvider(CurseForgeProviderBase):
    def initial_modpack_install(self):
        pass


    def move_custom_mods(self, variables={}, mod_index=[], ignore=[]):
        raise NotImplementedError