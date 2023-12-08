import os
from modules import constants

def get_themes():
    return [
        {'name': custom_theme('blue'), 'title': 'Blue'},
        {'name': custom_theme('green'), 'title': 'Green'},
        {'name': custom_theme('red'), 'title': 'Red'},
        {'name': custom_theme('DaynNight'), 'title': 'DaynNight'},
        {'name': custom_theme('GhostTrain'), 'title': 'GhostTrain'},
        {'name': custom_theme('Greengage'), 'title': 'Greengage'},
        {'name': custom_theme('GreyGhost'), 'title': 'GreyGhost'},
        {'name': custom_theme('Harlequin'), 'title': 'Harlequin'},
        {'name': custom_theme('MoonlitSky'), 'title': 'MoonlitSky'},
        {'name': custom_theme('NightTrain'), 'title': 'NightTrain'},
        {'name': custom_theme('Oceanix'), 'title': 'Oceanix'},
        {'name': custom_theme('Sweetkind'), 'title': 'Sweetkind'},
        {'name': custom_theme('TrjBlue'), 'title': 'TrjBlue'},
    ]


def custom_theme(name):
    return os.path.join(constants.APP_BASE_DIR, 'assets', 'themes', f'{name}.json')


def get_theme_from_title(title):
    themes = get_themes()
    for theme in themes:
        if theme['title'] == title:
            return theme
    return themes[0]