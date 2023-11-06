import os
from datetime import datetime


def set_env(name, value):
    os.environ[name] = value


def get_env(name):
    return os.environ.get(name)


def destructure(obj={}, args=[]):
    output = []

    if len(args):
        for arg in args:
            value = obj.get(arg) if isinstance(obj, dict) else obj[arg]
            output.append(value)

    return output

def get_time():
    return datetime.now().strftime('%m/%d/%Y %H:%M:%S')


def path_is_relative(path, base):
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
    abs_path = os.path.abspath(path)
    result = False
        
    # Determine if the path is within the base path
    if not path_is_relative(abs_path, base_path):
        return False

    # Ensure the path exists
    if not os.path.exists(abs_path):
        return False

    # Ensure the file to delete is within a whitelisted directory
    # while ensuring the target isn't the directory itself.
    for dir_ in whitelist:
        full_path = os.path.join(base_path, dir_)
        if path_is_relative(abs_path, full_path) and abs_path != full_path:
            result = True

    # 
    if len(whitelist) == 0:
        result = True

    return result