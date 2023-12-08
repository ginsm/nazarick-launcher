from abc import ABC, abstractmethod
import os
import zipfile

import requests

from modules.updater.common import extract_modpack_changelog

class ModpackProviderAbstract(ABC):
    @abstractmethod
    def get_latest_version():
        raise NotImplementedError
    
    @abstractmethod
    def initial_install():
        raise NotImplementedError

    @abstractmethod
    def download(self, variables):
        log, tmp, version = [
            variables['log'],
            variables['tmp'],
            variables['version']
        ]

        log(f'[INFO] Downloading latest version: {version['name']} {version['version']}.')

        # Download the file as .zip
        req = requests.get(version.get('url'), allow_redirects=True)

        if req.status_code == 200:
            open(os.path.join(tmp, 'update.zip'), 'wb').write(req.content)
        
        return req

    @abstractmethod
    def extract(self, variables, game):
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

        extract_modpack_changelog(variables, game)