import os
from pathlib import Path
import shutil

from modules import constants, utility


def move_files(source, target, walk=False, overwrite=True):
    """
    Moves a file to a target destination. The behavior can be changed based
    on the `walk` and `overwrite` parameters.

    `walk`: Walk through the directory, checking whether each file should be
    moved.
    `overwrite`: Overwrite existing files (destructive).
    """
    # Iterate over directory's files
    if os.path.isdir(source) and walk:
        for file_ in os.listdir(source):
            file_path = os.path.join(source, file_)

            # Iterate through directories if overwrite is false
            if os.path.isdir(file_path):
                for root, _, files in os.walk(file_path):
                    for name in files:
                        root_path = os.path.join(root, name)

                        # Get target path
                        path_without_source = root_path.replace(source, "")[1:]
                        target_path = os.path.join(target, path_without_source)

                        # Ensure target root exists
                        target_root, _ = os.path.split(target_path)
                        os.makedirs(target_root, exist_ok=True)

                        # Move file if path doesn't exist or overwrite is enabled
                        if not os.path.exists(target_path) or overwrite:
                            shutil.move(root_path, target_path)

            # Move files outside of nested directories
            else:
                target_path = os.path.join(target, file_)

                if os.path.exists(target_path) and overwrite:
                    overwrite_path(file_path, target_path)

                if not os.path.exists(target_path):
                    # Create the root dir
                    target_root, _ = os.path.split(target_path)
                    os.makedirs(target_root, exist_ok=True)

                    # Move the source to the target location
                    shutil.move(file_path, target_path)

    # Attempt to move top-level files
    else:
        if os.path.exists(target) and overwrite:
            overwrite_path(source, target)

        if not os.path.exists(target):
            # Create the root dir
            target_root, _ = os.path.split(target)
            os.makedirs(target_root, exist_ok=True)

            # Move the source to the target location
            shutil.move(source, target)


def safe_delete(path, base_path, whitelist, logger):
    """
    This function removes a path based on several criteria:
    - The path is relative to the base path.
    - The path is not the base path itself.
    - The path is contained within the given whitelist; or the whitelist is empty.
    """
    if can_delete_path(base_path, path, whitelist):
        rm_func = shutil.rmtree if os.path.isdir(path) else os.remove
        rm_func(path)
        logger.info(f'(R) {path.replace(base_path, "")[1:]}')


def overwrite_path(source, target):
    """
    Overwrites the given target path, with the contents of the source path, if
    the source path exists.
    """
    if os.path.exists(source):
        target_root, _ = os.path.split(target)
        rm_func = shutil.rmtree if os.path.isdir(target) else os.remove

        if os.path.exists(target):
            rm_func(target)

        if not os.path.exists(target_root):
            os.makedirs(target_root, exist_ok=True)

        shutil.move(source, target)


# ---- HELPER FUNCTIONS ---- #
def path_is_relative(base: str, child: str) -> bool:
    try:
        Path(child).resolve().relative_to(Path(base).resolve())
        return True
    except Exception:
        return False


def can_delete_path(base_path, path, whitelist=[]) -> bool:
    """
    This function is a helper function to safe_delete. It checks whether the following
    three criterias are met:
    - The path is relative to the base path.
    - The path is not the base path itself.
    - The path is contained within the given whitelist; or the whitelist is empty.
    """
    # Variables
    path_abs = os.path.abspath(path)

    # Determine if the path is within the base path
    if not path_is_relative(base_path, path_abs):
        return False

    # Ensure the path exists
    if not os.path.exists(path_abs):
        return False

    # Ensure the file to delete is within a whitelisted directory
    # while ensuring the target isn't the directory itself.
    for dir_ in whitelist:
        base_whitelist_path = os.path.join(base_path, dir_)
        if (
            path_is_relative(base_whitelist_path, path_abs)
            and base_whitelist_path != path_abs
        ):
            return True

    # Allow any path within the base path if whitelist length is 0
    if path_is_relative(base_path, path_abs) and len(whitelist) == 0:
        return True

    return False

def safe_extract(zf, destination):
    destination = os.path.abspath(destination)

    files = zf.infolist()
    total_uncompressed = sum(_file.file_size for _file in files)
    total_compressed = sum(_file.compress_size for _file in files) or 1 # avoid div by 0 with default

    if len(files) > constants.MAX_ENTRY_COUNT:
        raise RuntimeError(f"Archive has too many entries: {len(files)} > {constants.MAX_ENTRY_COUNT}")

    if total_uncompressed > constants.MAX_TOTAL_UNCOMPRESSED:
        tuf = utility.formatted_bytes(total_uncompressed)
        raise RuntimeError(f"Archive uncompressed size too large: {tuf}")
    
    if (total_uncompressed / total_compressed) > constants.MAX_COMPRESSION_RATIO:
        tuf = utility.formatted_bytes(total_uncompressed)
        tcf = utility.formatted_bytes(total_compressed)
        raise RuntimeError(f"Suspicious compression ratio: {tuf} /{tcf} > {constants.MAX_COMPRESSION_RATIO}")

    for _file in files:
        dest = os.path.abspath(os.path.join(destination, _file.filename))

        if not path_is_relative(destination, dest):
            raise RuntimeError(f"Blocked zip path traversal: {_file.filename}")
        
        if _file.file_size > constants.MAX_FILE_SIZE:
            fsf = utility.formatted_bytes(_file.file_size)
            raise RuntimeError(f"File is too large: {_file.filename} ({fsf}).")
        
        zf.extract(_file, destination)