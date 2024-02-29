from modules.providers.CurseForgeProvider import CurseForgeMinecraftProvider
from modules.providers.ModrinthProvider import ModrinthMinecraftProvider
from modules.providers.SelfHostedProvider import SelfHostedMinecraftProvider
from modules.providers.ThunderstoreProvider import ThunderstoreValheimProvider
from modules.updater import minecraft_updater, valheim_updater, enshrouded_updater


LIST = [
    # Minecraft
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
                    'modpack': SelfHostedMinecraftProvider,
                    'mods': ModrinthMinecraftProvider
                },
                'type': 'modrinth',
                'project': 'nazarick-smp',
                'file': 'latest'
            },
            {
                'name': 'Vault Hunters',
                'providers': {
                    'modpack': CurseForgeMinecraftProvider,
                    'mods': CurseForgeMinecraftProvider,
                },
                'type': 'curseforge',
                'project': '711537',
                'file': '5076205'
            },
        ],
        'updater': minecraft_updater,
    },

    # Valheim
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
                    'modpack': ThunderstoreValheimProvider,
                    'mods': ThunderstoreValheimProvider
                },
                'type': 'thunderstore',
                'project': 'Syh/Nazarick_Core',
                'file': 'latest'
            },
        ],
        'updater': valheim_updater,
    },

    # Enshrouded
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

def get_modpack_data(game, modpack):
    for game_dict in LIST:
        if game_dict.get('name').lower() == game.lower() and game_dict.get('modpacks'):
            for pack in game_dict.get('modpacks'):
                if pack.get('name').lower() == modpack.lower():
                    return pack
    return None