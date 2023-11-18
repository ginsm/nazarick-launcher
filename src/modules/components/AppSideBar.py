import os
from PIL import Image
from customtkinter.windows.widgets.theme import ThemeManager
from modules.tufup import BASE_DIR
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
            games=games,
            frame=game['frame'],
            size=icon_size
        )
        button.grid(column=0, row=len(game_buttons), sticky='n', ipady=pad, ipadx=pad * 2)

        # Add button to global game_buttons
        game_buttons.append({'name': game['name'], 'button': button})

    return frame


def GameButton(ctk, master, game, games, frame, size):
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
        command=lambda: select_game(game, games, frame),
        height=size,
        width=size,
        corner_radius=0,
        border_width=0
    )

def clear_game_Buttons():
    global game_buttons
    game_buttons = []

def color_buttons(selected_game):
    global game_buttons

    normal=ThemeManager.theme.get('CTk').get('fg_color')
    text=ThemeManager.theme.get('Sidebar').get('text_color')
    selected=ThemeManager.theme.get('CTkFrame').get('fg_color')

    for game_button in game_buttons:
        button = game_button['button']
        button.configure(hover_color=selected)
        button.configure(text_color=text)
        
        if game_button['name'] == selected_game:
            button.configure(fg_color=selected)
        else:
            button.configure(fg_color=normal)


def select_game(game, games, frame):
    # Raise the frame in the app
    frame.grid(row=0, column=1, rowspan=len(games), sticky='nsew')

    for g in games:
        if g['name'] != game:
            g['frame'].grid_forget()

    # Set the game in store
    store.set_game(game.lower())

    # Color the game button differently
    color_buttons(game)