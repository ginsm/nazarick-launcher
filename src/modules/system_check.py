import os, urllib


# Used for checking permissions
NEED_ADMIN = 'need-admin'
HAVE_PERM = 'have-perm'
UNKNOWN = 'unknown'

def elevation_needed(game_paths):
    return any(check_access(v) == NEED_ADMIN for v in game_paths)

def check_access(path):
    if (os.path.exists(path)):
        test_file = os.path.join(path, 'NazarickAccessTest')
        try:
            open(test_file, 'x')
            os.remove(test_file)
            return HAVE_PERM
        except:
            return NEED_ADMIN
    return UNKNOWN


# Used for checking internet connectivity
def check_internet():
    try:
        response = urllib.request.urlopen('https://www.google.com', timeout=6)
        return True
    except:
        return False