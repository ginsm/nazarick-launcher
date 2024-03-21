from modules.providers.CurseForgeProvider import CurseForgeMinecraftProvider
from modules.providers.ModrinthProvider import ModrinthMinecraftProvider
from modules.providers.SelfHostedProvider import SelfHostedMinecraftProvider
from modules.providers.ThunderstoreProvider import ThunderstoreValheimProvider
from modules.updaters.EnshroudedUpdater import EnshroudedUpdater
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
                'elevate_check': False
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
                'elevate_check': True
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
        'settings': [
            {
                'name': 'install',
                'type': 'directory',
                'label': 'Install Path',
                'placeholder': 'Enter the path to your Enshrouded install.',
                'elevate_check': True
            }
        ],
        'updater': EnshroudedUpdater,
    }
]