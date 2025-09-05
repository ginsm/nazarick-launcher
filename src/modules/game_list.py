from modules.providers.CurseForgeProvider import CurseForgeMinecraftProvider
from modules.providers.ModrinthProvider import ModrinthMinecraftProvider
from modules.providers.SelfHostedProvider import SelfHostedFallout76Provider, SelfHostedMinecraftProvider
from modules.providers.ThunderstoreProvider import ThunderstoreValheimProvider
from modules.updaters.EnshroudedUpdater import EnshroudedUpdater
from modules.updaters.Fallout76Updater import Fallout76Updater
from modules.updaters.MinecraftUpdater import MinecraftUpdater
from modules.updaters.ValheimUpdater import ValheimUpdater


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
                'elevate_check': True
            },
            {
                'name': 'executable',
                'type': 'file',
                'label': "Launcher's Executable Path",
                'placeholder': "Enter the path to your launcher's executable.",
                'elevate_check': False,
                'storeapp': {
                    'search': 'Minecraft Launcher',
                    'ID': 'Microsoft.4297127D64EC6_8wekyb3d8bbwe',
                    'exe': 'Minecraft.exe'
                }
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
                'file': 'latest',
                'game_version': '1.20.1'
            },
            {
                'name': 'Vault Hunters',
                'providers': {
                    'modpack': SelfHostedMinecraftProvider,
                    'mods': CurseForgeMinecraftProvider,
                },
                'type': 'curseforge',
                'project': 'Vault Hunters',
                'file': 'latest',
                'game_version': '1.18.2'
            },
            {
                'name': 'nazarick-smp',
                'providers': {
                    'modpack': SelfHostedMinecraftProvider,
                    'mods': ModrinthMinecraftProvider
                },
                'type': 'modrinth',
                'project': 'mccp',
                'file': 'latest',
                'game_version': '1.21.8'
            },
        ],
        'updater': MinecraftUpdater,
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
                'elevate_check': True,
                'steam': {
                    'ID': '892970'
                }
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
        'updater': ValheimUpdater,
    },

    # Enshrouded
    {
        'name': 'Enshrouded',
        'settings': [],
        'updater': EnshroudedUpdater,
    },

    # Fallout 76
    {
        'name': 'Fallout76',
        'settings': [
            {
                'name': 'install',
                'type': 'directory',
                'label': 'Install Path',
                'placeholder': 'Enter the path to your Fallout 76 install.',
                'elevate_check': True,
                'steam': {
                    'ID': '1151340'
                },
                'storeapp': {
                    'search': 'Fallout 76',
                    'ID': 'BethesdaSoftworks.Fallout76-PC_3275kfvn8vcwc',
                    'exe': 'Fallout76.exe'
                },
            },
            {
                'name': 'documents',
                'type': 'directory',
                'label': 'Documents Path',
                'placeholder': 'Enter the path to your Documents folder.',
                'elevate_check': True,
                'win_folder': {
                    'ID': 'Documents'   
                }
            },
            {
                'name': 'platform',
                'type': 'dropdown',
                'label': 'Game Platform',
                'choices': ['Steam', 'Microsoft Store']
            }
        ],
        'modpacks': [
            {
                'name': 'Quality',
                'providers': {
                    'modpack': SelfHostedFallout76Provider,
                    'mods': SelfHostedFallout76Provider
                },
                'project': 'Quality'
            },
            {
                'name': 'Performance',
                'providers': {
                    'modpack': SelfHostedFallout76Provider,
                    'mods': SelfHostedFallout76Provider
                },
                'project': 'Performance'
            }
        ],
        'updater': Fallout76Updater
    },
]