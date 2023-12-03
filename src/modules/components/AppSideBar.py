import os
from PIL import Image
from customtkinter.windows.widgets.theme import ThemeManager
from modules.tufup import BASE_DIR
from modules import store

frame_buttons = []

def create(ctk, parent, frames):
    icon_size=54
    pad=10

    # Create frame
    sidebar = ctk.CTkFrame(master=parent, width=icon_size + (pad * 2), fg_color=('#1d1e1e', '#1d1e1e'), height=icon_size + pad)

    # Create buttons
    for frame in frames:
        global frame_buttons

        # Create button
        button = FrameButton(
            ctk=ctk,
            master=parent,
            name=frame['name'],
            frames=frames,
            frame=frame['frame'],
            size=icon_size
        )
        button.grid(column=0, row=len(frame_buttons), sticky='n', ipady=pad, ipadx=pad * 2)

        # Add button to global frame_buttons
        frame_buttons.append({'name': frame['name'], 'button': button})

    return sidebar


def FrameButton(ctk, master, name, frames, frame, size):
    # Image directory
    IMAGE_DIR = BASE_DIR / 'assets' / 'icons'

    # Create frame image
    frame_image = ctk.CTkImage(
        Image.open(os.path.join(IMAGE_DIR, f'{name}.png')),
        size=(size, size)
    )

    # Create button and return it
    return ctk.CTkButton(
        master=master,
        image=frame_image,
        text=name,
        compound='top',
        command=lambda: select_frame(name, frames, frame),
        height=size,
        width=size,
        corner_radius=0,
        border_width=0
    )

def clear_frame_Buttons():
    global frame_buttons
    frame_buttons = []

def color_buttons(selected_frame):
    global frame_buttons

    normal=ThemeManager.theme.get('CTk').get('fg_color')
    text=ThemeManager.theme.get('Sidebar').get('text_color')
    selected=ThemeManager.theme.get('CTkFrame').get('fg_color')

    for frame_button in frame_buttons:
        button = frame_button['button']
        button.configure(hover_color=selected)
        button.configure(text_color=text)
        
        if frame_button['name'] == selected_frame:
            button.configure(fg_color=selected)
        else:
            button.configure(fg_color=normal)


def select_frame(frame_name, frames, frame):
    # Raise the frame in the app
    frame.grid(row=0, column=1, rowspan=len(frames), sticky='nsew')

    for f in frames:
        if f['name'] != frame_name:
            f['frame'].grid_forget()

    # Set the frame in store
    store.set_frame(frame_name.lower())

    # Color the frame button differently
    color_buttons(frame_name)