import json, os, requests
from modules import constants, filesystem
from modules.providers.ProviderAbstract import ProviderAbstract

class CurseForgeProviderBase(ProviderAbstract):
    def download_mod(self, updater, mod_data, local_paths, destination):
        mod_data = self.get_download_info(mod_data)
        mod_name = mod_data.get('file')
        
        normalized_mod_data = {
            "mod_download_url": mod_data.get('url'),
            "mod_name": mod_name
        }
        
        super().download_mod(updater, normalized_mod_data, local_paths, destination)


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
        result = super().download_modpack(updater)

        if result is not True:
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
        }, timeout=constants.DOWNLOAD_TIMEOUTS)

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
            req = requests.get(f'https://api.curseforge.com/v1/mods/{project_id}', timeout=constants.DOWNLOAD_TIMEOUTS)
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