import os
from PIL import Image
from tktooltip import ToolTip
from modules.tufup_settings import BASE_DIR
from modules import view
from modules import store

game_buttons = []

def create(ctk, master, games):
    icon_size=54
    pad=14

    # Create frame
    frame = ctk.CTkFrame(master=master, width=icon_size + pad, fg_color=('#1d1e1e', '#1d1e1e'), height=icon_size + pad)

    # Create buttons
    for game in games:
        global game_buttons

        # Create button
        button = GameButton(
            ctk=ctk,
            master=master,
            game=game['name'],
            frame=game['frame'],
            size=icon_size
        )
        button.grid(column=0, row=len(game_buttons), sticky='n', ipady=pad, ipadx=pad)
        ToolTip(button, msg=game['name'], delay=0.01, follow=True)

        # Add button to global game_buttons
        game_buttons.append({'name': game['name'], 'button': button})

        # Add button to lockable
        view.add_lockable(button)

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
        width=size,
        corner_radius=0
    )


def color_buttons(selected_game):
    global game_buttons
    
    normal='#1d1e1e'
    dark_selected='#2b2b2b'
    light_selected='#dbdbdb'

    for game_button in game_buttons:
        if game_button['name'] == selected_game:
            game_button['button'].configure(fg_color=(light_selected, dark_selected))
        else:
            game_button['button'].configure(fg_color=(normal, normal))


def select_game(game, frame):
    # Raise the frame in the app
    frame.tkraise()

    # Set the game in store
    store.set_game(game.lower())

    # Color the game button differently
    color_buttons(game)