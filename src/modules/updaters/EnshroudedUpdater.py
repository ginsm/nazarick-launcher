from typing import override
from modules import utility
from modules.updaters.AbstractGameUpdater import AbstractGameUpdater

# Enshrouded doesn't have mod support yet; this updater simply launches the game.
class EnshroudedUpdater(AbstractGameUpdater):
    def initialize(self):
        self.exe_name = 'enshrouded.exe'
        self.command = ['cmd', '/c', 'start', 'steam://run/1203620']

    @override
    def start(self):
        self.initialize()

        self.log('')
        self.log(f'[INFO] Beginning process at {utility.get_time()}.')
        self.log(f'[INFO] This game doesn\'t require updates as it\'s vanilla only currently.')

        self.run_executable()

        self.log(f'[INFO] Finished process at {utility.get_time()}.')

    def install_update(self):
        raise NotImplementedError