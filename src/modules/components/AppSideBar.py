import os
from PIL import Image
from customtkinter.windows.widgets.theme import ThemeManager
from modules import constants
from modules import state_manager

frame_buttons = []

def create(ctk, parent, frames):
    icon_size=54
    pad=10

    # Create frame
    sidebar = ctk.CTkFrame(master=parent, width=icon_size + (pad * 2), fg_color=('#1d1e1e', '#1d1e1e'), border_width=-1)

    # Create buttons
    for frame in frames:
        global frame_buttons

        # Create button
        button = FrameButton(
            ctk=ctk,
            master=sidebar,
            name=frame['name'],
            frames=frames,
            frame=frame['frame'],
            size=icon_size
        )

        if frame['name'] == 'Settings':
            button.grid(column=0, row=len(frame_buttons) + 1, sticky='ew', ipady=pad, ipadx=pad * 2)
        else:
            button.grid(column=0, row=len(frame_buttons), sticky='ew', ipady=pad, ipadx=pad * 2)

        # Add button to global frame_buttons
        frame_buttons.append({'name': frame['name'], 'button': button})

    # Add a spacer between the last two buttons and occupy as much space as possible to push the
    # settings button down to the bottom of the column.
    spacer = ctk.CTkFrame(
        master=sidebar,
        width=icon_size,
        border_width=-1,
        corner_radius=0,
        fg_color=ThemeManager.theme.get('CTk').get('fg_color')
    )

    # Position the spacer/configure its row
    spacer.grid(column=0, row=len(frame_buttons) - 1, sticky='nsew')
    sidebar.grid_rowconfigure(len(frame_buttons) - 1, weight=1)

    return sidebar


def FrameButton(ctk, master, name, frames, frame, size):
    # Image directory
    IMAGE_DIR = constants.APP_BASE_DIR / 'assets' / 'icons'

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
        border_width=-1
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
        if f['name'] != frame_name and f['name'] != 'Sidebar':
            f['frame'].grid_forget()

    # Set the frame in store
    state_manager.set_frame(frame_name.lower())

    # Color the frame button differently
    color_buttons(frame_name)