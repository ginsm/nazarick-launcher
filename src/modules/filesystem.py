import os
import shutil


def move_files(source, target, overwrite=True):
    # Iterate over directory's files
    for file_ in os.listdir(source):
        file_path = os.path.join(source, file_)

        # Iterate through directories if overwrite is false
        if not overwrite and os.path.isdir(file_path):
            for root, _, files in os.walk(file_path):
                for name in files:
                    root_path = os.path.join(root, name)

                    # Get target path
                    path_without_source = root_path.replace(source, '')[1:]
                    target_path = os.path.join(target, path_without_source)

                    # Ensure target root exists
                    target_root, _ = os.path.split(target_path)
                    os.makedirs(target_root, exist_ok=True)

                    # Move file if path doesn't exist or overwrite enabled
                    if not os.path.exists(target_path):
                        shutil.move(root_path, target_path)

        # Attempt to move top-level files (if they don't already exist)
        else:
            target_path = os.path.join(target, file_)
            os.makedirs(os.path.split(target_path)[0], exist_ok=True)

            if overwrite and os.path.isdir(target_path):
                shutil.rmtree(target_path)

            if overwrite or not os.path.exists(target_path):
                shutil.move(file_path, target_path)


def delete_path(base_path, path, whitelist, log):
    if can_delete_path(base_path, path, whitelist):
        rm_func = shutil.rmtree if os.path.isdir(path) else os.remove
        rm_func(path)
        log(f'[INFO] (R) {path.replace(base_path, "")[1:]}')


def overwrite(source, target):
    target_root, _ = os.path.split(target)
    rm_func = shutil.rmtree if os.path.isdir(target) else os.remove

    if os.path.exists(target):
        rm_func(target)

    if not os.path.exists(target_root):
        os.makedirs(target_root)

    shutil.move(source, target)


# ---- HELPER FUNCTIONS ---- #
def path_is_relative(base, path):
    # Get the absolute paths
    base_path = os.path.abspath(base)
    abs_path = os.path.abspath(path)

    # Determine if the path is within the base path
    base_len = len(base_path)
    if abs_path[0:base_len] != base_path:
        return False
    return True


def can_delete_path(base_path, path, whitelist = []):
    """
        Ensures that the given path is within a whitelisted directory inside the instance path and that the path exists.\n\n
    """
    # Variables
    path_abs = os.path.abspath(path)
    result = False
                
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
        if path_is_relative(base_whitelist_path, path_abs) and base_whitelist_path != path_abs:
            result = True

    # 
    if len(whitelist) == 0:
        result = True

    return result