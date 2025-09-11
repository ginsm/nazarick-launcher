from abc import ABC, abstractmethod
import os
import shutil
import zipfile

import requests

class ProviderAbstract(ABC):
    # Mod specific methods
    @abstractmethod
    def download_mod(self, updater, mod_data, local_paths, destination):
        raise NotImplementedError

    @abstractmethod
    def move_custom_mods(self, mods_dir, updater, mod_index, ignore = []):
        logger, tmp = [
            updater.logger,
            updater.temp_path
        ]

        logger.info('Moving user added mods.')

        destination = os.path.join(tmp, 'custommods')

        # Create custommods directory
        os.makedirs(destination, exist_ok=True)

        mods = os.listdir(mods_dir)

        # This is needed to prevent file being used by another process error
        os.chdir(tmp)

        for mod in mods:
            if mod not in mod_index and mod not in ignore:
                logger.info(f'(M) {mod}')
                shutil.move(
                    os.path.join(mods_dir, mod),
                    os.path.join(destination, mod)
                )

    # Modpack specific methods
    @abstractmethod
    def get_latest_modpack_version(self):
        raise NotImplementedError

    @abstractmethod
    def download_modpack(self, updater):
        logger, tmp, version, progress_bar = [
            updater.logger,
            updater.temp_path,
            updater.version,
            updater.widgets.get('progressbar')
        ]

        logger.info(f'Downloading latest version: {version['name']} ({version['version']}) for {updater.game}.')

        # Download the file as .zip
        req = requests.get(version.get('url'), stream=True, allow_redirects=True, timeout=15)

        if req.status_code == 200:
            with open(os.path.join(tmp, 'update.zip'), 'wb') as file:
                total_length = req.headers.get('content-length')

                if total_length is None:
                    file.write(req.content)
                else:
                    total_length = int(total_length)
                    chunk_size = int(total_length / 60)
                    logger.debug(f'Downloading {total_length} bytes with a chunk size of {chunk_size}.')
                    for data in req.iter_content(chunk_size=chunk_size):
                        file.write(data)
                        progress_bar.add_percent(0.005)

        return req

    @abstractmethod
    def extract_modpack(self, updater, game, pack):
        logger, tmp = [
            updater.logger,
            updater.temp_path
        ]

        zip_file = os.path.join(tmp, 'update.zip')

        if not os.path.exists(zip_file):
            return

        logger.info('Extracting the modpack zip.')

        with zipfile.ZipFile(zip_file, 'r') as ref:
            ref.extractall(tmp)

        # Remove update.zip
        os.remove(zip_file)

        updater.extract_modpack_changelog(game, pack)

    @abstractmethod
    def get_modpack_modlist(self, updater):
        raise NotImplementedError

    @abstractmethod
    def initial_install(self, updater):
        raise NotImplementedError