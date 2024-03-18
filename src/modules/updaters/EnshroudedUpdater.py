import logging
from typing import override
from modules import constants, utility
from modules.updaters.AbstractGameUpdater import AbstractGameUpdater

# Enshrouded doesn't have mod support yet; this updater simply launches the game.
class EnshroudedUpdater(AbstractGameUpdater):
    def initialize(self):
        self.exe_name = 'enshrouded.exe'
        self.command = ['cmd', '/c', 'start', 'steam://run/1203620']
        self.logger = logging.getLogger(f'{constants.LOGGER_NAME}.enshrouded.')
        self.cancel = False

    @override
    def start(self, update_button):
        self.initialize()

        self.logger.info('')
        self.logger.info(f'Beginning process at {utility.get_time()}.')
        self.logger.info(f'This game doesn\'t require updates as it\'s vanilla only currently.')

        self.run_executable()

        self.logger.info(f'Finished process at {utility.get_time()}.')

        update_button.configure(text='Play')
        self.cancel = False

    def install_update(self):
        raise NotImplementedError