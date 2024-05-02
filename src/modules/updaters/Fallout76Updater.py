from modules import state_manager
from modules.updaters.AbstractGameUpdater import AbstractGameUpdater


class Fallout76Updater(AbstractGameUpdater):
    def initialize(self):
        # Get game state
        game_state = state_manager.get_pack_state('Fallout76')

        # Begin initializing variables
        self.game = 'Fallout76'


    def install_update(self):
        pass