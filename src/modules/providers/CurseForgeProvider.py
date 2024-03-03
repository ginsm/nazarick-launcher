import json
import os
import requests
from modules import constants
from modules.providers.ProviderAbstract import ProviderAbstract
from modules.updater.common import check_local_mod_paths

class CurseForgeProviderBase(ProviderAbstract):
    def download_mod(self, log, mod_data, local_paths, destination):
        mod_data = self.get_download_info(mod_data)
        mod_name = mod_data.get('file')
        destination = os.path.join(destination, mod_name)

        if check_local_mod_paths(log, local_paths, destination, mod_name):
            return
        
        if not mod_data.get('url'):
            raise Exception(mod_name)

        req = requests.get(mod_data.get('url'), allow_redirects=True)

        if req.status_code == 200:
            log(f'[INFO] (D) {mod_name}')
            open(destination, 'wb').write(req.content)
        else:
            raise Exception(mod_name)
        
        
    def move_custom_mods(self, mods_dir='', variables={}, mod_index=[], ignore=[]):
        raise NotImplementedError
        

    def get_latest_modpack_version(self, _, modpack):
        project_id, file_id, game_version = [
            modpack.get('project'),
            modpack.get('file'),
            modpack.get('game_version')
        ]
        download_info = False

        # Get latest version file
        if file_id == 'latest':
            file_id = self.get_latest_version_file(
                project_id,
                game_version
            )
        
        # Get download info
        download_info = self.get_download_info({
            'projectID': project_id,
            'fileID': file_id
        })

        return {
            'name': modpack.get('name'),
            'version': download_info.get('file'),
            'url': download_info.get('url')
        } if download_info else False
        

    def download_modpack(self, variables):
        req = super().download_modpack(variables)

        if req.status_code != 200:
            raise Exception(f'Invalid response from SelfHosted while downloading modpack: {variables['version']['name']}.')
        

    def extract_modpack(self, variables, game, pack):
        return super().extract_modpack(variables, game, pack)
    

    def get_modpack_modlist(self, variables):
        manifest_json_path = os.path.join(variables.get('tmp'), 'manifest.json')
        contents = open(manifest_json_path, 'r').read()
        files = json.loads(contents).get('files')
        return files


    def initial_modpack_install(self, variables):
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
        

    def get_latest_version_file(self, project_id, game_version):
            # Get project data
            req = requests(f'https://api.curseforge.com/v1/mods/{project_id}')
            if req.status_code != 200:
                return False
            
            # Look for latest mod version (for respective game_version)
            content = json.loads(req.text)
            for version in content.get('latestFilesIndexes'):
                if version.get('gameVersion') == game_version:
                    return version.get('fileId')



class CurseForgeMinecraftProvider(CurseForgeProviderBase):
    def initial_modpack_install(self, variables):
        inst_path = variables['instpath']
        configpath = os.path.join(inst_path, 'config')
        modspath = os.path.join(inst_path, 'mods')

        def move_existing_files(path):
            if os.path.exists(path):
                os.rename(path, f'{path}-old')

        move_existing_files(configpath)
        move_existing_files(modspath)


    def move_custom_mods(self, variables={}, mod_index=[], ignore=[]):
        raise NotImplementedError