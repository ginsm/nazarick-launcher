import json
import os
import requests
from modules import constants, filesystem
from modules.providers.ProviderAbstract import ProviderAbstract

class CurseForgeProviderBase(ProviderAbstract):
    def download_mod(self, updater, mod_data, local_paths, destination):
        mod_data = self.get_download_info(mod_data)
        mod_name = mod_data.get('file')
        destination = os.path.join(destination, mod_name)

        if updater.check_local_mod_paths(local_paths, destination, mod_name):
            return

        if not mod_data.get('url'):
            raise Exception(mod_name)

        req = requests.get(mod_data.get('url'), allow_redirects=True, timeout=(10,45))

        if req.status_code == 200:
            updater.logger.info(f'(D) {mod_name}')
            with open(destination, 'wb') as file:
                file.write(req.content)
        else:
            raise Exception(mod_name)


    def move_custom_mods(self, mods_dir, updater, mod_index, ignore=[]):
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


    def download_modpack(self, updater):
        req = super().download_modpack(updater)

        if req.status_code != 200:
            raise Exception(f"Invalid response from SelfHosted while downloading modpack: {updater.version.get('name')}.")


    def extract_modpack(self, updater, game, pack):
        return super().extract_modpack(updater, game, pack)


    def get_modpack_modlist(self, updater):
        manifest_json_path = os.path.join(updater.temp_path, 'manifest.json')
        with open(manifest_json_path, 'r') as file:
            contents = file.read()
            return json.loads(contents).get('files')


    def initial_install(self, updater):
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
        }, timeout=(10,45))

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
            req = requests.get(f'https://api.curseforge.com/v1/mods/{project_id}', timeout=(10,45))
            if req.status_code != 200:
                return False

            # Look for latest mod version (for respective game_version)
            content = json.loads(req.text)
            for version in content.get('latestFilesIndexes'):
                if version.get('gameVersion') == game_version:
                    return version.get('fileId')



class CurseForgeMinecraftProvider(CurseForgeProviderBase):
    def initial_install(self, updater):
        destination = os.path.join(updater.install_path, 'instance-backup')
        overrides_path = os.path.join(updater.temp_path, 'overrides')
        overrides = {'mods', 'config'}
        existing_files = False

        if os.path.exists(overrides_path):
            files = os.listdir(overrides_path)
            for f in files:
                overrides.add(f)

        # Move any conflicting overrides to `instance-backup`
        for override in overrides:
            source = os.path.join(updater.install_path, override)
            target = os.path.join(destination, override)
            if os.path.exists(source):
                filesystem.move_files(source, target, overwrite=True)
                existing_files = True

        if existing_files:
            updater.logger.info("Moved existing instance files into 'instance-backup' folder.")