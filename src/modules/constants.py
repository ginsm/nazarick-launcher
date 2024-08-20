import os, pathlib, sys
from dotenv import load_dotenv
import platform

# App info
APP_VERSION = '1.4.13'
APP_NAME = 'Nazarick_Launcher'
APP_BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
LOGGER_NAME = 'Nazarick'

# Platform
ON_MAC = platform.system() == "Darwin"
ON_WINDOWS = platform.system() == "Windows"

# Are we running in a Pyinstaller bundle?
# https://pyinstaller.org/en/stable/runtime-information.html
APP_BUNDLED = getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')

# DotEnv constants
load_dotenv(os.path.join(APP_BASE_DIR, '.env'))

SELFHOSTED_WEBSITE=os.getenv('SELFHOSTED_WEBSITE')
CURSEFORGE_API_KEY=os.getenv('CURSEFORGE_API_KEY')