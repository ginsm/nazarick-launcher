from modules.providers.ModProviders import ModrinthModProvider, ThunderstoreModProvider
from modules.providers.ModpackProviders import CurseForgeModpackProvider, SelfHostedMinecraftModpackProvider, ThunderstoreModpackProvider
from modules.updater import minecraft_updater, valheim_updater, enshrouded_updater


LIST = [
    {
        'name': 'Minecraft',
        'settings': [
            {
                'name': 'instance',
                'type': 'directory',
                'label': 'Instance Path',
                'placeholder': 'Enter the path to your Minecraft instance.',
            },
            {
                'name': 'executable',
                'type': 'file',
                'label': "Launcher's Executable Path",
                'placeholder': "Enter the path to your launcher's executable."
            }
        ],
        'modpacks': [
            {
                'name': 'nazarick-smp',
                'providers': {
                    'modpack': SelfHostedMinecraftModpackProvider,
                    'mods': ModrinthModProvider
                },
                'slug': '',
                'url': ''
            },
            {
                'name': 'Vault Hunters',
                'provider': CurseForgeModpackProvider,
                'slug': '',
                'url': ''
            },
        ],
        'updater': minecraft_updater,
    },
    {
        'name': 'Valheim',
        'settings': [
            {
                'name': 'install',
                'type': 'directory',
                'label': 'Install Path',
                'placeholder': 'Enter the path to your Valheim install.',
            },
        ],
        'modpacks': [
            {
                'name': 'nazarick-smp',
                'providers': {
                    'modpack': ThunderstoreModpackProvider,
                    'mods': ThunderstoreModProvider
                },
                'slug': '',
                'url': ''
            },
        ],
        'updater': valheim_updater,
    },
    {
        'name': 'Enshrouded',
        'settings': [
            {
                'name': 'install',
                'type': 'directory',
                'label': 'Install Path',
                'placeholder': 'Enter the path to your Enshrouded install.',
            }
        ],
        'updater': enshrouded_updater,
    }
]

def get_modpack(game, modpack):
    for game_dict in LIST:
        if game_dict.get('name').lower() == game.lower():
            for pack in game_dict.get('modpacks'):
                if pack.get('name').lower() == modpack.lower():
                    return pack
    return None