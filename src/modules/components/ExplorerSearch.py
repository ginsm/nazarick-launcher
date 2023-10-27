from modules import store
from modules.debounce import debounce
from tkinter import filedialog

@debounce(1)
def handleKeyPress(entry, name):
    stored = store.getGameState()[name]
    value = entry.get()
    
    if (stored != value):
        store.setGameState({name: value})

def create(ctk, master, label, placeholder, name, find):
    frame = ctk.CTkFrame(master=master, fg_color="transparent")
    frame.grid_columnconfigure(0, weight=1)
    frame.grid_rowconfigure(0, weight=1)

    label = ctk.CTkLabel(master=frame, text=label)
    label.grid(row=1, column=0, padx=10, pady=(5, 0), sticky="w")

    entry = ctk.CTkEntry(master=frame, placeholder_text=placeholder, height=36)
    entry.grid(row=2, column=0, padx=(10, 5), pady=5, sticky="ew")
    entry.bind(sequence="<KeyRelease>", command=lambda _ : handleKeyPress(entry, name))

    searchFunction = getSearchFunction(find)
    search = ctk.CTkButton(master=frame, text="Explore", command=lambda: searchFunction(entry, name), height=36)
    search.grid(row=2, column=1, padx=(0, 10), pady=5, sticky="ew")

    # Get entry state from storage and set it
    state = store.getGameState()
    if bool(state[name]):
        setEntry(entry, state[name])

    return [entry, search, frame]


# Helper Functions
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