import os, webbrowser
from PIL import Image
from tkinter import filedialog
from tktooltip import ToolTip
from customtkinter.windows.widgets.theme import ThemeManager
from elevate import elevate
from modules import store, system_check, constants
from modules.debounce import debounce
from modules.components.common import InfoModal

def create(ctk, master, app, label, placeholder, name, find, game=''):
    frame = ctk.CTkFrame(master=master, fg_color='transparent', border_width=0)
    frame.grid_columnconfigure(0, weight=1)
    frame.grid_rowconfigure(0, weight=1)

    label = ctk.CTkLabel(master=frame, text=label)
    label.grid(row=1, column=0, pady=2, sticky='w')

    entry = ctk.CTkEntry(master=frame, placeholder_text=placeholder, height=36, border_width=0)
    entry.grid(row=2, column=0, padx=(0, 5), pady=(0, 5), sticky='ew')
    entry.bind(sequence='<KeyRelease>', command=lambda _ : handle_key_press(ctk, entry, name, app))
    ToolTip(entry, msg=placeholder, delay=0.01, follow=True)

    # Button variables
    button_height = 36
    button_width = 44
    icon_size = 18

    # Images
    IMAGE_DIR = constants.APP_BASE_DIR / 'assets' / 'icons'
    search_image = ctk.CTkImage(Image.open(os.path.join(IMAGE_DIR, 'zoom.png')), size=(icon_size, icon_size))
    open_image = ctk.CTkImage(Image.open(os.path.join(IMAGE_DIR, 'folder.png')), size=(icon_size, icon_size))

    # Search Button
    search_function = get_search_function(find)
    search_button = ctk.CTkButton(master=frame, image=search_image, text='', command=lambda: search_function(entry, name, ctk, app), height=button_height, width=button_width, border_width=0)
    search_button.grid(row=2, column=1, padx=(0, 5), pady=(0, 5), sticky='ew')
    ToolTip(search_button, msg=f'Search for the {name} path.', delay=0.01, follow=True)

    # Open Button
    open_button = ctk.CTkButton(master=frame, image=open_image, text='', command=lambda: open_path(entry, name), height=button_height, width=button_width, border_width=0)
    open_button.grid(row=2, column=2, pady=(0, 5), sticky='ew')
    ToolTip(open_button, msg=f'Open the {name} path.', delay=0.01, follow=True)

    # Get entry state from storage and set it
    state = store.get_pack_state(game)
    if bool(state.get(name)):
        set_entry(entry, state[name])

    return [entry, search_button, frame]


# Helper Functions
@debounce(1)
def handle_key_press(ctk, entry, name, app):
    stored = store.get_pack_state()[name]
    value = entry.get()
    
    if (stored != value):
        store.set_pack_state({name: value})
        if system_check.check_perms(value) == system_check.NEED_ADMIN:
            warn_admin_required(ctk, value, app)


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


def search_for_dir(entry, name, ctk, app):
    path = filedialog.askdirectory()
    if (path is not None and path != ''):
        set_entry(entry=entry, string=path)
        store.set_pack_state({name: path})
        if system_check.check_perms(path) == system_check.NEED_ADMIN:
            warn_admin_required(ctk, path, app)


def search_for_file(entry, name, ctk, app):
    path = filedialog.askopenfile()
    if (path is not None):
        set_entry(entry=entry, string=path.name)
        store.set_pack_state({name: path.name})
        if system_check.check_perms(path) == system_check.NEED_ADMIN:
            warn_admin_required(ctk, path, app)


def warn_admin_required(ctk, path, app):
    def handle_restart(_):
        app.destroy()
        elevate(show_console=False)

    def destroy_modal(modal):
        modal.destroy()

    border_color = ThemeManager.theme.get('CTkCheckBox').get('border_color')
    
    InfoModal.create(
        ctk,
        text=f'The following path requires administrative privileges:\n\n"{path}"\n\nDo you want to elevate the launcher?',
        buttons=[
            {'text': 'Cancel', 'command': destroy_modal},
            {'text': 'Elevate', 'command': handle_restart, 'border': border_color},
        ],
        title='Admin Required',
    )