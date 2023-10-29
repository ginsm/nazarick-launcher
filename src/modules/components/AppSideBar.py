import os
from PIL import Image
from tktooltip import ToolTip
from modules.tufup_settings import BASE_DIR
from modules import view
from modules import store


def create(ctk, master, games):
    icon_size=44

    # Create frame
    frame = ctk.CTkFrame(master=master, width=80, fg_color='transparent', height=icon_size)
    frame.grid_rowconfigure((0, 1), weight=1)

    # Store buttons in array
    gameButtons = []

    # Create buttons
    for game in games:
        button = GameButton(
            ctk=ctk,
            master=master,
            game=game['name'],
            frame=game['frame'],
            size=icon_size
        )
        button.grid(column=0, row=len(gameButtons), sticky='n', pady=(15,0))
        ToolTip(button, msg=game['name'], delay=0.01, follow=True)
        gameButtons.append(button)

    # Add buttons to lockables
    view.add_lockable(gameButtons)

    return frame


def GameButton(ctk, master, game, frame, size):
    # Image directory
    IMAGE_DIR = BASE_DIR / 'icons'

    # Create game image
    game_image = ctk.CTkImage(
        Image.open(os.path.join(IMAGE_DIR, f'{game}.png')),
        size=(size, size)
    )

    # Create button and return it
    return ctk.CTkButton(
        master=master,
        image=game_image,
        text='',
        command=lambda: select_game(game, frame),
        height=size,
        width=size
    )

def select_game(game, frame):
    frame.tkraise()
    store.set_game(game.lower())