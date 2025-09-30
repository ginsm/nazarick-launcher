import os, pathlib, sys, platform
from dotenv import load_dotenv

# App info
APP_VERSION = '1.4.15'
APP_NAME = 'Nazarick_Launcher'
APP_BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
LOGGER_NAME = 'Nazarick'
MAX_WORKER_AMOUNT = 4

# Networking
DOWNLOAD_TIMEOUTS = (20, 45) # connection timeout, read timeout
MAX_CONNECTIONS_PER_HOST = 4

# Zip protections
KiB = 1024
MiB = 1024 * KiB
GiB = 1024 * MiB

MAX_FILE_SIZE = 300 * MiB
MAX_TOTAL_UNCOMPRESSED = int(1.5 * GiB)
MAX_ENTRY_COUNT = 10000
MAX_COMPRESSION_RATIO = 200.0

# Platform
ON_MAC = platform.system() == "Darwin"
ON_WINDOWS = platform.system() == "Windows"

# Are we running in a Pyinstaller bundle?
# https://pyinstaller.org/en/stable/runtime-information.html
APP_BUNDLED = getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')

# DotEnv constants
load_dotenv(os.path.join(APP_BASE_DIR, '.env'))

SELFHOSTED_WEBSITE = os.getenv('SELFHOSTED_WEBSITE')
CURSEFORGE_API_KEY = os.getenv('CURSEFORGE_API_KEY')