from modules.updater import minecraft_updater, valheim_updater


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
        'updater': minecraft_updater
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
        'updater': valheim_updater
    }
]