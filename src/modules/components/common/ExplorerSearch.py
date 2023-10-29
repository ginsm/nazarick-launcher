import os
import webbrowser
from PIL import Image
from tkinter import filedialog
from tktooltip import ToolTip
from modules import store
from modules.debounce import debounce
from modules.tufup_settings import BASE_DIR

def create(ctk, master, label, placeholder, name, find, game=''):
    frame = ctk.CTkFrame(master=master, fg_color='transparent')
    frame.grid_columnconfigure(0, weight=1)
    frame.grid_rowconfigure(0, weight=1)

    label = ctk.CTkLabel(master=frame, text=label)
    label.grid(row=1, column=0, padx=10, pady=(5, 0), sticky='w')

    entry = ctk.CTkEntry(master=frame, placeholder_text=placeholder, height=36)
    entry.grid(row=2, column=0, padx=(10, 5), pady=5, sticky='ew')
    entry.bind(sequence='<KeyRelease>', command=lambda _ : handle_key_press(entry, name))
    ToolTip(entry, msg=placeholder, delay=0.01, follow=True)

    # Button variables
    button_height = 36
    button_width = 44
    icon_size = 18

    # Images
    IMAGE_DIR = BASE_DIR / 'icons'
    search_image = ctk.CTkImage(Image.open(os.path.join(IMAGE_DIR, 'zoom.png')), size=(icon_size, icon_size))
    open_image = ctk.CTkImage(Image.open(os.path.join(IMAGE_DIR, 'folder.png')), size=(icon_size, icon_size))

    # Search Button
    search_function = get_search_function(find)
    search_button = ctk.CTkButton(master=frame, image=search_image, text='', command=lambda: search_function(entry, name), height=button_height, width=button_width)
    search_button.grid(row=2, column=1, padx=(0, 5), pady=5, sticky='ew')
    ToolTip(search_button, msg=f'Search for the {name} path.', delay=0.01, follow=True)

    # Open Button
    open_button = ctk.CTkButton(master=frame, image=open_image, text='', command=lambda: open_path(entry, name), height=button_height, width=button_width)
    open_button.grid(row=2, column=2, padx=(0, 10), pady=5, sticky='ew')
    ToolTip(open_button, msg=f'Open the {name} path.', delay=0.01, follow=True)


    # Get entry state from storage and set it
    state = store.get_game_state(game)
    if bool(state.get(name)):
        set_entry(entry, state[name])

    return [entry, search_button, frame]


# Helper Functions
@debounce(1)
def handle_key_press(entry, name):
    stored = store.get_game_state()[name]
    value = entry.get()
    
    if (stored != value):
        store.set_game_state({name: value})

def open_path(entry, name):
    path = entry.get()
    if (name == 'executable'):
        path = os.path.split(path)[0]

    if (os.path.isdir(path)):
        webbrowser.open(path)

def get_search_function(find):
    match find:
        case 'directory':
            return search_for_dir
        case 'file':
            return search_for_file
        case _:
            return search_for_file

def set_entry(entry, string):
    entry.delete(first_index=0, last_index='end')
    entry.insert(index=0, string=string)

def search_for_dir(entry, name):
    path = filedialog.askdirectory()
    if (path is not None and path != ''):
        set_entry(entry=entry, string=path)
        store.set_game_state({name: path})

def search_for_file(entry, name):
    path = filedialog.askopenfile()
    if (path is not None):
        set_entry(entry=entry, string=path.name)
        store.set_game_state({name: path.name})