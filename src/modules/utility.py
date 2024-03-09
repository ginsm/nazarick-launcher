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


def some(list_, func):
    for element in list_:
        if (func(element)):
            return True
    return False


def get_time():
    return datetime.now().strftime('%m/%d/%Y %H:%M:%S')