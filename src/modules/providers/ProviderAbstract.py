from abc import ABC, abstractmethod
import os
import shutil
import zipfile

import requests

from modules.updater.common import extract_modpack_changelog

class ProviderAbstract(ABC):
    # Mod specific methods
    @abstractmethod
    def download_mod(self, log, mod_data, destination):
        raise NotImplementedError
    
    @abstractmethod
    def move_custom_mods(self, mods_dir = '', variables = {}, mod_index = [], ignore = []):
        log, tmp = [
            variables['log'],
            variables['tmp']
        ]

        log('[INFO] Moving user added mods.')

        destination = os.path.join(tmp, 'custommods')

        # Create custommods directory
        os.makedirs(destination, exist_ok=True)

        mods = os.listdir(mods_dir)

        # This is needed to prevent file being used by another process error
        os.chdir(tmp)

        for mod in mods:
            if mod not in mod_index and mod not in ignore:
                log(f'[INFO] (M) {mod}')
                shutil.move(
                    os.path.join(mods_dir, mod),
                    os.path.join(destination, mod)
                )
    
    # Modpack specific methods
    @abstractmethod
    def get_latest_modpack_version(self):
        raise NotImplementedError
    
    @abstractmethod
    def download_modpack(self, variables):
        log, tmp, version = [
            variables['log'],
            variables['tmp'],
            variables['version']
        ]

        log(f'[INFO] Downloading latest version: {version['name']} - {version['version']}.')

        # Download the file as .zip
        req = requests.get(version.get('url'), allow_redirects=True)

        if req.status_code == 200:
            open(os.path.join(tmp, 'update.zip'), 'wb').write(req.content)
            
        return req
    
    @abstractmethod
    def extract_modpack(self, variables, game, pack):
        log, tmp = [
            variables['log'],
            variables['tmp']
        ]

        zip_file = os.path.join(tmp, 'update.zip')

        log('[INFO] Extracting the modpack zip.')

        with zipfile.ZipFile(zip_file, 'r') as ref:
            ref.extractall(tmp)

        # Remove update.zip
        os.remove(zip_file)

        extract_modpack_changelog(variables, game, pack)
    
    @abstractmethod
    def initial_modpack_install(self):
        raise NotImplementedError