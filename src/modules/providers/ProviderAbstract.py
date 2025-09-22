from abc import ABC, abstractmethod
import os, shutil, zipfile

from modules import constants, filesystem, network

class ProviderAbstract(ABC):
    # Mod specific methods
    @abstractmethod
    def download_mod(self, updater, mod_data, local_paths, destination):
        """
        Expects mod_data to contain:
        - mod_download_url
        - mod_name
        """
        mod_download_url = mod_data.get('mod_download_url')
        mod_name = os.path.basename(mod_data.get('mod_name'))

        if not mod_name:
            raise Exception("missing mod name: " + mod_data)
        if not mod_download_url:
            raise Exception(f"missing mod_download_url for {mod_name}")

        # Add mod name to destination if missing.
        if not destination.endswith(mod_name):
            destination = os.path.join(destination, mod_name)

        # Skip if the user already has the file somewhere local
        if updater.check_local_mod_paths(local_paths, destination, mod_name):
            return

        # Ensure parent directory exists
        destination_dir = os.path.dirname(destination)
        os.makedirs(destination_dir, exist_ok=True)

        # Add mod_name to destination and create temp path
        temp_path = destination + ".part"

        written = 0
        total = 0

        try:
            with network.per_host_semaphore(mod_download_url):
                with updater.session.get(
                    mod_download_url,
                    stream=True,
                    allow_redirects=True,
                    timeout=constants.DOWNLOAD_TIMEOUTS
                ) as r:
                    r.raise_for_status()
                    total = int(r.headers.get("Content-Length") or 0)
                    chunk = 512 * 1024
                    with open(temp_path, "wb") as f:
                        for data in r.iter_content(chunk_size=chunk):
                            if updater.cancel:
                                break
                            if not data:
                                continue
                            f.write(data)
                            written += len(data)

            if total and written != total:
                raise IOError(f"Incomplete download for {mod_name}: {written}/{total}")

            os.replace(temp_path, destination)

            if updater.unzip_mods and zipfile.is_zipfile(destination):
                split_ext = os.path.splitext(destination)
                ext = split_ext[1]
                extract_dir = split_ext[0]
                allowed_ext = {".zip", ".mrpack"}

                if ext in allowed_ext:
                    if not updater.unzip_into_subdir:
                        extract_dir = destination_dir

                    with zipfile.ZipFile(destination, "r") as zf:
                        filesystem.safe_extract(zf, extract_dir)

                    try:
                        os.remove(destination)
                    except OSError:
                        pass
                updater.logger.info(f'(DX) {mod_name}')

            else:
                updater.logger.info(f'(D) {mod_name}')


        except Exception:
            # Clean up partial file on any failure
            try:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
            except OSError:
                pass
            raise


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

        logger.info(f"Downloading latest version: {version.get('name')} ({version.get('version')}) for {updater.game}.")

        os.makedirs(tmp, exist_ok=True)
        destination = os.path.join(tmp, "update.zip")
        temp_path = destination + ".part"

        chunk = 512 * 1024
        target_progress = 0.30
        progress_added = 0.0

        written = 0
        total = 0

        try:
            with updater.session.get(
                version.get("url"),
                stream=True,
                allow_redirects=True,
                timeout=constants.DOWNLOAD_TIMEOUTS
            ) as r:
                r.raise_for_status()
                total = int(r.headers.get("Content-Length") or 0)

                with open(temp_path, "wb") as f:
                    for data in r.iter_content(chunk_size=chunk):
                        if updater.cancel:
                            break
                        if not data:
                            continue
                        f.write(data)
                        written += len(data)
                        
                        # Calculate percentage to add
                        if total > 0:
                            increment_percentage = (len(data) / total) * target_progress
                        # Unknown data size fallback (based on a 60MB pack)
                        # NOTE - Maybe make an updater-specific fallback
                        else:
                            increment_percentage = target_progress / 120.0

                        # Clamp so we never exceed target_progress due to rounding
                        remaining = target_progress - progress_added
                        if increment_percentage > remaining:
                            increment_percentage = remaining

                        if increment_percentage > 0:
                            progress_bar.add_percent(increment_percentage)
                            progress_added += increment_percentage

            if total and written != total:
                # Clean up partial, failed downloads
                try:
                    os.remove(temp_path)
                except OSError:
                    pass
                raise IOError(f"Incomplete modpack: {written}/{total}")

            # Handle any cases where not enough progress was added (specifically if the total size isn't known)
            if progress_added < target_progress:
                progress_bar.add_percent(target_progress - progress_added)
                progress_added = target_progress

            os.replace(temp_path, destination)
            logger.debug(f"Downloaded {written} bytes to update.zip")
            return True

        except Exception:
            # Best-effort cleanup
            try:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
            except OSError:
                pass
            raise


    @abstractmethod
    def extract_modpack(self, updater, game, pack):
        logger, tmp = [
            updater.logger,
            updater.temp_path
        ]

        zip_file = os.path.join(tmp, 'update.zip')

        # This doesn't mean that the zip file didn't download -- it could have been extracted already in a previous update. So, just return, 
        # and the updater will error out if any of the necessary files are missing from the zip downstream.
        if not os.path.exists(zip_file):
            return
        
        # If it did download, and it's not a zip file, proceed to cancel the update and alert the user.
        if not zipfile.is_zipfile(zip_file):
            updater.logger.warning("Modpack archive is not a zip file. Aborting update process.")
            updater.logger.debug(f"Zipfile location: {zip_file}")
            updater.cancel = True
            return

        logger.info('Extracting the modpack zip.')

        with zipfile.ZipFile(zip_file, 'r') as zf:
            filesystem.safe_extract(zf, tmp)

        # Remove update.zip
        os.remove(zip_file)

        updater.extract_modpack_changelog(game, pack)


    @abstractmethod
    def get_modpack_modlist(self, updater):
        raise NotImplementedError


    @abstractmethod
    def initial_install(self, updater):
        raise NotImplementedError