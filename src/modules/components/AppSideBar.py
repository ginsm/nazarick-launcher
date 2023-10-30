import os
from PIL import Image
from modules.tufup_settings import BASE_DIR
from modules import view
from modules import store

game_buttons = []

def create(ctk, master, games):
    icon_size=54
    pad=10

    # Create frame
    frame = ctk.CTkFrame(master=master, width=icon_size + (pad * 2), fg_color=('#1d1e1e', '#1d1e1e'), height=icon_size + pad)

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
        button.grid(column=0, row=len(game_buttons), sticky='n', ipady=pad, ipadx=pad * 2)

        # Add button to global game_buttons
        game_buttons.append({'name': game['name'], 'button': button})

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
        text=game,
        compound='top',
        command=lambda: select_game(game, frame),
        height=size,
        width=size,
        corner_radius=0
    )


def color_buttons(selected_game):
    global game_buttons
    
    normal=('#1d1e1e', '#1d1e1e')
    normal_text=("#ffffff", "#ffffff")
    selected=('#dbdbdb', '#2b2b2b')
    selected_text=("#1a1a1a", "#ffffff")

    for game_button in game_buttons:
        button = game_button['button']
        
        if game_button['name'] == selected_game:
            button.configure(fg_color=selected)
            button.configure(text_color=selected_text)
        else:
            button.configure(fg_color=normal)
            button.configure(text_color=normal_text)


def select_game(game, frame):
    # Raise the frame in the app
    frame.tkraise()

    # Set the game in store
    store.set_game(game.lower())

    # Color the game button differently
    color_buttons(game)