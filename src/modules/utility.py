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


def path_is_relative(base, path):
    # Get the absolute paths
    base_path = os.path.abspath(base)
    abs_path = os.path.abspath(path)

    # Determine if the path is within the base path
    base_len = len(base_path)
    if abs_path[0:base_len] != base_path:
        return False
    return True

