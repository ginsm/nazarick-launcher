import os
from modules.tufup import BASE_DIR

def get_themes():
    return [
        {'name': 'blue', 'title': 'Blue', 'hex': '#1f6aa5'},
        {'name': 'dark-blue', 'title': 'Dark Blue', 'hex': '#1f538d'},
        {'name': 'green', 'title': 'Green', 'hex': '#2fa572'},
        {'name': custom_theme('Anthracite'), 'title': 'Anthracite', 'hex': ("#748498", "#748498")},
        {'name': custom_theme('DaynNight'), 'title': 'DaynNight', 'hex': ("#a9b8c4", "#748498")},
        {'name': custom_theme('GhostTrain'), 'title': 'GhostTrain', 'hex': ("#a3b2be", "#2e435c")},
        {'name': custom_theme('Greengage'), 'title': 'Greengage', 'hex': ("#a9b8c4", "#a9b8c4")},
        {'name': custom_theme('GreyGhost'), 'title': 'GreyGhost', 'hex': ("#9dacb8", "#97a6b2")},
        {'name': custom_theme('Hades'), 'title': 'Hades', 'hex': ("#d67915", "#d67915")},
        {'name': custom_theme('Harlequin'), 'title': 'Harlequin', 'hex': ("#a9b8c4", "#a9b8c4")},
        {'name': custom_theme('MoonlitSky'), 'title': 'MoonlitSky', 'hex': ("#7083b4", "#4b5791")},
        {'name': custom_theme('NeonBanana'), 'title': 'NeonBanana', 'hex': ("#283e7b", "#233773")},
        {'name': custom_theme('NightTrain'), 'title': 'NightTrain', 'hex': ("#02244c", "#1b1e48")},
        {'name': custom_theme('Oceanix'), 'title': 'Oceanix', 'hex': ("#375774", "#173145")},
        {'name': custom_theme('Sweetkind'), 'title': 'Sweetkind', 'hex': ("gray20", "gray20")},
        {'name': custom_theme('TestCard'), 'title': 'TestCard', 'hex': ("#b6ffff", "#b6ffff")},
        {'name': custom_theme('TrojanBlue'), 'title': 'TrojanBlue', 'hex': ("#283e7b", "#233773")},
    ]

def custom_theme(name):
    return os.path.join(BASE_DIR, 'themes', f'{name}.json')