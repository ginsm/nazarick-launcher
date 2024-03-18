from datetime import datetime
from modules import game_list


def get_time():
    return datetime.now().strftime('%m/%d/%Y %H:%M:%S')


def get_modpack_data(game, modpack):
    for game_dict in game_list.LIST:
        if game_dict.get('name').lower() == game.lower() and game_dict.get('modpacks'):
            for pack in game_dict.get('modpacks'):
                if pack.get('name').lower() == modpack.lower():
                    return pack
    return {}