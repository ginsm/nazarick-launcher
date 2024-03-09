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


def path_is_relative(base, path):
    # Get the absolute paths
    base_path = os.path.abspath(base)
    abs_path = os.path.abspath(path)

    # Determine if the path is within the base path
    base_len = len(base_path)
    if abs_path[0:base_len] != base_path:
        return False
    return True