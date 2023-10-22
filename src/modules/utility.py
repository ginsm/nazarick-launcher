import os
from datetime import datetime

def absdir(file):
    return os.path.dirname(os.path.realpath(file))

def setenv(name, value):
    os.environ[name] = value

def getenv(name):
    return os.environ.get(name)

def destructure(obj={}, args=[]):
    output = []

    if len(args):
        for arg in args:
            value = obj.get(arg) if isinstance(obj, dict) else obj[arg]
            output.append(value)

    return output

def getTime():
    return datetime.now().strftime("%m/%d/%Y %H:%M:%S")