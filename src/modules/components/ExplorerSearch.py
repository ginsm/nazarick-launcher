import os
import webbrowser
from modules import store
from modules.debounce import debounce
from tkinter import filedialog
from modules.tufupsettings import BASE_DIR
from PIL import Image
from tktooltip import ToolTip

def create(ctk, master, label, placeholder, name, find):
    frame = ctk.CTkFrame(master=master, fg_color="transparent")
    frame.grid_columnconfigure(0, weight=1)
    frame.grid_rowconfigure(0, weight=1)

    label = ctk.CTkLabel(master=frame, text=label)
    label.grid(row=1, column=0, padx=10, pady=(5, 0), sticky="w")

    entry = ctk.CTkEntry(master=frame, placeholder_text=placeholder, height=36)
    entry.grid(row=2, column=0, padx=(10, 5), pady=5, sticky="ew")
    entry.bind(sequence="<KeyRelease>", command=lambda _ : handleKeyPress(entry, name))
    ToolTip(entry, msg=placeholder, delay=0.01, follow=True)

    # Button variables & images
    button_height = 36
    button_width = 44
    icon_size = 18
    IMAGE_DIR = BASE_DIR / 'icons'
    searchImage = ctk.CTkImage(Image.open(os.path.join(IMAGE_DIR, 'zoom.png')), size=(icon_size, icon_size))
    openImage = ctk.CTkImage(Image.open(os.path.join(IMAGE_DIR, 'folder.png')), size=(icon_size, icon_size))

    # Search Button
    searchFunction = getSearchFunction(find)
    searchButton = ctk.CTkButton(master=frame, image=searchImage, text="", command=lambda: searchFunction(entry, name), height=button_height, width=button_width)
    searchButton.grid(row=2, column=1, padx=(0, 5), pady=5, sticky="ew")
    ToolTip(searchButton, msg=f"Search for the {name} path.", delay=0.01, follow=True)

    # Open Button
    openButton = ctk.CTkButton(master=frame, image=openImage, text="", command=lambda: openPath(entry, name), height=button_height, width=button_width)
    openButton.grid(row=2, column=2, padx=(0, 10), pady=5, sticky="ew")
    ToolTip(openButton, msg=f"Open the {name} path.", delay=0.01, follow=True)


    # Get entry state from storage and set it
    state = store.getGameState()
    if bool(state[name]):
        setEntry(entry, state[name])

    return [entry, searchButton, frame]


# Helper Functions
@debounce(1)
def handleKeyPress(entry, name):
    stored = store.getGameState()[name]
    value = entry.get()
    
    if (stored != value):
        store.setGameState({name: value})

def openPath(entry, name):
    path = entry.get()
    if (name == 'executable'):
        path = os.path.split(path)[0]

    if (os.path.isdir(path)):
        webbrowser.open(path)

def getSearchFunction(find):
    match find:
        case 'directory':
            return searchForDir
        case 'file':
            return searchForFile
        case _:
            return searchForFile

def setEntry(entry, string):
    entry.delete(first_index=0, last_index="end")
    entry.insert(index=0, string=string)

def searchForDir(entry, name):
    path = filedialog.askdirectory()
    if (path is not None and path != ""):
        setEntry(entry=entry, string=path)
        store.setGameState({name: path})

def searchForFile(entry, name):
    path = filedialog.askopenfile()
    if (path is not None):
        setEntry(entry=entry, string=path.name)
        store.setGameState({name: path.name})